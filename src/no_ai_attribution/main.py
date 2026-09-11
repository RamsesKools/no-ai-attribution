"""Reject AI attribution in git commit messages."""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterable, Sequence
from re import Pattern

AI_TOOLS = (
    "claude",
    "anthropic",
    "copilot",
    "chatgpt",
    "openai",
    "codex",
    "gpt-?[0-9]",
    "gemini",
    "cursor",
    "windsurf",
    "devin",
    "aider",
    "artificial intelligence",
    "language model",
    r"\bai\b",
    r"\bllm\b",
)

ATTRIBUTION_TRAILERS = (
    "co-?authored-by",
    "assisted-by",
    "authored-by",
    "created-by",
    "generated-by",
    "helped-by",
    "written-by",
)

ATTRIBUTION_VERBS = (
    "assisted",
    "authored",
    "built",
    "created",
    "generated",
    "made",
    "produced",
    "written",
)

_AI = "|".join(AI_TOOLS)

PATTERNS = (
    # Trailer crediting an AI tool: "Co-authored-by: Claude <...>".
    re.compile(rf"^\s*(?:{'|'.join(ATTRIBUTION_TRAILERS)})\s*:.*(?:{_AI})", re.IGNORECASE),
    # Prose credit: "generated with Claude Code", "written by ChatGPT".
    re.compile(
        rf"(?:{'|'.join(ATTRIBUTION_VERBS)})\s+(?:with|by|using)\s+\W*(?:{_AI})", re.IGNORECASE
    ),
    # Addresses used by AI committers.
    re.compile(
        r"noreply@anthropic\.com|@openai\.com|\[bot\]@users\.noreply\.github\.com", re.IGNORECASE
    ),
    # The robot emoji, which several tools sign off with.
    re.compile("\N{ROBOT FACE}"),
)

SCISSORS = re.compile(r"^#\s*-{6,}\s*>8\s*-{6,}")


def visible_lines(text: str) -> list[str]:
    """Message lines git would keep, blanked instead of dropped to keep numbering."""
    lines = []
    for line in text.splitlines():
        if SCISSORS.match(line):
            break
        lines.append("" if line.startswith("#") else line)
    return lines


def find_violations(
    text: str,
    extra_patterns: Iterable[Pattern[str]] = (),
    allow_patterns: Iterable[Pattern[str]] = (),
) -> list[tuple[int, str]]:
    patterns = (*PATTERNS, *extra_patterns)
    allowed = tuple(allow_patterns)
    return [
        (number, line)
        for number, line in enumerate(visible_lines(text), start=1)
        if any(pattern.search(line) for pattern in patterns)
        and not any(pattern.search(line) for pattern in allowed)
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filenames",
        nargs="*",
        help="commit message files, as passed by the pre-commit commit-msg stage",
    )
    parser.add_argument(
        "--extra-pattern",
        action="append",
        default=[],
        metavar="REGEX",
        help="additional case-insensitive regex to reject; repeatable",
    )
    parser.add_argument(
        "--allow-pattern",
        action="append",
        default=[],
        metavar="REGEX",
        help="case-insensitive regex exempting a line from every check; repeatable",
    )
    args = parser.parse_args(argv)

    extra_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in args.extra_pattern]
    allow_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in args.allow_pattern]

    returncode = 0
    for filename in args.filenames:
        with open(filename, encoding="utf-8") as handle:
            violations = find_violations(handle.read(), extra_patterns, allow_patterns)
        if violations:
            returncode = 1
            print(f"{filename}: AI attribution is not allowed in commit messages.")
            for number, line in violations:
                print(f"  line {number}: {line.strip()}")
            print("Remove the line(s) above and commit again.")
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
