#!/usr/bin/env python3
"""Cytognosis Download Manager — Robust, resumable, parallel download tool.

Built on top of aria2c for maximum throughput with:
- Parallel segmented downloads (multi-connection)
- Full resume/continue capability (state-aware)
- HTTP/HTTPS/FTP support with optional authentication
- Progress monitoring and status checking
- JSON state file for crash recovery
- Support for batch downloads and website mirroring
- GCP/AWS bucket downloads via rclone integration

Usage:
    # Single file download
    python download_manager.py download URL [--output PATH] [--connections N]

    # Check progress of running/completed downloads
    python download_manager.py status [JOB_ID]

    # Resume a failed/interrupted download
    python download_manager.py resume JOB_ID

    # List all downloads
    python download_manager.py list

    # Download from cloud bucket
    python download_manager.py cloud REMOTE:PATH LOCAL_PATH

    # Mirror a website
    python download_manager.py mirror URL [--output DIR]

    # Start aria2 RPC daemon (for GUI)
    python download_manager.py daemon [--port 6800]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import urllib.parse
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

# ── Constants ────────────────────────────────────────────────────────────────

STATE_DIR = Path.home() / ".local" / "share" / "cytognosis" / "downloads"
STATE_FILE = STATE_DIR / "download_state.json"
ARIA2C = shutil.which("aria2c") or "aria2c"
RCLONE = shutil.which("rclone") or "rclone"
WGET = shutil.which("wget") or "wget"

# Default aria2c settings for maximum throughput
DEFAULT_CONNECTIONS = 16  # connections per server
DEFAULT_SPLIT = 16  # number of file segments
DEFAULT_MIN_SPLIT_SIZE = "20M"
DEFAULT_MAX_TRIES = 0  # infinite retries
DEFAULT_RETRY_WAIT = 10  # seconds between retries
DEFAULT_TIMEOUT = 60  # connection timeout
DEFAULT_MAX_CONCURRENT = 5  # max concurrent downloads


class DownloadStatus(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFYING = "verifying"


@dataclass
class DownloadJob:
    """Persistent state for a single download job."""

    job_id: str
    url: str
    output_path: str
    status: str = DownloadStatus.QUEUED.value
    pid: int | None = None
    connections: int = DEFAULT_CONNECTIONS
    split: int = DEFAULT_SPLIT
    total_size: int | None = None
    downloaded_size: int = 0
    progress_percent: float = 0.0
    speed_bps: int = 0
    eta_seconds: int | None = None
    created_at: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None
    checksum: str | None = None
    checksum_type: str | None = None
    auth_user: str | None = None
    auth_pass: str | None = None
    extra_args: list[str] = field(default_factory=list)
    log_file: str | None = None

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        if not self.log_file:
            self.log_file = str(STATE_DIR / "logs" / f"{self.job_id}.log")


class DownloadState:
    """Manages persistent download state across sessions."""

    def __init__(self) -> None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        (STATE_DIR / "logs").mkdir(exist_ok=True)
        self.jobs: dict[str, DownloadJob] = {}
        self._load()

    def _load(self) -> None:
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text())
                for job_id, job_data in data.get("jobs", {}).items():
                    self.jobs[job_id] = DownloadJob(**job_data)
            except (json.JSONDecodeError, TypeError):
                pass

    def save(self) -> None:
        data = {"jobs": {jid: asdict(j) for jid, j in self.jobs.items()}}
        STATE_FILE.write_text(json.dumps(data, indent=2, default=str))

    def add_job(self, job: DownloadJob) -> None:
        self.jobs[job.job_id] = job
        self.save()

    def update_job(self, job_id: str, **kwargs: Any) -> None:
        if job_id in self.jobs:
            for k, v in kwargs.items():
                setattr(self.jobs[job_id], k, v)
            self.save()

    def get_job(self, job_id: str) -> DownloadJob | None:
        return self.jobs.get(job_id)

    def generate_job_id(self, url: str) -> str:
        """Generate a short, deterministic job ID from URL."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
        parsed = urllib.parse.urlparse(url)
        filename = Path(parsed.path).stem[:20] or "download"
        return f"{filename}_{url_hash}"


