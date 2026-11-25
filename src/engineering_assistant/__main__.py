"""Class 1 command-line catalogue entry point, retained in the new package."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from engineering_assistant.services.catalog import build_manifest


def main() -> None:
    """Print a JSON manifest for a documents directory."""
    parser = argparse.ArgumentParser(description="Build a document manifest")
    parser.add_argument("directory", type=Path, help="Directory to scan")
    args = parser.parse_args()
    manifest = build_manifest(args.directory)
    print(json.dumps([asdict(item) for item in manifest], indent=2))


if __name__ == "__main__":
    main()
