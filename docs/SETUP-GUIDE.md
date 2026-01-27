# Setup Guide

A complete step-by-step guide for downloading files from Wix form exports.

---

## Prerequisites

- **Python 3.6+** installed on your computer
- Access to your Wix dashboard
- CSV exports from your Wix forms

---

## Step 1: Install Python

### Mac

Python usually comes pre-installed. To check:

1. Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter)
2. Type: `python3 --version`
3. If you see `Python 3.x.x`, you're ready!

**If not installed:** Download from [python.org/downloads](https://www.python.org/downloads/)

### Windows

1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. ⚠️ **IMPORTANT:** Check the box **"Add Python to PATH"**
4. Click **Install Now**
5. Open Command Prompt and verify: `python --version`

---

## Step 2: Create Your Folder Structure

Create folders like this:

```
My Downloads/                    ← files will be saved here
└── wix-downloader/              ← script folder
    ├── download_files.py        ← the script
    ├── config.json              ← your settings
    └── source/                  ← put CSVs here
```

---

## Step 3: Get Your Site ID

1. Log into [Wix.com](https://www.wix.com)
2. Open your website's dashboard
3. Copy the ID from the URL:

```
https://manage.wix.com/dashboard/c9b5b61e-3209-4638-9002-f1b14692676f/home
                                 └──────────── COPY THIS ────────────┘
```

See [Finding Your Site ID](FINDING-YOUR-SITE-ID.md) for more details.

---

## Step 4: Create config.json

Create a file called `config.json` in your script folder:

```json
{
  "site_id": "YOUR-SITE-ID-HERE"
}
```

Replace `YOUR-SITE-ID-HERE` with the ID you copied.

---

## Step 5: Export Your CSV from Wix

### For New Integrated Forms:

1. Go to **Forms & Submissions** in your Wix dashboard
2. Select your form
3. Click **Export** → **CSV**
4. Save to your `source/` folder

### For Old Forms (forms.wix.com):

1. Go to **Forms & Submissions**
2. Select your form
3. **Important:** Switch to the "name and file" view first
4. Click **Export** → **CSV**
5. Save to your `source/` folder

> **Why "name and file" view?** The default view may not include file upload URLs.

---

## Step 6: Run the Script

### Preview First (Recommended)

```bash
cd /path/to/wix-downloader
python3 download_files.py --dryrun
```

This creates a preview file showing what would be downloaded.

### Download Files

```bash
python3 download_files.py
```

**Tip:** On Mac, type `cd ` (with a space) then drag the folder from Finder into Terminal.

---

## Step 7: Find Your Files

Downloaded files appear in the **parent folder** (one level up from the script):

```
My Downloads/                    ← files are here!
├── John Smith - 2026-01-15.pdf
├── Jane Doe - 2026-01-14.docx
└── wix-downloader/              ← script stays here
```

---

## Common Issues

### "No Site ID configured"
Create `config.json` with your Site ID (see Step 4)

### "No URL columns detected"
Your CSV may not contain file upload columns, or they may be in an unexpected format

### "wix:document URLs won't work"
You need to configure your Site ID for these URLs to be converted

### "Permission denied" on Mac
Try: `chmod +x download_files.py`

---

## Next Steps

- See all options: `python3 download_files.py --help`
- Detect columns: `python3 download_files.py --detect`
- Learn about Wix URLs: [Wix Forms Explained](WIX-FORMS-EXPLAINED.md)
