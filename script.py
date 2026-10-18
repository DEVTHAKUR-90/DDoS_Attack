#!/usr/bin/env python3
"""
download_gdoc.py — Download a Google Docs / Sheets / Slides / Drive file
from its share URL, with retries and multiple fallback strategies.

USAGE
-----
Interactive:
    python download_gdoc.py

Command-line:
    python download_gdoc.py --url "https://docs.google.com/document/d/XXXX/edit" --format docx -o myfile.docx

    python download_gdoc.py -u "<url>" -f pdf -o out.pdf -v

Requires:
    pip install requests
"""

import argparse
import logging
import re
import sys
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter, Retry

logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("download_gdoc")

# Export formats available per Google file type, in priority order (first = default)
EXPORT_FORMATS = {
    "document": ["docx", "pdf", "odt", "rtf", "txt", "html"],
    "spreadsheets": ["xlsx", "pdf", "ods", "csv", "tsv"],
    "presentation": ["pptx", "pdf", "odp", "txt"],
}

BAD_CONTENT_TYPES = ("text/html",)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def build_session() -> requests.Session:
    """Session with retry/backoff for transient network errors."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retries = Retry(
        total=4,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def extract_file_id(url: str):
    """Pull the file ID out of any common Google Docs/Drive URL shape."""
    patterns = [
        r"/d/([a-zA-Z0-9_-]{15,})",       # /document/d/ID/  or  /file/d/ID/
        r"[?&]id=([a-zA-Z0-9_-]{15,})",   # ?id=ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def detect_doc_type(url: str):
    if "document" in url:
        return "document"
    if "spreadsheets" in url:
        return "spreadsheets"
    if "presentation" in url:
        return "presentation"
    if "drive.google.com" in url:
        return "drive"  # generic Drive file, not a native Docs/Sheets/Slides doc
    return None


def _looks_like_error_page(resp: requests.Response) -> bool:
    ctype = resp.headers.get("Content-Type", "")
    return any(bad in ctype for bad in BAD_CONTENT_TYPES)


def _extract_confirm_token(resp: requests.Response):
    """Large Drive files show a 'can't scan for viruses' interstitial with a confirm token."""
    for key, value in resp.cookies.items():
        if key.startswith("download_warning"):
            return value
    match = re.search(r"confirm=([0-9A-Za-z_]+)", resp.text)
    if match:
        return match.group(1)
    return None


def try_export_download(session, file_id, doc_type, export_ext, timeout=30):
    """Primary method: native Docs/Sheets/Slides export endpoint."""
    url = f"https://docs.google.com/{doc_type}/d/{file_id}/export?format={export_ext}"
    log.debug(f"Trying export URL: {url}")
    resp = session.get(url, timeout=timeout)
    if resp.status_code == 200 and not _looks_like_error_page(resp):
        return resp.content
    return None


def try_drive_uc_download(session, file_id, timeout=30):
    """Fallback: generic Drive 'uc?export=download' endpoint, handles large-file confirm tokens."""
    base = "https://drive.google.com/uc"
    resp = session.get(base, params={"export": "download", "id": file_id}, timeout=timeout, stream=True)

    token = _extract_confirm_token(resp)
    if token:
        resp = session.get(
            base, params={"export": "download", "id": file_id, "confirm": token},
            timeout=timeout, stream=True,
        )

    if resp.status_code == 200 and not _looks_like_error_page(resp):
        return resp.content
    return None


