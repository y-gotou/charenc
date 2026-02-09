#!/usr/bin/env python3
"""Convert file to UTF-8 and save original encoding metadata."""

import sys
import json
import hashlib
import argparse
import shutil
from pathlib import Path
from datetime import datetime


def convert_to_utf8(
    file_path: str,
    encoding: str,
    backup: bool = True
) -> dict:
    """Convert file to UTF-8.

    Args:
        file_path: Path to the file to convert
        encoding: Source encoding (e.g., 'cp932', 'shift_jis', 'euc-jp')
        backup: Create backup file

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
        backup_path = path.parent / f"{path.name}.{encoding}.bak"
        try:
            shutil.copy2(path, backup_path)
        except (IOError, OSError) as e:
            return {"status": "error", "error": f"Backup failed: {e}"}

    # Prepare UTF-8 bytes and calculate hashes in memory (before any file modification)
    utf8_bytes = text.encode('utf-8')
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    converted_hash = hashlib.sha256(utf8_bytes).hexdigest()

    # Create metadata directory
    meta_dir = path.parent / ".charenc_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata first (before writing file to avoid orphaned conversions)
    metadata = {
        "schema": "charenc-simple",
        "original_file": str(path),
        "original_encoding": encoding,
        "original_hash": original_hash,
        "converted_hash": converted_hash,
        "backup_path": str(backup_path) if backup_path else None,
        "converted_at": datetime.now().isoformat()
    }
    meta_path = meta_dir / f"{path.name}.json"
    try:
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except (IOError, OSError) as e:
        return {"status": "error", "error": f"Metadata write failed: {e}"}

    # Write UTF-8 file last (after metadata is saved successfully)
    try:
        with open(path, 'wb') as f:
            f.write(utf8_bytes)
    except IOError as e:
        return {"status": "error", "error": f"Cannot write file: {e}"}

    return {
        "status": "success",
        "file": str(path),
        "original_encoding": encoding,
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
        "--no-backup",
        action="store_true",
        help="Skip backup creation"
    )

    args = parser.parse_args()

    result = convert_to_utf8(
        args.file,
        encoding=args.encoding,
        backup=not args.no_backup
    )

    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
