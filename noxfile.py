import os
import sys
import shutil
from pathlib import Path
import nox


# Define the common environment variables
def get_common_env():
    """
    Get common environment variables, detecting if we are in a Pixi environment.
    This ensures 'uv' uses the correct environment (Pixi's or standard .venv).
    """
    env = {
        "UV_HTTP_TIMEOUT": "300",
        "UV_CONCURRENT_DOWNLOADS": "16",
        "FORCE_COLOR": "1",
    }

    # If .pixi/envs/default exists and we are not explicitly in a venv, point uv there
    pixi_env = Path(".pixi/envs/default")

    # Also check for standard .venv which might be a symlink to a conda env (setup_environment.sh does this)
    venv_path = Path(".venv")

    if not os.environ.get("VIRTUAL_ENV"):
        if pixi_env.exists():
            # We resolve it to absolute path
            env["UV_PROJECT_ENVIRONMENT"] = str(pixi_env.resolve())
            print(f"👻 Detected Pixi environment. Setting UV_PROJECT_ENVIRONMENT to: {env['UV_PROJECT_ENVIRONMENT']}")
        elif venv_path.exists() and venv_path.is_symlink():
            # If .venv is a symlink, it likely points to a conda env created by our scripts
            resolved = venv_path.resolve()
            env["UV_PROJECT_ENVIRONMENT"] = str(resolved)
            print(
                f"👻 Detected linked environment. Setting UV_PROJECT_ENVIRONMENT to: {env['UV_PROJECT_ENVIRONMENT']}"
            )

    return env


COMMON_ENV = get_common_env()

# Define the supported Python versions
SUPPORTED_PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]
DEFAULT_PYTHON_VERSION = "3.12"
# Define the session names
nox.options.sessions = ["lint", "test", "typing"]


def log_session_info(session, info_dict):
    """Log session information in a structured way."""
    session.log("-" * 60)
    for key, value in info_dict.items():
        session.log(f"{key:<20} : {value}")
    session.log("-" * 60)


def resource_allocated_run(session, *args, **kwargs):
    """
    Run command with strict resource limits if configured via Environment Variables.
    Supports APUs, CPU limiting, and GPU isolation.
    """
    import shutil
    cpu_limit = os.environ.get("CYTO_LIMIT_CPUS")
    mem_limit = os.environ.get("CYTO_LIMIT_MEM")  # Requires `systemd-run` or `prlimit` on Linux
    apu_override = os.environ.get("CYTO_APU_GFX_OVERRIDE")  # e.g., 10.3.0
    gpu_limit = os.environ.get("CYTO_LIMIT_GPUS")

    cmd = list(args)
    env = kwargs.get("env", COMMON_ENV).copy()

    # CPU Masking
    if cpu_limit and shutil.which("taskset"):
        session.log(f"Limiting to {cpu_limit} CPUs via taskset")
        cmd = ["taskset", "-c", f"0-{int(cpu_limit)-1}"] + cmd

    # Memory Limiting (Naive wrapper via prlimit if installed)
    if mem_limit and shutil.which("prlimit"):
        session.log(f"Limiting Memory to {mem_limit} bytes via prlimit")
        cmd = ["prlimit", f"--as={mem_limit}"] + cmd

    # APU/GPU Limits
    if gpu_limit:
        session.log(f"Isolating to {gpu_limit} GPUs")
        env["CUDA_VISIBLE_DEVICES"] = ",".join(str(i) for i in range(int(gpu_limit)))
        env["HIP_VISIBLE_DEVICES"] = env["CUDA_VISIBLE_DEVICES"]

    if apu_override:
        session.log(f"Forcing APU GFX Override to {apu_override}")
        env["HSA_OVERRIDE_GFX_VERSION"] = apu_override
        # Preallocate APU memory for PyTorch if needed
        env["PYTORCH_HIP_ALLOC_CONF"] = "garbage_collection_threshold:0.6,max_split_size_mb:128"

    kwargs["env"] = env
    kwargs["external"] = kwargs.get("external", True)
    session.run(*cmd, **kwargs)


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def init_project(session):
    """Initialize the project environment with uv."""
    log_session_info(session, {"Action": "Project Initialization"})

    # Initialize git if not already
    if not Path(".git").exists():
        session.run("git", "init", external=True)

    # Check if uv is installed
    session.run("uv", "--version", external=True)

    # Install the project in development mode with all dependencies
    # Using --all-extras to install all optional dependencies including dev tools
    session.run("uv", "sync", "--all-extras", external=True, env=COMMON_ENV)

    # Install pre-commit hooks
    if Path(".pre-commit-config.yaml").exists():
        session.run("uv", "run", "pre-commit", "install", external=True, env=COMMON_ENV)

    session.log("✅ Project initialized successfully!")


# ==============================================================================
# Development Sessions
# ==============================================================================


