#!/usr/bin/env python3
"""Convert file to UTF-8 and save original encoding metadata."""

import sys
import json
import hashlib
import argparse
import shutil
from pathlib import Path
from datetime import datetime


def get_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def detect_line_ending(content: bytes) -> str:
    """Detect line ending style."""
    if b'\r\n' in content:
        return "CRLF"
    elif b'\r' in content:
        return "CR"
    elif b'\n' in content:
        return "LF"
    return "NONE"


def convert_to_utf8(
    file_path: str,
    encoding: str,
    output: str = None,
    backup: bool = True,
    backup_dir: str = None
) -> dict:
    """Convert file to UTF-8.

    Args:
        file_path: Path to the file to convert
        encoding: Source encoding (e.g., 'cp932', 'shift_jis', 'euc-jp')
        output: Output file path (default: overwrite original)
        backup: Create backup file
        backup_dir: Directory for backup files

    Returns:
        dict with conversion result
    """
    path = Path(file_path).resolve()

    if not path.exists():
        return {"status": "error", "error": f"File not found: {file_path}"}

    # Read original content
    try:
        with open(path, 'rb') as f:
            original_bytes = f.read()
    except IOError as e:
        return {"status": "error", "error": f"Cannot read file: {e}"}

    # Detect line ending
    line_ending = detect_line_ending(original_bytes)

    # Decode with specified encoding
    try:
        text = original_bytes.decode(encoding)
    except UnicodeDecodeError as e:
        return {
            "status": "error",
            "error": f"Decode error with {encoding}: {e}"
        }
    except LookupError:
        return {"status": "error", "error": f"Unknown encoding: {encoding}"}

    # Create backup
    backup_path = None
    if backup:
        if backup_dir:
            bdir = Path(backup_dir)
        else:
            bdir = path.parent
        bdir.mkdir(parents=True, exist_ok=True)
        backup_path = bdir / f"{path.name}.{encoding}.bak"
        try:
            shutil.copy2(path, backup_path)
        except (IOError, OSError) as e:
            return {"status": "error", "error": f"Backup failed: {e}"}

    # Determine output path
    output_path = Path(output).resolve() if output else path

    # Create metadata directory
    meta_dir = path.parent / ".charenc_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata
    metadata = {
        "original_file": str(path),
        "output_file": str(output_path),
        "original_encoding": encoding,
        "original_size": len(original_bytes),
        "original_hash": get_file_hash(path),
        "backup_path": str(backup_path) if backup_path else None,
        "line_ending": line_ending,
        "converted_at": datetime.now().isoformat()
    }
    meta_path = meta_dir / f"{path.name}.json"
    try:
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except (IOError, OSError) as e:
        return {"status": "error", "error": f"Metadata write failed: {e}"}

    # If output is in a different directory, also save metadata there
    if output_path.parent != path.parent:
        output_meta_dir = output_path.parent / ".charenc_meta"
        output_meta_dir.mkdir(parents=True, exist_ok=True)
        output_meta_path = output_meta_dir / f"{output_path.name}.json"
        try:
            with open(output_meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except (IOError, OSError) as e:
            # Non-fatal: metadata already saved in original location
            pass

    # Normalize line endings to LF for UTF-8
    text_normalized = text.replace('\r\n', '\n').replace('\r', '\n')

    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text_normalized)

    return {
        "status": "success",
        "file": str(output_path),
        "original_encoding": encoding,
        "line_ending": line_ending,
        "backup": str(backup_path) if backup_path else None,
        "metadata": str(meta_path)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert file to UTF-8 for editing with Claude Code"
    )
    parser.add_argument("file", help="File to convert")
    parser.add_argument(
        "--encoding", "-e",
        required=True,
        help="Source encoding (e.g., cp932, shift_jis, euc-jp)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: overwrite original)"
    )
    parser.add_argument(
        "--backup-dir",
        help="Directory for backup files (default: same as source)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation"
    )

    args = parser.parse_args()

    result = convert_to_utf8(
        args.file,
        encoding=args.encoding,
        output=args.output,
        backup=not args.no_backup,
        backup_dir=args.backup_dir
    )

    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
