#!/usr/bin/env python3
"""Restore file to original encoding from UTF-8."""

import sys
import json
import hashlib
import argparse
from pathlib import Path


def get_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def restore_encoding(
    file_path: str,
    errors: str = 'strict',
    cleanup: bool = True
) -> dict:
    """Restore file to original encoding.

    Args:
        file_path: Path to the UTF-8 file to restore
        errors: Error handling ('strict', 'replace', 'backslashreplace', 'xmlcharrefreplace')
        cleanup: Remove backup and metadata files after restore

    Returns:
        dict with restoration result
    """
    path = Path(file_path).resolve()

    if not path.exists():
        return {"status": "error", "error": f"File not found: {file_path}"}

    # Load metadata
    meta_dir = path.parent / ".charenc_meta"
    meta_path = meta_dir / f"{path.name}.json"

    if not meta_path.exists():
        return {
            "status": "error",
            "error": "Metadata not found. Cannot restore without metadata."
        }

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return {"status": "error", "error": f"Cannot read metadata: {e}"}

    # Verify metadata format (v2)
    if metadata.get("schema") != "charenc-simple":
        return {
            "status": "error",
            "error": "Unsupported metadata format. Please use charenc v2.0 to convert this file.",
            "found_schema": metadata.get("schema", "unknown (v1 format)")
        }

    # Verify required keys
    required_keys = ["original_encoding", "converted_hash", "converted_at"]
    missing_keys = [k for k in required_keys if k not in metadata]
    if missing_keys:
        return {
            "status": "error",
            "error": f"Invalid metadata: missing required keys: {', '.join(missing_keys)}"
        }

    # Verify file hash
    hash_warning = None
    expected_hash = None
    current_hash = None
    try:
        current_hash = get_file_hash(path)
        expected_hash = metadata['converted_hash']
        if current_hash != expected_hash:
            hash_warning = "File was modified since conversion (hash mismatch)"
    except IOError:
        pass  # If hash calculation fails, continue without verification

    # Get encoding from metadata
    target_encoding = metadata["original_encoding"]

    # Read UTF-8 content (preserve newlines as-is)
    try:
        with open(path, 'r', encoding='utf-8', newline='') as f:
            text = f.read()
    except UnicodeDecodeError as e:
        return {
            "status": "error",
            "error": f"Invalid UTF-8 content: {e}",
            "hint": "The file is not valid UTF-8. It may be corrupted or not converted with convert_to_utf8.py."
        }
    except IOError as e:
        return {"status": "error", "error": f"Cannot read file: {e}"}

    # Convert to original encoding
    try:
        encoded_bytes = text.encode(target_encoding, errors=errors)
    except UnicodeEncodeError as e:
        return {
            "status": "error",
            "error": f"Encode error with {target_encoding}: {e}",
            "hint": "Try --errors replace or --errors backslashreplace"
        }
    except LookupError:
        return {"status": "error", "error": f"Unknown encoding: {target_encoding}"}

    # Write output file
    try:
        with open(path, 'wb') as f:
            f.write(encoded_bytes)
    except IOError as e:
        return {"status": "error", "error": f"Cannot write file: {e}"}

    # Cleanup
    backup_removed = False
    meta_removed = False

    if cleanup and metadata:
        # Remove backup file (restrict to same directory as target file)
        if metadata.get("backup_path"):
            backup_path = Path(metadata["backup_path"]).resolve()
            if backup_path.parent == path.parent and backup_path.exists():
                try:
                    backup_path.unlink()
                    backup_removed = True
                except IOError:
                    pass

        # Remove metadata file
        if meta_path.exists():
            try:
                meta_path.unlink()
                meta_removed = True
            except IOError:
                pass

        # Try to remove empty metadata directory
        if meta_dir.exists():
            try:
                meta_dir.rmdir()
            except OSError:
                pass  # Directory not empty

    result = {
        "status": "success",
        "file": str(path),
        "encoding": target_encoding,
        "backup_removed": backup_removed,
        "metadata_removed": meta_removed
    }
    if hash_warning:
        result["warning"] = hash_warning
        if expected_hash and current_hash:
            result["expected_hash"] = expected_hash
            result["current_hash"] = current_hash
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Restore file to original encoding after editing"
    )
    parser.add_argument("file", help="UTF-8 file to restore")
    parser.add_argument(
        "--errors",
        default="strict",
        choices=["strict", "replace", "backslashreplace", "xmlcharrefreplace"],
        help="Error handling for unconvertible characters (default: strict)"
    )
    parser.add_argument(
        "--keep-backup",
        action="store_true",
        help="Keep backup and metadata files"
    )

    args = parser.parse_args()

    result = restore_encoding(
        args.file,
        errors=args.errors,
        cleanup=not args.keep_backup
    )

    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