def _build_aria2_cmd(job: DownloadJob) -> list[str]:
    """Build aria2c command with optimal settings."""
    output_path = Path(job.output_path)
    cmd = [
        ARIA2C,
        "--continue=true",  # Resume support
        f"--max-connection-per-server={job.connections}",
        f"--split={job.split}",
        f"--min-split-size={DEFAULT_MIN_SPLIT_SIZE}",
        f"--max-tries={DEFAULT_MAX_TRIES}",
        f"--retry-wait={DEFAULT_RETRY_WAIT}",
        f"--timeout={DEFAULT_TIMEOUT}",
        f"--connect-timeout={DEFAULT_TIMEOUT}",
        "--auto-file-renaming=false",
        "--allow-overwrite=true",
        "--file-allocation=falloc",  # Fast preallocation on ext4/xfs
        "--summary-interval=30",  # Print summary every 30s
        "--console-log-level=notice",
        f"--log={job.log_file}",
        "--log-level=info",
        f"--dir={output_path.parent}",
        f"--out={output_path.name}",
    ]

    # Authentication
    if job.auth_user:
        cmd.append(f"--http-user={job.auth_user}")
    if job.auth_pass:
        cmd.append(f"--http-passwd={job.auth_pass}")

    # FTP-specific
    parsed = urllib.parse.urlparse(job.url)
    if parsed.scheme in ("ftp", "ftps"):
        cmd.append("--ftp-pasv=true")
        if job.auth_user:
            cmd.append(f"--ftp-user={job.auth_user}")
        if job.auth_pass:
            cmd.append(f"--ftp-passwd={job.auth_pass}")

    # Checksum verification
    if job.checksum and job.checksum_type:
        cmd.append(f"--checksum={job.checksum_type}={job.checksum}")

    # Extra args
    cmd.extend(job.extra_args)

    # URL last
    cmd.append(job.url)
    return cmd


def _get_remote_size(url: str) -> int | None:
    """Get file size via HEAD request."""
    try:
        import urllib.request

        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as resp:
            cl = resp.headers.get("Content-Length")
            return int(cl) if cl else None
    except Exception:
        return None


