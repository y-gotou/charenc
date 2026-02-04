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
    encoding: str = None,
    output: str = None,
    errors: str = 'strict',
    cleanup: bool = True,
    force: bool = False,
    strict_hash: bool = False
) -> dict:
    """Restore file to original encoding.

    Args:
        file_path: Path to the UTF-8 file to restore
        encoding: Target encoding (default: from metadata)
        output: Output file path (default: overwrite original)
        errors: Error handling ('strict', 'replace', 'backslashreplace', 'xmlcharrefreplace')
        cleanup: Remove backup and metadata files after restore
        force: Force restore even if file hash doesn't match
        strict_hash: Fail if file hash doesn't match conversion metadata (can be overridden with force)

    Returns:
        dict with restoration result
    """
    path = Path(file_path).resolve()

    if not path.exists():
        return {"status": "error", "error": f"File not found: {file_path}"}

    # Load metadata
    meta_dir = path.parent / ".charenc_meta"
    meta_path = meta_dir / f"{path.name}.json"
    metadata = None

    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return {"status": "error", "error": f"Cannot read metadata: {e}"}

    # If metadata not found by filename, search by output_file field
    if metadata is None and meta_dir.exists():
        for json_file in meta_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    candidate = json.load(f)
                    if candidate.get("output_file") == str(path):
                        metadata = candidate
                        meta_path = json_file
                        break
            except (json.JSONDecodeError, IOError):
                continue

    # Verify file hash if metadata contains converted_hash
    hash_warning = None
    expected_hash = None
    current_hash = None
    if metadata and metadata.get('converted_hash'):
        try:
            current_hash = get_file_hash(path)
            expected_hash = metadata['converted_hash']
            if current_hash != expected_hash:
                if strict_hash and not force:
                    return {
                        "status": "error",
                        "error": "File has been modified since conversion (hash mismatch). Use --force to override.",
                        "expected_hash": expected_hash,
                        "current_hash": current_hash
                    }
                hash_warning = "File was modified since conversion (hash mismatch)"
        except IOError:
            pass  # If hash calculation fails, continue without verification

    # Determine encoding
    target_encoding = encoding
    if target_encoding is None:
        if metadata is None:
            return {
                "status": "error",
                "error": "No metadata found. Specify encoding with --encoding"
            }
        target_encoding = metadata["original_encoding"]

    # Get line ending from metadata
    line_ending = "LF"
    if metadata:
        line_ending = metadata.get("line_ending", "LF")

    # Read UTF-8 content
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except IOError as e:
        return {"status": "error", "error": f"Cannot read file: {e}"}

    # Restore line endings
    if line_ending == "CRLF":
        # Normalize to LF first, then convert to CRLF
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = text.replace('\n', '\r\n')
    elif line_ending == "CR":
        text = text.replace('\r\n', '\n').replace('\n', '\r')

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
    output_path = Path(output).resolve() if output else path
    try:
        with open(output_path, 'wb') as f:
            f.write(encoded_bytes)
    except IOError as e:
        return {"status": "error", "error": f"Cannot write file: {e}"}

    # Cleanup
    backup_removed = False
    meta_removed = False

    if cleanup and metadata:
        # Remove backup file
        if metadata.get("backup_path"):
            backup_path = Path(metadata["backup_path"])
            if backup_path.exists():
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
        "file": str(output_path),
        "encoding": target_encoding,
        "line_ending": line_ending,
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
        "--encoding", "-e",
        help="Target encoding (default: from metadata)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: overwrite original)"
    )
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
    parser.add_argument(
        "--strict-hash",
        action="store_true",
        help="Fail if file hash doesn't match conversion metadata (can be overridden with --force)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force restore even if file hash doesn't match (useful with --strict-hash)"
    )

    args = parser.parse_args()

    result = restore_encoding(
        args.file,
        encoding=args.encoding,
        output=args.output,
        errors=args.errors,
        cleanup=not args.keep_backup,
        force=args.force,
        strict_hash=args.strict_hash
    )

    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
