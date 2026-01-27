#!/usr/bin/env python3
"""
Wix Form File Downloader
========================
A generic tool for downloading files from Wix form CSV exports.

Features:
  - Auto-detects URL columns in any CSV
  - Supports wix:document:// and wix:image:// URL formats
  - Configurable via config.json or command-line
  - Dry-run mode to preview downloads
  - Tracks downloaded files to avoid duplicates

FOLDER STRUCTURE:
  Parent Folder/                 ← files saved HERE (one level up)
  ├── *.pdf, *.docx, etc.        ← downloaded files
  └── script_folder/             ← folder containing this script
      ├── download_files.py      ← this script
      ├── config.json            ← your configuration (optional)
      ├── source/                ← put your CSV exports here
      └── .processed.json        ← tracks downloads (auto-created)

USAGE:
  python download_files.py                    # Download files
  python download_files.py --dryrun           # Preview only
  python download_files.py --detect           # Show detected columns
  python download_files.py --site-id XXXX     # Override site ID

For setup instructions, see: docs/SETUP-GUIDE.md
"""

import argparse
import csv
import json
import os
import re
import ssl
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    "site_id": "",                    # Your Wix site ID (required for wix:document URLs)
    "output_folder": "..",            # Save files to parent folder
    "source_folder": "source",        # Folder containing CSV exports
    "name_columns": [],               # Columns to use for filename (e.g., ["First Name", "Last Name"])
    "date_column": "",                # Column name for submission date
    "url_columns": [],                # Specific URL columns (auto-detected if empty)
}

CONFIG_FILE = "config.json"
HISTORY_FILE = ".processed.json"


# =============================================================================
# URL DETECTION AND CONVERSION
# =============================================================================

def is_url_column(values: list) -> bool:
    """Check if a column contains URLs or Wix file references."""
    url_patterns = [
        r'^https?://',
        r'^wix:document://',
        r'^wix:image://',
        r'^wix:video://',
    ]
    
    url_count = 0
    non_empty = 0
    
    for val in values[:50]:  # Sample first 50 rows
        if val and val.strip():
            non_empty += 1
            for pattern in url_patterns:
                if re.match(pattern, val.strip(), re.IGNORECASE):
                    url_count += 1
                    break
    
    # Consider it a URL column if >50% of non-empty values are URLs
    return non_empty > 0 and (url_count / non_empty) > 0.5


def detect_url_columns(csv_path: Path) -> list:
    """Auto-detect columns containing URLs in a CSV file."""
    url_columns = []
    
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            
            if not headers:
                return []
            
            # Collect values for each column
            column_values = {i: [] for i in range(len(headers))}
            for row in reader:
                for i, val in enumerate(row):
                    if i < len(headers):
                        column_values[i].append(val)
            
            # Check each column
            for i, header in enumerate(headers):
                if is_url_column(column_values[i]):
                    url_columns.append(header)
    
    except Exception as e:
        print(f"  ⚠️  Error detecting columns: {e}")
    
    return url_columns


def convert_wix_url(wix_url: str, site_id: str) -> str:
    """Convert wix:document:// or wix:image:// URLs to downloadable URLs."""
    if not wix_url:
        return wix_url
    
    wix_url = wix_url.strip()
    
    # Already a direct URL
    if wix_url.startswith("http://") or wix_url.startswith("https://"):
        return wix_url
    
    # wix:document://v1/{file_id}/{original_name}
    if wix_url.startswith("wix:document://"):
        match = re.search(r'wix:document://v1/([^/]+)/', wix_url)
        if match and site_id:
            file_part = match.group(1)
            return f"https://{site_id}.usrfiles.com/ugd/{file_part}"
    
    # wix:image://v1/{file_id}/{dimensions}/{original_name}
    if wix_url.startswith("wix:image://"):
        match = re.search(r'wix:image://v1/([^/]+)/', wix_url)
        if match and site_id:
            file_part = match.group(1)
            return f"https://static.wixstatic.com/media/{file_part}"
    
    return wix_url


# =============================================================================
# FILE OPERATIONS
# =============================================================================

def load_config(script_dir: Path) -> dict:
    """Load configuration from config.json or return defaults."""
    config_path = script_dir / CONFIG_FILE
    config = DEFAULT_CONFIG.copy()
    
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Error reading config.json: {e}")
    
    return config


def load_history(history_path: Path) -> dict:
    """Load the history of processed URLs."""
    if history_path.exists():
        try:
            with open(history_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"processed_urls": [], "download_log": []}
    return {"processed_urls": [], "download_log": []}


def save_history(history_path: Path, history: dict):
    """Save the history of processed URLs."""
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)


def get_extension(url: str) -> str:
    """Extract file extension from URL."""
    path = urlparse(url).path
    filename = unquote(Path(path).name)
    if "." in filename:
        ext = "." + filename.split(".")[-1].lower()
        if len(ext) <= 10:
            return ext
    return ".pdf"  # Default extension