def download_with_fallbacks(session, file_id, doc_type, preferred_ext, out_path, max_attempts=3):
    """
    Try, in order:
      1. Native export in the requested format
      2. Native export in each other available format (if requested one fails)
      3. Generic Drive uc?export=download endpoint
    Retries each network call a few times before moving to the next fallback.
    """
    candidates = []
    if doc_type in EXPORT_FORMATS:
        ext_order = [preferred_ext] + [e for e in EXPORT_FORMATS[doc_type] if e != preferred_ext]
        candidates = [("export", ext) for ext in ext_order]

    last_error = None

    for method, ext in candidates:
        for attempt in range(1, max_attempts + 1):
            try:
                log.info(f"Attempt {attempt}: native export as .{ext} ...")
                content = try_export_download(session, file_id, doc_type, ext)
                if content:
                    final_path = out_path.with_suffix(f".{ext}") if out_path.suffix == "" else out_path
                    final_path.write_bytes(content)
                    log.info(f"✅ Success via native export (.{ext}) -> {final_path}")
                    return final_path
                log.warning(f"Export as .{ext} returned no usable content (attempt {attempt}).")
            except requests.RequestException as e:
                last_error = e
                log.warning(f"Network error on attempt {attempt} ({ext}): {e}")
            time.sleep(1.5 * attempt)

    log.info("Trying generic Drive download fallback ...")
    for attempt in range(1, max_attempts + 1):
        try:
            content = try_drive_uc_download(session, file_id)
            if content:
                final_path = out_path if out_path.suffix else out_path.with_suffix(".bin")
                final_path.write_bytes(content)
                log.info(f"✅ Success via Drive uc?export=download -> {final_path}")
                return final_path
            log.warning(f"Drive uc fallback attempt {attempt} returned no usable content.")
        except requests.RequestException as e:
            last_error = e
            log.warning(f"Network error on Drive fallback attempt {attempt}: {e}")
        time.sleep(1.5 * attempt)

    log.error("❌ All download strategies failed.")
    if last_error:
        log.error(f"Last network error: {last_error}")
    log.error(
        "This usually means: the file is private, the owner disabled downloading/exporting, "
        "or sharing isn't set to 'Anyone with the link can view'."
    )
    return None


def parse_args():
    parser = argparse.ArgumentParser(description="Download a Google Docs/Sheets/Slides/Drive file from its URL.")
    parser.add_argument("-u", "--url", help="Google Docs/Sheets/Slides/Drive share URL")
    parser.add_argument("-f", "--format", help="Export format, e.g. docx, pdf, xlsx, pptx, csv")
    parser.add_argument("-o", "--output", help="Output file path/name")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose/debug logging")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    url = args.url or input("Paste the Google Docs/Sheets/Slides/Drive URL: ").strip()

    doc_type = detect_doc_type(url)
    file_id = extract_file_id(url)

    if not file_id:
        log.error("Could not extract a file ID from that URL. Check the link and try again.")
        sys.exit(1)

    if doc_type is None:
        log.error("Could not determine the file type from the URL.")
        sys.exit(1)

    if doc_type == "drive":
        log.info("This looks like a generic Drive file link (not a native Docs/Sheets/Slides doc).")
        preferred_ext = args.format or "bin"
    else:
        available = EXPORT_FORMATS[doc_type]
        preferred_ext = args.format or available[0]
        if preferred_ext not in available:
            log.warning(f"'{preferred_ext}' not in known formats for {doc_type} ({', '.join(available)}); trying anyway.")

    output_name = args.output or f"output.{preferred_ext}"
    out_path = Path(output_name)

    session = build_session()

    if doc_type == "drive":
        result = None
        for attempt in range(1, 4):
            try:
                content = try_drive_uc_download(session, file_id)
                if content:
                    out_path.write_bytes(content)
                    result = out_path
                    log.info(f"✅ Saved to: {out_path}")
                    break
                log.warning(f"Attempt {attempt} returned no usable content.")
            except requests.RequestException as e:
                log.warning(f"Network error on attempt {attempt}: {e}")
            time.sleep(1.5 * attempt)
        if not result:
            log.error("❌ Download failed. The file may be private or restricted.")
            sys.exit(1)
    else:
        result = download_with_fallbacks(session, file_id, doc_type, preferred_ext, out_path)
        if not result:
            sys.exit(1)


if __name__ == "__main__":
    main()