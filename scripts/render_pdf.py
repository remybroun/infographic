#!/usr/bin/env python3
"""Render an HTML file to PDF with headless Chrome.

Chrome is the renderer because it is the only engine on a normal machine that
handles the whole feature set this skill's CSS relies on: `@page`, grid,
`break-inside`, `print-color-adjust`, `text-wrap: balance`, and modern color.
WeasyPrint and wkhtmltopdf each drop several of those silently, which shows up
as a PDF that is subtly wrong rather than one that fails loudly.

    python3 scripts/render_pdf.py out/doc.html -o out/doc.pdf
"""

from __future__ import annotations

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys

CANDIDATES = {
    "Darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ],
    "Linux": [
        "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium", "/usr/bin/chromium-browser",
        "/snap/bin/chromium", "/usr/bin/microsoft-edge",
    ],
    "Windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
}


def find_chrome(explicit: str = None) -> str:
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        raise SystemExit(f"[pdf] --chrome path not found: {explicit}")
    env = os.environ.get("CHROME_PATH")
    if env and os.path.isfile(env):
        return env
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    for path in CANDIDATES.get(platform.system(), []):
        if os.path.isfile(path):
            return path
        for match in glob.glob(path):
            if os.path.isfile(match):
                return match
    raise SystemExit(
        "[pdf] no Chrome/Chromium found. Install Google Chrome, or set CHROME_PATH, "
        "or pass --chrome /path/to/binary."
    )


def render(html_path: str, pdf_path: str, chrome: str = None, wait_ms: int = 1800,
           scale: float = None, verbose: bool = False, profile: str = None,
           timeout: int = 120) -> str:
    """Render `html_path` to `pdf_path`.

    **Do not add `--user-data-dir` here.** Measured on macOS with Chrome 151:
    passing any `--user-data-dir` (fresh temp *or* reused persistent) while the
    user's own Chrome is running makes headless hang indefinitely, even on a
    trivial one-line document. Without it, the same documents export in 2-3
    seconds. Chrome already isolates the headless profile from the GUI one, so
    the flag bought nothing and cost everything.

    `profile` remains available for environments that genuinely need an explicit
    data dir (containers, CI as root). Expect the hang above if you use it on a
    desktop where Chrome is open.
    """
    html_path = os.path.abspath(html_path)
    if not os.path.isfile(html_path):
        raise SystemExit(f"[pdf] input not found: {html_path}")
    pdf_path = os.path.abspath(pdf_path)
    os.makedirs(os.path.dirname(pdf_path) or ".", exist_ok=True)
    binary = find_chrome(chrome)

    cmd = [
        binary,
        "--headless",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-lcd-text",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--virtual-time-budget={int(wait_ms)}",
        f"--print-to-pdf={pdf_path}",
    ]
    # Chrome refuses to run as root without this; harmless elsewhere in CI.
    if platform.system() == "Linux" and os.geteuid() == 0:
        cmd.insert(1, "--no-sandbox")
    if profile:
        cmd.append(f"--user-data-dir={os.path.abspath(profile)}")
    if scale:
        cmd.append(f"--force-device-scale-factor={scale}")
    cmd.append(f"file://{html_path}")

    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise SystemExit(
            f"[pdf] Chrome did not finish within {timeout}s.\n"
            f"      A document this size normally exports in a few seconds, so this is\n"
            f"      almost always the browser, not the document. Check in this order:\n"
            f"        1. Are you passing --profile / a user-data-dir? On macOS that hangs\n"
            f"           headless whenever the desktop Chrome is running. Drop it.\n"
            f"        2. Quit any stuck headless Chrome processes and retry.\n"
            f"        3. Try a different binary with --chrome or CHROME_PATH."
        )

    if not os.path.isfile(pdf_path):
        sys.stderr.write((result.stdout or "") + "\n" + (result.stderr or "") + "\n")
        raise SystemExit(f"[pdf] Chrome produced no file. Exit code {result.returncode}.")
    if verbose and result.stderr.strip():
        sys.stderr.write(result.stderr)
    return pdf_path


def page_count(pdf_path: str):
    """Best-effort page count. Uses pdfinfo when present, else counts /Type /Page."""
    if shutil.which("pdfinfo"):
        try:
            out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True,
                                 timeout=20).stdout
            for line in out.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split()[-1])
        except Exception:
            pass
    try:
        with open(pdf_path, "rb") as fh:
            blob = fh.read()
        return max(blob.count(b"/Type /Page") - blob.count(b"/Type /Pages"),
                   blob.count(b"/Type/Page") - blob.count(b"/Type/Pages"), 0) or None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Render HTML to PDF with headless Chrome.")
    parser.add_argument("html")
    parser.add_argument("-o", "--out", help="output PDF (defaults to input with .pdf)")
    parser.add_argument("--chrome", help="explicit browser binary")
    parser.add_argument("--wait", type=int, default=1800,
                        help="virtual time budget in ms; raise it when web fonts or "
                             "large images have not settled")
    parser.add_argument("--scale", type=float, help="device scale factor")
    parser.add_argument("--profile", help="explicit --user-data-dir. Only for containers "
                                          "or CI: on a desktop with Chrome open this hangs")
    parser.add_argument("--timeout", type=int, default=120, help="seconds before giving up")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    out = args.out or os.path.splitext(args.html)[0] + ".pdf"
    path = render(args.html, out, args.chrome, args.wait, args.scale, args.verbose,
                  args.profile, args.timeout)
    pages = page_count(path)
    size = os.path.getsize(path)
    print(f"[pdf] wrote {path} ({size:,} bytes"
          + (f", {pages} page{'s' if pages != 1 else ''}" if pages else "") + ")")


if __name__ == "__main__":
    main()