def _get_download_progress(job: DownloadJob) -> dict[str, Any]:
    """Get current download progress from aria2c log and control file.

    Note: With file-allocation=falloc, file size on disk equals total size
    immediately after pre-allocation. We must parse the aria2 log for actual
    download progress instead.
    """
    output_path = Path(job.output_path)
    aria2_ctrl = output_path.with_suffix(output_path.suffix + ".aria2")
    result: dict[str, Any] = {
        "status": job.status,
        "progress_percent": 0.0,
        "downloaded_size": 0,
        "total_size": job.total_size,
        "speed_bps": 0,
        "speed_human": "",
        "eta_human": "",
        "pid_alive": False,
    }

    # Check if pid is alive
    if job.pid:
        try:
            os.kill(job.pid, 0)
            result["pid_alive"] = True
        except OSError:
            result["pid_alive"] = False

    # Parse aria2 log for actual progress (more reliable than file size)
    log_path = Path(job.log_file) if job.log_file else None
    log_parsed = False
    if log_path and log_path.exists():
        try:
            with open(log_path, "rb") as f:
                # Read last 64KB for recent progress (logs can be verbose)
                f.seek(0, 2)
                end = f.tell()
                f.seek(max(0, end - 65536))
                tail = f.read().decode("utf-8", errors="ignore")
                lines = tail.strip().split("\n")
                for line in reversed(lines):
                    # Match aria2c progress: [#id SIZE/TOTAL(PCT%) CN:N DL:SPEED ETA:TIME]
                    if "%" in line and ("DL:" in line or "ETA:" in line):
                        result["last_log_line"] = line.strip()[-150:]
                        # Extract percentage
                        import re
                        pct_match = re.search(r"(\d+(?:\.\d+)?)%", line)
                        if pct_match:
                            result["progress_percent"] = float(pct_match.group(1))
                        # Extract downloaded/total sizes
                        size_match = re.search(
                            r"\s([\d.]+(?:GiB|MiB|KiB|B))/([\d.]+(?:GiB|MiB|KiB|B))",
                            line,
                        )
                        if size_match:
                            result["downloaded_human"] = size_match.group(1)
                            result["total_human"] = size_match.group(2)
                        # Extract speed
                        speed_match = re.search(r"DL:([\d.]+(?:GiB|MiB|KiB|B))", line)
                        if speed_match:
                            result["speed_human"] = speed_match.group(1) + "/s"
                        # Extract ETA
                        eta_match = re.search(r"ETA:([\dhms]+)", line)
                        if eta_match:
                            result["eta_human"] = eta_match.group(1)
                        log_parsed = True
                        break
                    elif "Download complete:" in line:
                        result["progress_percent"] = 100.0
                        result["status"] = DownloadStatus.COMPLETED.value
                        log_parsed = True
                        break
        except Exception:
            pass

    # Fallback: check file size if log parsing didn't work
    if not log_parsed and output_path.exists():
        file_size = output_path.stat().st_size
        result["downloaded_size"] = file_size
        # Only use file size for progress if no pre-allocation (no .aria2 file)
        if not aria2_ctrl.exists() and job.total_size:
            result["progress_percent"] = round(
                (file_size / job.total_size) * 100, 2
            )

    # Determine completion: no control file + process dead = done
    if output_path.exists() and not aria2_ctrl.exists():
        if not result["pid_alive"]:
            result["status"] = DownloadStatus.COMPLETED.value
            result["progress_percent"] = 100.0

    return result


def _format_size(size_bytes: int | None) -> str:
    """Format bytes to human-readable size."""
    if size_bytes is None:
        return "unknown"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024  # type: ignore[assignment]
    return f"{size_bytes:.1f} PB"


def _format_duration(seconds: int | None) -> str:
    """Format seconds to human-readable duration."""
    if seconds is None:
        return "unknown"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


# ── CLI Commands ─────────────────────────────────────────────────────────────


