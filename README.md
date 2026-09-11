# no-ai-attribution

A [pre-commit](https://pre-commit.com/) hook that rejects AI attribution in git commit messages.

Coding agents like to sign their work: `Co-Authored-By: Claude`, `🤖 Generated with [Claude Code]`, `Assisted-by: Codex`.
If you would rather your history not carry that, this hook blocks the commit and tells you which line to remove.

## Usage

Add it to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/RamsesKools/no-ai-attribution
    rev: v0.1.0
    hooks:
      - id: no-ai-attribution
```

The hook runs at the `commit-msg` stage, so install that stage once per repo:

```sh
pre-commit install --hook-type commit-msg
```

## What it blocks

- Attribution trailers naming an AI tool: `Co-authored-by`, `Assisted-by`, `Generated-by`, `Helped-by`, and friends.
- Prose credits such as `generated with Claude Code`, `written by ChatGPT`, `made with Cursor`.
- Addresses AI committers use, like `noreply@anthropic.com` and `...[bot]@users.noreply.github.com`.
- The 🤖 robot emoji.

Comment lines and the verbose diff below git's scissors line are ignored, so a diff that happens to contain one of these strings will not fail the commit.

Mentioning an AI tool in a normal message is fine: `Document the claude/CLAUDE.md sync script` passes, only the crediting patterns fail.

## Configuration

Add your own patterns (case-insensitive regexes, repeatable):

```yaml
      - id: no-ai-attribution
        args: [--extra-pattern, "robodev", --extra-pattern, "paired-with:"]
```

## Installing it everywhere on a machine

pre-commit is per repo. To cover every repo on a machine, point git's global `core.hooksPath` at a directory holding a `commit-msg` hook that calls this one, and have that hook chain through to each repo's own `.git/hooks` so local hooks keep working.

## Development

```sh
pip install -e '.[test]'
pytest
```
