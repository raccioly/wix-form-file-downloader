# Wix Form File Downloader

A simple, open-source tool for downloading files from Wix form CSV exports.

**Works with:**
- Old Wix Forms (forms.wix.com)
- New integrated Wix Forms
- Any CSV with downloadable URLs

---

## ⚡ Quick Start

1. **Download the script** - Clone this repo or download `download_files.py`

2. **Create your folder structure:**
   ```
   My Files/                    ← files will be saved here
   └── wix-downloader/          ← put the script here
       ├── download_files.py
       ├── config.json          ← your settings
       └── source/              ← put CSVs here
   ```

3. **Get your Wix Site ID** - See [Finding Your Site ID](docs/FINDING-YOUR-SITE-ID.md)

4. **Create `config.json`:**
   ```json
   {
     "site_id": "your-site-id-here"
   }
   ```

5. **Export CSV from Wix** and save to `source/` folder

6. **Run the script:**
   ```bash
   cd /path/to/wix-downloader
   python3 download_files.py --dryrun  # Preview first
   python3 download_files.py           # Download files
   ```

---

## ✨ Features

### Auto-Detection
The script automatically scans your CSV for columns containing:
- Direct URLs (`https://...`)
- Wix document references (`wix:document://...`)
- Wix image references (`wix:image://...`)

### Smart Naming
Files are named using detected name and date columns:
```
John Smith - 2026-01-15.pdf
Jane Doe - 2026-01-14.docx
```

### Duplicate Prevention
Tracks downloaded files to avoid re-downloading on subsequent runs.

### Dry Run Mode
Preview what would be downloaded without actually downloading:
```bash
python3 download_files.py --dryrun
```

### Column Detection
See what URL columns were detected:
```bash
python3 download_files.py --detect
```

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [Setup Guide](docs/SETUP-GUIDE.md) | Step-by-step setup for beginners |
| [Finding Your Site ID](docs/FINDING-YOUR-SITE-ID.md) | How to find your Wix Site ID |
| [Wix Forms Explained](docs/WIX-FORMS-EXPLAINED.md) | How Wix stores uploaded files |

---

## ⚙️ Configuration

Create a `config.json` file with your settings:

```json
{
  "site_id": "a18c1cea-079d-47d1-a94d-8a0aaf5dcd6f",
  "output_folder": "..",
  "source_folder": "source",
  "name_columns": ["First Name", "Last Name"],
  "date_column": "Submission Time",
  "url_columns": []
}
```

| Setting | Description | Default |
|---------|-------------|---------|
| `site_id` | Your Wix site ID (required for wix:document URLs) | `""` |
| `output_folder` | Where to save files (relative to script) | `".."` (parent folder) |
| `source_folder` | Folder containing CSV exports | `"source"` |
| `name_columns` | Columns to use for filename | Auto-detect |
| `date_column` | Column for submission date | Auto-detect |
| `url_columns` | Specific URL columns to use | Auto-detect |

---

## 🔧 Command Line Options

```
python3 download_files.py [options]

Options:
  --dryrun       Preview only - creates a text file with filenames
  --detect       Show detected URL columns in CSV files
  --site-id ID   Override site ID from config.json
  --help         Show help message
```

---

## 📝 Requirements

- Python 3.6+
- No additional packages required (uses standard library only)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

---

## 💡 Acknowledgments

Originally developed for CCT Atlanta volunteer resume management.
