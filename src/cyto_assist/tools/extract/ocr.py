"""OCR pre-processing pipeline for scanned/image-based PDFs.

Detects whether a PDF is text-based or scanned, and applies OCR when needed.
Supports:
  - Tesseract OCR (CPU, system dependency)
  - olmOCR (Allen AI, VLM-based, requires GPU)

Usage:
    from cytognosis_tools.extract.ocr import is_scanned_pdf, ocr_pipeline

    if is_scanned_pdf("scan.pdf"):
        text = ocr_pipeline("scan.pdf", output_dir)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _try_import(module_name: str):
    try:
        return __import__(module_name)
    except ImportError:
        return None


fitz = _try_import("fitz")


# ── Scan Detection ────────────────────────────────────────────────────────


def is_scanned_pdf(
    path: str,
    min_chars_per_page: int = 50,
    sample_pages: int = 5,
) -> bool:
    """Detect if a PDF is scanned (image-based) vs text-based.

    Checks the first few pages for extractable text. If average text length
    per page is below threshold, the PDF is likely scanned.

    Args:
        path: Path to PDF file
        min_chars_per_page: Minimum characters per page to consider text-based
        sample_pages: Number of pages to sample

    Returns:
        True if the PDF appears to be scanned/image-based
    """
    if fitz is None:
        print(
            "⚠ PyMuPDF not available for scan detection, assuming text-based",
            file=sys.stderr,
        )
        return False

    doc = fitz.open(path)
    total_chars = 0
    pages_checked = min(len(doc), sample_pages)

    for i in range(pages_checked):
        page = doc[i]
        text = page.get_text("text")
        total_chars += len(text.strip())

    doc.close()

    if pages_checked == 0:
        return False

    avg_chars = total_chars / pages_checked
    is_scanned = avg_chars < min_chars_per_page

    if is_scanned:
        print(
            f"⚠ PDF appears scanned (avg {avg_chars:.0f} chars/page, "
            f"threshold: {min_chars_per_page})",
            file=sys.stderr,
        )

    return is_scanned


# ── Tesseract OCR ─────────────────────────────────────────────────────────


def is_tesseract_available() -> bool:
    """Check if Tesseract OCR is installed."""
    try:
        result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ocr_pdf_tesseract(
    path: str,
    output_dir: Path,
    lang: str = "eng",
    dpi: int = 300,
) -> str:
    """OCR a scanned PDF using Tesseract via page-by-page image conversion.

    Converts each page to an image, runs Tesseract, and returns concatenated text.

    Args:
        path: Path to scanned PDF
        output_dir: Directory for intermediate files
        lang: Tesseract language code (default: eng)
        dpi: Resolution for image conversion (default: 300)

    Returns:
        Extracted text from all pages
    """
    if fitz is None:
        print("ERROR: PyMuPDF required for PDF-to-image conversion", file=sys.stderr)
        return ""

    if not is_tesseract_available():
        print(
            "ERROR: Tesseract not installed. Install with: sudo apt install tesseract-ocr",
            file=sys.stderr,
        )
        return ""

    print(f"→ Running Tesseract OCR (lang={lang}, dpi={dpi})", file=sys.stderr)

    doc = fitz.open(path)
    all_text = []

    ocr_dir = output_dir / "ocr_pages"
    ocr_dir.mkdir(parents=True, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Render page to image at specified DPI
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img_path = ocr_dir / f"page_{page_num + 1}.png"
        pix.save(str(img_path))

        # Run Tesseract on the image
        try:
            result = subprocess.run(
                [
                    "tesseract",
                    str(img_path),
                    "stdout",
                    "-l",
                    lang,
                    "--psm",
                    "3",  # Fully automatic page segmentation
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                all_text.append(result.stdout)
            else:
                print(
                    f"  ⚠ Tesseract failed on page {page_num + 1}: {result.stderr[:100]}",
                    file=sys.stderr,
                )
        except subprocess.TimeoutExpired:
            print(
                f"  ⚠ Tesseract timed out on page {page_num + 1}",
                file=sys.stderr,
            )

    doc.close()

    full_text = "\n\n--- PAGE BREAK ---\n\n".join(all_text)

    # Save OCR'd text
    text_path = output_dir / "ocr_text.txt"
    text_path.write_text(full_text, encoding="utf-8")

    print(
        f"✓ Tesseract OCR complete: {len(doc)} pages, {len(full_text)} characters",
        file=sys.stderr,
    )

    return full_text


# ── olmOCR (Allen AI VLM) ─────────────────────────────────────────────────


def is_olmocr_available() -> bool:
    """Check if olmOCR is installed."""
    try:
        result = subprocess.run(
            ["python", "-c", "import olmocr"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ocr_pdf_olmocr(
    path: str,
    output_dir: Path,
) -> str:
    """OCR a scanned PDF using Allen AI's olmOCR (VLM-based).

    olmOCR produces high-quality Markdown from complex scientific PDFs,
    handling multi-column layouts, equations, tables, and handwriting.

    Requires: pip install olmocr (and GPU)

    Args:
        path: Path to scanned PDF
        output_dir: Directory for output

    Returns:
        Extracted Markdown text
    """
    if not is_olmocr_available():
        print(
            "⚠ olmOCR not available. Install with: pip install olmocr",
            file=sys.stderr,
        )
        return ""

    print("→ Running olmOCR (VLM-based, may take a while)...", file=sys.stderr)

    ocr_output_dir = output_dir / "olmocr_output"
    ocr_output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "olmocr",
                str(path),
                "--output",
                str(ocr_output_dir),
            ],
            capture_output=True,
            text=True,
            timeout=600,  # 10 min timeout for large documents
        )

        if result.returncode == 0:
            # Read output (olmOCR writes Markdown by default)
            md_files = list(ocr_output_dir.glob("*.md"))
            if md_files:
                text = md_files[0].read_text(encoding="utf-8")
                print(
                    f"✓ olmOCR complete: {len(text)} characters",
                    file=sys.stderr,
                )
                return text

            # Try text output
            txt_files = list(ocr_output_dir.glob("*.txt"))
            if txt_files:
                return txt_files[0].read_text(encoding="utf-8")

        print(
            f"⚠ olmOCR failed: {result.stderr[:200]}",
            file=sys.stderr,
        )
    except subprocess.TimeoutExpired:
        print("⚠ olmOCR timed out (>10 min)", file=sys.stderr)

    return ""


# ── OCR Pipeline ──────────────────────────────────────────────────────────


def ocr_pipeline(
    path: str,
    output_dir: Path,
    prefer_olmocr: bool = True,
) -> str:
    """Full OCR pipeline: detect scanned PDF → OCR → return text.

    Tries olmOCR first (if available and GPU present), falls back to Tesseract.

    Args:
        path: Path to PDF file
        output_dir: Directory for output artifacts
        prefer_olmocr: Try olmOCR before Tesseract (default: True)

    Returns:
        Extracted text (empty string if OCR fails or PDF is text-based)
    """
    if not is_scanned_pdf(path):
        return ""  # Not scanned, no OCR needed

    print("→ Scanned PDF detected, running OCR pipeline...", file=sys.stderr)

    if prefer_olmocr and is_olmocr_available():
        text = ocr_pdf_olmocr(path, output_dir)
        if text:
            return text
        print("⚠ olmOCR failed, trying Tesseract...", file=sys.stderr)

    if is_tesseract_available():
        return ocr_pdf_tesseract(path, output_dir)

    print(
        "ERROR: No OCR engine available. Install Tesseract or olmOCR.",
        file=sys.stderr,
    )
    return ""
