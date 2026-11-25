"""Validate the first line of a commit message against Conventional Commits."""

import re
import sys
from pathlib import Path

PATTERN = re.compile(
    r"^[a-z]+(?:\([a-z0-9._/-]+\))?!?: .+\S$"
)


def main() -> int:
    """Return a non-zero exit code for an invalid commit message."""
    if len(sys.argv) != 2:
        print("Usage: check_commit_message.py <commit-message-file>", file=sys.stderr)
        return 2
    message_file = Path(sys.argv[1])
    lines = message_file.read_text(encoding="utf-8").splitlines()
    header = next((line for line in lines if line.strip()), "")
    if not PATTERN.fullmatch(header):
        print(
            "Invalid commit header. Use '<type>(<scope>): <description>', "
            "for example 'feat(catalog): discover PDF files'.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
