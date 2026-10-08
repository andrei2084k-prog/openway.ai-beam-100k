#!/usr/bin/env python3
"""Check every file of this repository against MANIFEST.sha256.

No third-party packages. Reports files whose hash differs, files listed but
missing, and files present but not listed.

Usage:  python3 verify/check_manifest.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "MANIFEST.sha256"
SKIP_DIRS = {".git", ".replay", "__pycache__"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    listed: dict[str, str] = {}
    for line in MANIFEST.read_text().splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            listed[name.strip()] = digest

    bad = []
    for name, digest in sorted(listed.items()):
        path = ROOT / name
        if not path.is_file():
            bad.append(f"missing   {name}")
        elif sha256(path) != digest:
            bad.append(f"changed   {name}")

    present = {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts)
    }
    for name in sorted(present - set(listed) - {"MANIFEST.sha256"}):
        bad.append(f"unlisted  {name}")

    print(f"files in manifest: {len(listed)}")
    if bad:
        print("FAIL")
        for b in bad:
            print("  " + b)
        return 1
    print("PASS — every file matches its SHA-256 in MANIFEST.sha256")
    return 0


if __name__ == "__main__":
    sys.exit(main())
