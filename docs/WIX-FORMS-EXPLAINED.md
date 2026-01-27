# How Wix Forms Store Uploaded Files

This document explains how Wix handles file uploads from forms and how this script converts those references into downloadable URLs.

---

## Types of Wix Forms

### New Integrated Forms (Current)

Forms built directly in the Wix Editor. These are part of your website and submissions appear in your site's dashboard.

- File uploads typically use direct `https://` URLs
- Sometimes use `wix:document://` format
- Found in: Dashboard → Forms & Submissions

### Old Forms (forms.wix.com)

Standalone forms from the older Wix Forms app. Being phased out but still in use on many sites.

- Often use `wix:document://` format in exports
- May require "name and file" view for CSV export
- Some columns may be named differently

---

## URL Formats

When you export form submissions to CSV, file upload fields may contain different URL formats:

### 1. Direct URLs (Easiest)

```
https://static.wixstatic.com/ugd/abc123_file.pdf
```

These work directly - no conversion needed.

### 2. User Files URLs

```
https://a18c1cea-079d-47d1-a94d-8a0aaf5dcd6f.usrfiles.com/ugd/anonym_abc123.pdf
        └──────────── SITE ID ────────────┘          └─── FILE ID ───┘
```

These also work directly. Note that the Site ID is visible in the URL.

### 3. wix:document:// Format

```
wix:document://v1/anonym_abc123def456.pdf/Original-Filename.pdf
              └─┘ └────── FILE ID ──────┘ └─ ORIGINAL NAME ───┘
```

This is an internal Wix reference, **not** a downloadable URL. The script converts these using your Site ID:

**Conversion formula:**
```
wix:document://v1/{file_id}/{name}
       ↓
https://{site_id}.usrfiles.com/ugd/{file_id}
```

### 4. wix:image:// Format

```
wix:image://v1/abc123/1920x1080/photo.jpg
```

Used for image uploads. Converted to:
```
https://static.wixstatic.com/media/{file_id}
```

---

## Why Is This Complicated?

Wix uses internal URL formats (`wix:document://`) in their data exports because:

1. **Storage abstraction** - Files can be moved between servers without breaking references
2. **Access control** - Internal URLs can enforce permissions
3. **Transformation** - Images can be resized, cropped, etc. on-the-fly

When you export to CSV, you get the internal reference, not the public URL. This script handles the conversion automatically.

---

## File Storage Locations

Wix stores uploaded files in different places depending on source:

| Type | Domain | Notes |
|------|--------|-------|
| Form uploads | `{site_id}.usrfiles.com` | Visitor-uploaded files |
| Site media | `static.wixstatic.com` | Images added in Editor |
| Galleries | `static.wixstatic.com/media` | Photo gallery images |

---

## Finding Files in Wix

### Media Manager → Visitor Uploads

All files uploaded through forms appear in:

1. Open Wix Editor
2. Click **Media** (or press M)
3. Click **Visitor Uploads** under MANAGE

Here you can:
- View all uploaded files
- Delete files
- Copy URLs for individual files
- See which files belong to which form

---

## Export Tips

### New Forms
- Export works with default view
- URLs are usually direct downloads

### Old Forms
1. Switch to "name and file" view first
2. Then export to CSV
3. Default view may not include file URLs

### Large Exports
- Wix may split large exports into multiple files
- Put all CSVs in your `source/` folder - the script handles multiple files

---

## Troubleshooting URL Issues

### "URL conversion failed"
- Check that your Site ID is correct
- The `wix:document://` format may have changed

### "File not found" on download
- File may have been deleted from Wix
- Site ID might not match the file's actual site
- Try getting a fresh CSV export

### "Direct download with strange characters"
- URL may need decoding
- The script handles URL encoding automatically
