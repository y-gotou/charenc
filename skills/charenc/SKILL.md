---
name: charenc
description: |
  Character encoding conversion for editing non-UTF-8 files with Claude Code.
  Use when: (1) Editing files with Japanese characters that appear garbled,
  (2) Working with legacy codebases using cp932/Shift-JIS/EUC-JP encoding,
  (3) Converting file encodings before editing and restoring after.
  Workflow: convert to UTF-8 -> edit -> restore original encoding.
---

# Character Encoding Conversion

Claude Code operates in UTF-8. This skill enables editing non-UTF-8 files (cp932, shift-jis, euc-jp, etc.) through a convert-edit-restore workflow.

## Quick Start

### 1. Convert to UTF-8

```bash
python scripts/convert_to_utf8.py <file> -e <encoding>
```

Example:
```bash
python scripts/convert_to_utf8.py config.txt -e cp932
```

This creates:
- Backup file: `config.txt.cp932.bak`
- Metadata: `.charenc_meta/config.txt.json`

### 2. Edit the file

The file is now UTF-8. Edit freely with Claude Code.

### 3. Restore original encoding

```bash
python scripts/restore_encoding.py <file>
```

Example:
```bash
python scripts/restore_encoding.py config.txt
```

This restores cp932 encoding and removes backup/metadata.

## Script Reference

### convert_to_utf8.py

| Option | Description |
|--------|-------------|
| `-e, --encoding` | Source encoding (required) |
| `-o, --output` | Output path (default: overwrite) |
| `--backup-dir` | Backup directory |
| `--no-backup` | Skip backup creation |

### restore_encoding.py

| Option | Description |
|--------|-------------|
| `-e, --encoding` | Target encoding (default: from metadata) |
| `-o, --output` | Output path (default: overwrite) |
| `--errors` | Error handling: strict/replace/backslashreplace |
| `--keep-backup` | Keep backup and metadata |

## Error Handling

If restore fails due to unconvertible characters (e.g., emoji added during editing):

```bash
# Replace with ?
python scripts/restore_encoding.py file.txt --errors replace

# Show as \xNN
python scripts/restore_encoding.py file.txt --errors backslashreplace
```

## Supported Encodings

See [supported_encodings.md](references/supported_encodings.md) for full list.

Common: `cp932`, `shift_jis`, `euc-jp`, `iso-2022-jp`
