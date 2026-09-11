# Contributing

## Setup

The project is managed with [uv](https://docs.astral.sh/uv/).

```sh
uv sync                      # .venv with the dev dependency group
uv run pytest                # unit tests
sh tests/test_global_hook.sh # tests hooks/commit-msg, needs no venv
uv run ruff check . && uv run ruff format .
uv run mypy
uv run pre-commit install --hook-type commit-msg # run this repo's own hook on its own commits
```

`uv run <cmd>` syncs the environment first, so there is nothing to activate.
CI runs the same commands with `--locked`, which fails if `uv.lock` is out of date.
Run `uv lock` after touching dependencies and commit the lockfile.

## What lives where

- [src/no_ai_attribution/main.py](src/no_ai_attribution/main.py): the entire checker, standard library only.
- [tests/test_main.py](tests/test_main.py): the message corpus, one list of messages that must fail and one that must pass.
- [hooks/commit-msg](hooks/commit-msg): the machine-wide git hook, tested by [tests/test_global_hook.sh](tests/test_global_hook.sh).
- [.pre-commit-hooks.yaml](.pre-commit-hooks.yaml): what consumers get when they add this repo to their config.

## Changing what the hook catches

Four tuples in `main.py` do the work:

- `AI_TOOLS`: names that make something AI attribution. A regex fragment, so `gpt-?[0-9]` and `\bai\b` are fine.
- `ATTRIBUTION_TRAILERS`: trailer keys, matched at the start of a line and followed by a colon.
- `ATTRIBUTION_VERBS`: verbs for prose credits, matched as `<verb> with|by|using <tool>`.
- `PATTERNS`: the assembled regexes, plus the standalone ones for committer addresses and the robot emoji.

Say a new agent called RoboDev starts signing commits with `Paired-with: RoboDev`.
Add `robodev` to `AI_TOOLS` and `paired-with` to `ATTRIBUTION_TRAILERS`, then add cases to both lists in `tests/test_main.py`:

```python
BLOCKED = [
    ...
    "Fix parser\n\nPaired-with: RoboDev",
]

ALLOWED = [
    ...
    "Pair up the robodev sensor readings",   # the near miss
]
```

Then `uv run pytest`.

Two rules keep this useful:

- Every new pattern gets a `BLOCKED` case and an `ALLOWED` near miss. Blocking a real commit annoys people far more than missing an attribution line, and the escape hatch is `--allow-pattern` or `git commit --no-verify`.
- Anchor short tokens with word boundaries. `\bai\b` matches `Helped-by: AI` without flagging `Fix aircraft parser`.

Users can already add their own patterns with `--extra-pattern`, so only add to the built-in lists when the tool is one most people would want blocked.

## Testing it the way a consumer runs it

```sh
printf 'Fix x\n\nCo-authored-by: Claude\n' > /tmp/msg.txt
uv run pre-commit try-repo . no-ai-attribution --hook-stage commit-msg --commit-msg-filename /tmp/msg.txt
```

`try-repo` clones the repo at HEAD, so commit your change before trusting the result.

## Releasing

1. Bump `version` in [pyproject.toml](pyproject.toml).
2. Commit, then tag: `git tag -a v0.2.0 -m 'v0.2.0' && git push --follow-tags`.
3. Bump the `rev:` in the README example.

Consumers pin `rev:`, so a tag reaches them only when they run `pre-commit autoupdate`.

## Why Python

The hook is a few dozen lines of regex over one file, so the language matters less than the install story, and Python wins on that:

- pre-commit is itself a Python tool, so every consumer of the primary install path already has a Python it can use. A Go or Rust rewrite would add a toolchain or a binary release pipeline to save nothing.
- `language: python` in `.pre-commit-hooks.yaml` means pre-commit builds an isolated virtualenv per consumer. No system packages, no version conflicts, and it works the same on macOS, Linux and Windows.
- The module has no dependencies and no imports outside the standard library, so `python3 src/no_ai_attribution/main.py msg.txt` works straight from a clone. That is what makes the machine-wide git hook a one-liner.
- Startup cost is irrelevant. This runs once per commit, after you have finished typing a message.

A compiled rewrite would only pay off if the hook had to run somewhere without Python, for example as a server-side `update` hook on a minimal image.
Shell plus grep is the other tempting option, and it is genuinely dependency free, but case-insensitive alternation, the robot emoji and the scissors line all behave differently between BSD and GNU grep, and the test suite would have to go with it.