def cmd_download(args: argparse.Namespace) -> int:
    """Start a new download."""
    state = DownloadState()
    url = args.url

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        parsed = urllib.parse.urlparse(url)
        filename = Path(parsed.path).name or "download"
        output_path = os.path.abspath(filename)

    # Generate job ID
    job_id = state.generate_job_id(url)

    # Check if job already exists and is running
    existing = state.get_job(job_id)
    if existing and existing.status == DownloadStatus.DOWNLOADING.value:
        progress = _get_download_progress(existing)
        if progress["pid_alive"]:
            print(f"⚠️  Download already running: {job_id}")
            print(f"   Progress: {progress['progress_percent']:.1f}%")
            return 0

    # Get remote file size
    total_size = _get_remote_size(url)

    # Create job
    job = DownloadJob(
        job_id=job_id,
        url=url,
        output_path=output_path,
        connections=args.connections,
        split=args.split,
        total_size=total_size,
        auth_user=args.user,
        auth_pass=args.password,
        extra_args=args.extra_args if args.extra_args else [],
    )

    # Build command
    cmd = _build_aria2_cmd(job)

    print(f"📥 Starting download: {url}")
    print(f"   Output: {output_path}")
    print(f"   Size: {_format_size(total_size)}")
    print(f"   Connections: {job.connections}")
    print(f"   Job ID: {job_id}")

    if args.background:
        # Run in background
        log_f = open(job.log_file, "a")
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,  # Detach from terminal
        )
        job.pid = proc.pid
        job.status = DownloadStatus.DOWNLOADING.value
        job.started_at = datetime.now(UTC).isoformat()
        state.add_job(job)
        print(f"   PID: {proc.pid}")
        print(f"   Log: {job.log_file}")
        print("\n✅ Download running in background. Check with:")
        print(f"   python {__file__} status {job_id}")
    else:
        # Run in foreground
        job.status = DownloadStatus.DOWNLOADING.value
        job.started_at = datetime.now(UTC).isoformat()
        state.add_job(job)

        result = subprocess.run(cmd)
        if result.returncode == 0:
            job.status = DownloadStatus.COMPLETED.value
            job.completed_at = datetime.now(UTC).isoformat()
            print(f"\n✅ Download completed: {output_path}")
        else:
            job.status = DownloadStatus.FAILED.value
            job.error_message = f"aria2c exited with code {result.returncode}"
            print(f"\n❌ Download failed (exit code {result.returncode})")
            print(f"   Resume with: python {__file__} resume {job_id}")
        state.save()

    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Check status of a download."""
    state = DownloadState()

    if args.job_id:
        job = state.get_job(args.job_id)
        if not job:
            print(f"❌ Job not found: {args.job_id}")
            return 1
        progress = _get_download_progress(job)
        _print_job_detail(job, progress)

        # Update state if status changed
        if progress["status"] != job.status:
            state.update_job(
                job.job_id,
                status=progress["status"],
                downloaded_size=progress["downloaded_size"],
                progress_percent=progress["progress_percent"],
            )
            if progress["status"] == DownloadStatus.COMPLETED.value:
                state.update_job(
                    job.job_id,
                    completed_at=datetime.now(UTC).isoformat(),
                )
    else:
        # Show all jobs
        if not state.jobs:
            print("No downloads found.")
            return 0
        for jid, job in state.jobs.items():
            progress = _get_download_progress(job)
            _print_job_summary(job, progress)

    return 0


def _print_job_detail(job: DownloadJob, progress: dict) -> None:
    """Print detailed job status."""
    status_icon = {
        "queued": "⏳",
        "downloading": "📥",
        "paused": "⏸️",
        "completed": "✅",
        "failed": "❌",
        "verifying": "🔍",
    }.get(progress["status"], "❓")

    print(f"\n{status_icon} Job: {job.job_id}")
    print(f"   URL: {job.url}")
    print(f"   Output: {job.output_path}")
    print(f"   Status: {progress['status']}")

    # Show size info from log if available
    dl_str = progress.get("downloaded_human", _format_size(progress.get("downloaded_size", 0)))
    total_str = progress.get("total_human", _format_size(progress.get("total_size")))
    print(f"   Progress: {progress['progress_percent']:.1f}% ({dl_str} / {total_str})")

    if progress.get("speed_human"):
        print(f"   Speed: {progress['speed_human']}")
    if progress.get("eta_human"):
        print(f"   ETA: {progress['eta_human']}")
    if job.pid:
        alive = "running" if progress["pid_alive"] else "stopped"
        print(f"   PID: {job.pid} ({alive})")
    if job.started_at:
        print(f"   Started: {job.started_at}")
    if job.completed_at:
        print(f"   Completed: {job.completed_at}")
    if job.error_message:
        print(f"   Error: {job.error_message}")
    if "last_log_line" in progress:
        print(f"   Last log: {progress['last_log_line']}")
    if job.log_file:
        print(f"   Log: {job.log_file}")


def _print_job_summary(job: DownloadJob, progress: dict) -> None:
    """Print one-line job summary."""
    status_icon = {
        "queued": "⏳",
        "downloading": "📥",
        "paused": "⏸️",
        "completed": "✅",
        "failed": "❌",
    }.get(progress["status"], "❓")
    name = Path(job.output_path).name[:30]
    pct = progress["progress_percent"]
    size = _format_size(progress.get("downloaded_size", 0))
    total = _format_size(progress.get("total_size"))
    pid_status = ""
    if job.pid and progress.get("pid_alive"):
        pid_status = f" [PID {job.pid}]"
    print(
        f"  {status_icon} {job.job_id:<30} {pct:>6.1f}%"
        f"  {size:>10}/{total:<10}{pid_status}  {name}"
    )


def cmd_resume(args: argparse.Namespace) -> int:
    """Resume a failed/interrupted download."""
    state = DownloadState()
    job = state.get_job(args.job_id)
    if not job:
        print(f"❌ Job not found: {args.job_id}")
        return 1

    if job.status == DownloadStatus.COMPLETED.value:
        print(f"✅ Job already completed: {args.job_id}")
        return 0

    # Check if already running
    if job.pid:
        try:
            os.kill(job.pid, 0)
            print(f"⚠️  Job already running (PID {job.pid})")
            return 0
        except OSError:
            pass

    print(f"🔄 Resuming download: {job.job_id}")
    cmd = _build_aria2_cmd(job)

    if args.background:
        log_f = open(job.log_file, "a")
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
        state.update_job(
            job.job_id,
            pid=proc.pid,
            status=DownloadStatus.DOWNLOADING.value,
            started_at=datetime.now(UTC).isoformat(),
        )
        print(f"   PID: {proc.pid}")
        print("✅ Resumed in background")
    else:
        state.update_job(
            job.job_id,
            status=DownloadStatus.DOWNLOADING.value,
        )
        result = subprocess.run(cmd)
        if result.returncode == 0:
            state.update_job(
                job.job_id,
                status=DownloadStatus.COMPLETED.value,
                completed_at=datetime.now(UTC).isoformat(),
            )
            print("✅ Download completed")
        else:
            state.update_job(
                job.job_id,
                status=DownloadStatus.FAILED.value,
                error_message=f"exit code {result.returncode}",
            )
            print("❌ Download failed")

    return 0


def cmd_cancel(args: argparse.Namespace) -> int:
    """Cancel a running download."""
    state = DownloadState()
    job = state.get_job(args.job_id)
    if not job:
        print(f"❌ Job not found: {args.job_id}")
        return 1

    if job.pid:
        try:
            os.killpg(os.getpgid(job.pid), signal.SIGTERM)
            print(f"🛑 Sent SIGTERM to PID {job.pid}")
        except OSError as e:
            print(f"   Process already stopped: {e}")

    state.update_job(job.job_id, status=DownloadStatus.PAUSED.value)
    print(f"   Resume with: python {__file__} resume {job.job_id}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List all downloads."""
    state = DownloadState()
    if not state.jobs:
        print("No downloads found.")
        return 0

    print(f"\n{'':2}{'ID':<30} {'Progress':>8}  {'Downloaded':>10}/{'Total':<10}"
          f"{'':1} {'File'}")
    print("  " + "─" * 80)
    for jid, job in state.jobs.items():
        progress = _get_download_progress(job)
        _print_job_summary(job, progress)
    print()
    return 0