@nox.session(python=DEFAULT_PYTHON_VERSION)
def jupyter_lab(session):
    """Launch Jupyter Lab with proper environment."""
    resource_allocated_run(session, "uv", "run", "--with", "jupyterlab", "jupyter", "lab", *session.posargs)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def marimo_edit(session):
    """Launch Marimo in edit mode."""
    resource_allocated_run(session, "uv", "run", "--with", "marimo", "marimo", "edit", *session.posargs)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def quarto_preview(session):
    """Preview Quarto documentation."""
    # Check if quarto is available
    try:
        session.run("quarto", "--version", external=True, silent=True)
    except Exception:
        session.error("Quarto CLI is not installed. Please install it to use this session.")

    resource_allocated_run(session, "quarto", "preview", "docs", *session.posargs)


# ==============================================================================
# Quality Assurance Sessions
# ==============================================================================


@nox.session(python=DEFAULT_PYTHON_VERSION)
def lint(session):
    """Run linting checks (ruff)."""
    session.run("uv", "run", "ruff", "check", ".", *session.posargs, external=True, env=COMMON_ENV)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def format(session):
    """Run formatting checks/fixes (ruff)."""
    # If standard 'format' session is run, we default to checking.
    # To fix, use 'nox -s format -- --fix' or explicit format_fix session if desired.
    # But ruff format is 'ruff format .' which writes.
    session.run("uv", "run", "ruff", "format", ".", *session.posargs, external=True, env=COMMON_ENV)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def lint_fix(session):
    """Run linting autofix."""
    session.run("uv", "run", "ruff", "check", "--fix", ".", *session.posargs, external=True, env=COMMON_ENV)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def typing(session):
    """Run type checking (mypy, pyright)."""
    session.run("uv", "run", "mypy", ".", external=True, env=COMMON_ENV)
    # session.run("uv", "run", "pyright", ".", external=True, env=COMMON_ENV) # Optional


@nox.session(python=DEFAULT_PYTHON_VERSION)
def security(session):
    """Run security checks (bandit via ruff or separate tool)."""
    # Ruff includes bandit rules (S)
    session.run("uv", "run", "ruff", "check", "--select", "S", ".", external=True, env=COMMON_ENV)


# ==============================================================================
# Testing Sessions
# ==============================================================================


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def test(session):
    """Run tests with pytest using Resource Wrapper."""
    resource_allocated_run(session, "uv", "run", "--with", "pytest-cov", "pytest", *session.posargs)


# ==============================================================================
# Documentation Sessions
# ==============================================================================


@nox.session(python=DEFAULT_PYTHON_VERSION)
def docs_build(session):
    """Build Sphinx documentation."""
    session.run("uv", "run", "sphinx-build", "-M", "html", "docs", "docs/_build", "-W", external=True, env=COMMON_ENV)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def docs_serve(session):
    """Serve documentation locally."""
    build_dir = Path("docs/_build/html")
    if not build_dir.exists():
        session.run("uv", "run", "sphinx-build", "-M", "html", "docs", "docs/_build", external=True, env=COMMON_ENV)

    session.log(f"Serving docs at http://localhost:8000")
    session.run("python", "-m", "http.server", "8000", "-d", str(build_dir), external=True)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def quarto_build(session):
    """Build Quarto documentation."""
    resource_allocated_run(session, "quarto", "render", "docs")

@nox.session(python=DEFAULT_PYTHON_VERSION)
def docs_publish(session):
    """Publish documentation to GitHub Pages (assuming gh-pages branch is setup)."""
    session.log("Building docs before publishing...")
    docs_build(session)
    # Using gh-pages deployment tool (requires `ghp-import` to be installed or similar)
    session.run("uv", "run", "pip", "install", "ghp-import", external=True, env=COMMON_ENV)
    session.run("uv", "run", "ghp-import", "-n", "-p", "-f", "docs/_build/html", external=True, env=COMMON_ENV)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def quarto_publish(session):
    """Publish Quarto documentation natively."""
    resource_allocated_run(session, "quarto", "publish", "gh-pages", "docs")


# ==============================================================================
# Build & Release Sessions
# ==============================================================================


@nox.session(python=DEFAULT_PYTHON_VERSION)
def build_wheel(session):
    """Build python package (sdist and wheel)."""
    session.run("uv", "run", "python", "-m", "build", external=True, env=COMMON_ENV)


@nox.session(python=DEFAULT_PYTHON_VERSION)
def release(session):
    """Publish package to PyPI."""
    # Ensure build is done
    session.notify("build_wheel")
    # Use twine to upload
    session.run("uv", "run", "twine", "upload", "dist/*", external=True, env=COMMON_ENV)


# ==============================================================================
# Docker Sessions
# ==============================================================================


@nox.session(python=False)
def docker_build(session):
    """Build Docker image."""
    image_name = "cyto-assist"
    session.run("docker", "build", "-t", image_name, ".", external=True)


@nox.session(python=False)
def docker_push(session):
    """Push Docker image."""
    image_name = "cyto-assist"
    session.run("docker", "push", image_name, external=True)


# ==============================================================================
# Environment Setup Session
# ==============================================================================


@nox.session(python=False, tags=["setup"])
def setup_env(session: nox.Session) -> None:
    """
    Setup the development environment using Cytoskeleton strategies.
    This creates a reproducible environment with PyTorch and other tools.
    """
    session.run("python", "scripts/setup_env.py", external=True)