def clean_string(s: str) -> str:
    """Clean string for use in filename."""
    if not s:
        return ""
    s = re.sub(r"[^\w\s.-]", "", str(s)).strip()
    s = re.sub(r"\s+", " ", s)
    return s.title()


def parse_date(date_str: str) -> str:
    """Parse submission date and return YYYY-MM-DD format."""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return datetime.now().strftime("%Y-%m-%d")


def download_file(url: str, dest: Path, ssl_ctx) -> bool:
    """Download a file from URL to destination."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=60) as resp:
            with open(dest, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


# =============================================================================
# CSV PROCESSING
# =============================================================================

def find_column_index(headers: list, column_names: list) -> int:
    """Find the index of a column by trying multiple possible names."""
    headers_lower = [h.lower().strip() for h in headers]
    for name in column_names:
        if name.lower().strip() in headers_lower:
            return headers_lower.index(name.lower().strip())
    return -1


def process_csv(csv_path: Path, config: dict, processed_urls: set) -> tuple:
    """
    Process a CSV file and extract download records.
    Returns (records, skipped_count, detected_columns)
    """
    records = []
    skipped = 0
    detected_url_cols = []
    
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            
            if not headers:
                return [], 0, []
            
            # Detect or use configured URL columns
            if config["url_columns"]:
                url_col_names = config["url_columns"]
            else:
                url_col_names = detect_url_columns(csv_path)
            
            detected_url_cols = url_col_names
            
            if not url_col_names:
                print(f"  ⚠️  No URL columns detected")
                return [], 0, []
            
            # Find column indices
            url_indices = []
            for col_name in url_col_names:
                idx = find_column_index(headers, [col_name])
                if idx >= 0:
                    url_indices.append((col_name, idx))
            
            # Find name columns
            name_cols = config.get("name_columns", [])
            if not name_cols:
                # Try common name column patterns
                name_cols = ["First Name", "First", "FirstName", "Name"]
            first_idx = find_column_index(headers, name_cols)
            
            last_cols = ["Last Name", "Last", "LastName", "Surname"]
            last_idx = find_column_index(headers, last_cols)
            
            # Find date column
            date_cols = [config.get("date_column", "")] if config.get("date_column") else []
            date_cols.extend(["Submission Time", "Submission Date", "Created Date", "Date", "Updated Date"])
            date_idx = find_column_index(headers, date_cols)
            
            # Process rows
            for row in reader:
                for col_name, url_idx in url_indices:
                    if url_idx >= len(row):
                        continue
                    
                    raw_url = row[url_idx].strip()
                    if not raw_url:
                        continue
                    
                    # Convert Wix URLs
                    url = convert_wix_url(raw_url, config.get("site_id", ""))
                    if not url.startswith("http"):
                        continue
                    
                    # Skip if already processed
                    if url in processed_urls or raw_url in processed_urls:
                        skipped += 1
                        continue
                    
                    # Build record
                    first_name = clean_string(row[first_idx]) if first_idx >= 0 and first_idx < len(row) else ""
                    last_name = clean_string(row[last_idx]) if last_idx >= 0 and last_idx < len(row) else ""
                    date = parse_date(row[date_idx]) if date_idx >= 0 and date_idx < len(row) else parse_date("")
                    
                    records.append({
                        "first": first_name,
                        "last": last_name,
                        "date": date,
                        "url": url,
                        "raw_url": raw_url,
                        "column": col_name,
                    })
    
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return [], 0, []
    
    return records, skipped, detected_url_cols


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Download files from Wix form CSV exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_files.py                    # Download all files
  python download_files.py --dryrun           # Preview without downloading
  python download_files.py --detect           # Show detected URL columns
  python download_files.py --site-id XXXX     # Override site ID from config
        """
    )
    parser.add_argument("--dryrun", action="store_true", 
                        help="Preview only - creates a text file with filenames")
    parser.add_argument("--detect", action="store_true",
                        help="Detect and display URL columns in CSV files")
    parser.add_argument("--site-id", type=str, default="",
                        help="Wix site ID (overrides config.json)")
    args = parser.parse_args()
    
    # Setup paths
    script_dir = Path(__file__).parent
    config = load_config(script_dir)
    
    # Override site_id from command line
    if args.site_id:
        config["site_id"] = args.site_id
    
    source_dir = script_dir / config.get("source_folder", "source")
    output_dir = script_dir / config.get("output_folder", "..")
    history_path = script_dir / HISTORY_FILE
    
    # Header
    print()
    print("=" * 60)
    if args.dryrun:
        print("  Wix Form File Downloader (DRY RUN)")
    elif args.detect:
        print("  Wix Form File Downloader (COLUMN DETECTION)")
    else:
        print("  Wix Form File Downloader")
    print("=" * 60)
    print()
    
    # Check source folder
    if not source_dir.exists():
        source_dir.mkdir(parents=True)
        print(f"📁 Created '{source_dir.name}/' folder.")
        print(f"   Please add your CSV exports there and run again.")
        print()
        return
    
    # Find CSV files
    csv_files = list(source_dir.glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in '{source_dir.name}/' folder.")
        print(f"   Please add your Wix form exports and run again.")
        print()
        return
    
    # Detection mode - just show columns and exit
    if args.detect:
        for csv_file in csv_files:
            print(f"📄 {csv_file.name}")
            url_cols = detect_url_columns(csv_file)
            if url_cols:
                print(f"   Detected URL columns: {', '.join(url_cols)}")
            else:
                print(f"   No URL columns detected")
            print()
        return
    
    # Load history
    history = load_history(history_path)
    processed_urls = set(history.get("processed_urls", []))
    
    if processed_urls:
        print(f"📋 History: {len(processed_urls)} previously downloaded")
    
    if config.get("site_id"):
        print(f"🔑 Site ID: {config['site_id'][:8]}...")
    else:
        print(f"⚠️  No Site ID configured (wix:document URLs won't work)")
    print()
    
    # Create output folder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all CSVs
    all_records = []
    total_skipped = 0
    
    for csv_file in csv_files:
        print(f"📄 Reading: {csv_file.name}")
        records, skipped, detected_cols = process_csv(csv_file, config, processed_urls)
        
        if detected_cols:
            print(f"   URL columns: {', '.join(detected_cols)}")
        print(f"   New: {len(records)} | Already downloaded: {skipped}")
        
        all_records.extend(records)
        total_skipped += skipped
    
    print()
    
    if not all_records:
        if total_skipped > 0:
            print(f"✅ All {total_skipped} files already downloaded. Nothing new to do!")
        else:
            print("❌ No downloadable URLs found in the CSV files.")
        print()
        return
    
    # Build filenames
    name_counter = {}
    filenames = []
    
    for rec in all_records:
        # Build filename
        if rec["first"] or rec["last"]:
            name_part = f"{rec['first']} {rec['last']}".strip()
        else:
            name_part = f"File"
        
        base_name = f"{name_part} - {rec['date']}"
        ext = get_extension(rec["url"])
        
        # Handle duplicates
        key = base_name.lower()
        name_counter.setdefault(key, 0)
        name_counter[key] += 1
        
        if name_counter[key] > 1:
            filename = f"{base_name} ({name_counter[key]}){ext}"
        else:
            filename = f"{base_name}{ext}"
        
        filenames.append((filename, rec))
    
    # DRY RUN MODE
    if args.dryrun:
        dryrun_file = output_dir / "_dryrun_preview.txt"
        print(f"🔍 DRY RUN: Would download {len(all_records)} files...")
        print()
        
        with open(dryrun_file, "w") as f:
            f.write(f"Wix Form File Downloader - DRY RUN PREVIEW\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Would download {len(filenames)} new files:\n\n")
            
            for i, (filename, rec) in enumerate(filenames, 1):
                print(f"  {i:3}. {filename}")
                f.write(f"{i:3}. {filename}\n")
                f.write(f"      URL: {rec['url']}\n")
            
            if total_skipped:
                f.write(f"\n\nWould skip {total_skipped} already-downloaded files.\n")
        
        print()
        print("=" * 60)
        print(f"  📝 Preview saved to: {dryrun_file.name}")
        print(f"  📊 Would download: {len(filenames)} new files")
        if total_skipped:
            print(f"  ⏭️  Would skip: {total_skipped} already downloaded")
        print("=" * 60)
        print()
        return
    
    # NORMAL MODE: Download files
    print(f"📥 Downloading {len(all_records)} files...")
    print()
    
    ssl_ctx = ssl.create_default_context()
    success = 0
    errors = 0
    newly_processed = []
    
    for filename, rec in filenames:
        # Check if file exists
        dest = output_dir / filename
        counter = 2
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        ext = get_extension(rec["url"])
        
        while dest.exists():
            filename = f"{base_name} ({counter}){ext}"
            dest = output_dir / filename
            counter += 1
        
        print(f"  ↓ {filename}")
        
        if download_file(rec["url"], dest, ssl_ctx):
            success += 1
            newly_processed.append(rec["url"])
            if rec["raw_url"] != rec["url"]:
                newly_processed.append(rec["raw_url"])
            
            history.setdefault("download_log", []).append({
                "filename": filename,
                "url": rec["url"],
                "downloaded_at": datetime.now().isoformat(),
            })
        else:
            errors += 1
    
    # Update history
    if newly_processed:
        history["processed_urls"] = list(processed_urls | set(newly_processed))
        history["last_run"] = datetime.now().isoformat()
        save_history(history_path, history)
    
    # Summary
    print()
    print("=" * 60)
    print(f"  ✅ Downloaded: {success}")
    if errors:
        print(f"  ❌ Errors: {errors}")
    if total_skipped:
        print(f"  ⏭️  Skipped (already had): {total_skipped}")
    print(f"  📁 Saved to: {output_dir}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
