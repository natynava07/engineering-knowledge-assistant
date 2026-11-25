"""Command-line entry point for the document catalog."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from engineering_knowledge_assistant.catalog import build_manifest


def main() -> None:
    """Print a JSON manifest for a documents directory."""
    parser = argparse.ArgumentParser(description="Build a document manifest")
    parser.add_argument("directory", type=Path, help="Directory to scan")
    args = parser.parse_args()
    manifest = build_manifest(args.directory)
    print(json.dumps([asdict(item) for item in manifest], indent=2))


if __name__ == "__main__":
    main()