def cmd_cloud(args: argparse.Namespace) -> int:
    """Download from cloud bucket using rclone."""
    cmd = [
        RCLONE,
        "copy",
        "--progress",
        "--transfers=8",
        "--checkers=16",
        "--multi-thread-streams=8",
        args.remote_path,
        args.local_path,
    ]
    print(f"☁️  Downloading from {args.remote_path} → {args.local_path}")
    return subprocess.call(cmd)


def cmd_mirror(args: argparse.Namespace) -> int:
    """Mirror a website using wget."""
    output_dir = args.output or "."
    cmd = [
        WGET,
        "--mirror",
        "--convert-links",
        "--adjust-extension",
        "--page-requisites",
        "--no-parent",
        "--continue",
        "-P",
        output_dir,
        args.url,
    ]
    print(f"🌐 Mirroring {args.url} → {output_dir}")
    return subprocess.call(cmd)


def cmd_daemon(args: argparse.Namespace) -> int:
    """Start aria2 RPC daemon for GUI integration."""
    port = args.port
    cmd = [
        ARIA2C,
        "--enable-rpc",
        f"--rpc-listen-port={port}",
        "--rpc-listen-all=true",
        "--rpc-allow-origin-all=true",
        f"--max-concurrent-downloads={DEFAULT_MAX_CONCURRENT}",
        f"--max-connection-per-server={DEFAULT_CONNECTIONS}",
        f"--split={DEFAULT_SPLIT}",
        "--continue=true",
        "--daemon=true",
        f"--log={STATE_DIR / 'logs' / 'aria2-rpc.log'}",
    ]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"✅ aria2 RPC daemon started on port {port}")
        print("   GUI: Open AriaNg (https://ariang.mayswind.net/) or")
        print("         install Chrome extension 'AriaNg Native'")
        print(f"   RPC: http://localhost:{port}/jsonrpc")
    else:
        print(f"❌ Failed to start daemon (exit code {result.returncode})")
    return result.returncode


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cytognosis Download Manager — robust parallel downloads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subs = parser.add_subparsers(dest="command", required=True)

    # download
    dl = subs.add_parser("download", aliases=["dl"], help="Start a download")
    dl.add_argument("url", help="URL to download")
    dl.add_argument("-o", "--output", help="Output file path")
    dl.add_argument(
        "-c", "--connections", type=int, default=DEFAULT_CONNECTIONS,
        help=f"Connections per server (default: {DEFAULT_CONNECTIONS})",
    )
    dl.add_argument(
        "-s", "--split", type=int, default=DEFAULT_SPLIT,
        help=f"File segments (default: {DEFAULT_SPLIT})",
    )
    dl.add_argument("-u", "--user", help="HTTP/FTP username")
    dl.add_argument("-p", "--password", help="HTTP/FTP password")
    dl.add_argument(
        "-b", "--background", action="store_true",
        help="Run in background",
    )
    dl.add_argument("--extra-args", nargs="*", help="Extra aria2c arguments")
    dl.set_defaults(func=cmd_download)

    # status
    st = subs.add_parser("status", help="Check download status")
    st.add_argument("job_id", nargs="?", help="Job ID (omit for all)")
    st.set_defaults(func=cmd_status)

    # resume
    rs = subs.add_parser("resume", help="Resume a download")
    rs.add_argument("job_id", help="Job ID to resume")
    rs.add_argument(
        "-b", "--background", action="store_true",
        help="Resume in background",
    )
    rs.set_defaults(func=cmd_resume)

    # cancel
    cn = subs.add_parser("cancel", help="Cancel a download")
    cn.add_argument("job_id", help="Job ID to cancel")
    cn.set_defaults(func=cmd_cancel)

    # list
    ls = subs.add_parser("list", aliases=["ls"], help="List all downloads")
    ls.set_defaults(func=cmd_list)

    # cloud
    cl = subs.add_parser("cloud", help="Download from cloud bucket via rclone")
    cl.add_argument("remote_path", help="Remote path (e.g. gcs:bucket/path)")
    cl.add_argument("local_path", help="Local destination path")
    cl.set_defaults(func=cmd_cloud)

    # mirror
    mr = subs.add_parser("mirror", help="Mirror a website with wget")
    mr.add_argument("url", help="Website URL to mirror")
    mr.add_argument("-o", "--output", help="Output directory")
    mr.set_defaults(func=cmd_mirror)

    # daemon
    dm = subs.add_parser("daemon", help="Start aria2 RPC daemon for GUI")
    dm.add_argument(
        "--port", type=int, default=6800, help="RPC port (default: 6800)",
    )
    dm.set_defaults(func=cmd_daemon)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
