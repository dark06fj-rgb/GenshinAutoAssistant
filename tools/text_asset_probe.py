#!/usr/bin/env python3
"""Read-only probe for plain-text files in a user-authorized game export.

This tool does not unpack archives, decrypt containers, modify inputs, or execute files.
It reports only format/encoding and counts, not proprietary text contents.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TEXT_SUFFIXES = {".json", ".txt", ".csv", ".xml", ".yaml", ".yml", ".ini", ".po", ".tsv"}


def inspect_text(path: Path, max_bytes: int = 2_000_000) -> dict:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return {"status": "unreadable", "error": str(exc)}
    if len(raw) > max_bytes:
        return {"status": "skipped", "reason": "file exceeds size limit", "size_bytes": len(raw)}
    if b"\x00" in raw[:4096] and not raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return {"status": "skipped", "reason": "binary content", "size_bytes": len(raw)}
    encoding = "utf-8"
    payload = raw
    if raw.startswith(b"\xff\xfe"):
        encoding, payload = "utf-16-le", raw[2:]
    elif raw.startswith(b"\xfe\xff"):
        encoding, payload = "utf-16-be", raw[2:]
    try:
        text = payload.decode(encoding)
    except UnicodeDecodeError:
        return {"status": "skipped", "reason": "not valid supported text encoding", "size_bytes": len(raw)}
    stripped = text.lstrip()
    kind = "text"
    string_count = 0
    if path.suffix.lower() == ".json" or stripped.startswith(("{", "[")):
        try:
            value = json.loads(text)
            kind = "json"
            def count_strings(item):
                if isinstance(item, str):
                    return 1
                if isinstance(item, dict):
                    return sum(count_strings(k) + count_strings(v) for k, v in item.items())
                if isinstance(item, list):
                    return sum(count_strings(v) for v in item)
                return 0
            string_count = count_strings(value)
        except json.JSONDecodeError:
            kind = "text (invalid JSON)"
    elif path.suffix.lower() in {".xml"} or stripped.startswith("<?xml"):
        kind = "xml candidate"
    elif path.suffix.lower() in {".csv", ".tsv"}:
        kind = "delimited-text candidate"
    elif path.suffix.lower() in {".yaml", ".yml"}:
        kind = "yaml candidate"
    return {
        "status": "readable",
        "encoding": encoding,
        "format": kind,
        "size_bytes": len(raw),
        "line_count": len(text.splitlines()),
        "string_value_count": string_count,
    }


def probe(root: Path, max_bytes: int = 2_000_000) -> dict:
    results = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        details = inspect_text(path, max_bytes=max_bytes)
        if details["status"] == "readable":
            results.append({"path": path.relative_to(root).as_posix(), **details})
    return {
        "format": "plain-text-probe-v1",
        "root": root.name,
        "readable_file_count": len(results),
        "files": results,
        "limitations": [
            "Only already-plain text files are inspected; archives and game containers are not unpacked.",
            "No source text is copied into the report.",
            "This is reconnaissance, not proof that a file is safe or supported to replace.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing files you are authorized to inspect")
    parser.add_argument("--output", type=Path, help="Write JSON report outside the input directory")
    parser.add_argument("--max-bytes", type=int, default=2_000_000)
    args = parser.parse_args()
    root = args.directory.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    if args.max_bytes < 1:
        parser.error("--max-bytes must be positive")
    report = json.dumps(probe(root, args.max_bytes), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.expanduser().resolve()
        if output == root or root in output.parents:
            parser.error("output must be outside the scanned input directory")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
