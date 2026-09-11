# no-ai-attribution

A [pre-commit](https://pre-commit.com/) hook that rejects AI attribution in git commit messages.

Coding agents like to sign their work: `Co-Authored-By: Claude`, `🤖 Generated with [Claude Code]`, `Assisted-by: Codex`.
If you would rather your history not carry that, this hook blocks the commit and tells you which line to remove.

## Why

AI agents are tools, not authors.
My compiler, IDE, linter and formatter never get a `Co-authored-by:` line, and neither should the agent.

> Until we decide AI Agents are actual beings and not tools, I'll happily change my point of view then.

Not every agent vendor shares that view.
Several of them ship override instructions telling the agent to sign its commits regardless of what your `AGENTS.md` or `CLAUDE.md` asks for, so "do not add attribution" quietly loses to the system prompt.

The lesson generalises: when you want to force agent behaviour, do not rely on instructions in a markdown file.
Put a guardrail in the environment it works in.
A hook that fails the commit is not something an agent can talk itself out of.

## Install

### In one repo, through pre-commit

Add it to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/RamsesKools/no-ai-attribution
    rev: v0.1.0
    hooks:
      - id: no-ai-attribution
```

The hook runs at the `commit-msg` stage, which `pre-commit install` does not cover by default, so install that stage once per repo:

```sh
pre-commit install --hook-type commit-msg
```

That is the whole setup.
pre-commit builds the hook its own virtualenv, and the hook needs nothing beyond the standard library.

### In every repo on your machine

pre-commit is per repo, and an agent can always work in a repo that does not have it.
To cover everything, install the checker once and point git's global `core.hooksPath` at [hooks/commit-msg](hooks/commit-msg):

```sh
uv tool install git+https://github.com/RamsesKools/no-ai-attribution
mkdir -p ~/.config/git/hooks
curl -fsSL https://raw.githubusercontent.com/RamsesKools/no-ai-attribution/main/hooks/commit-msg \
    -o ~/.config/git/hooks/commit-msg
chmod +x ~/.config/git/hooks/commit-msg
git config --global core.hooksPath ~/.config/git/hooks
```

Use `pipx install git+https://github.com/RamsesKools/no-ai-attribution` if you prefer pipx over uv.

`core.hooksPath` replaces `.git/hooks` instead of adding to it, so the script hands over to the repo's own `commit-msg` hook when there is one.
Repos that use pre-commit keep working.

Two things worth knowing:

- If `core.hooksPath` is already set, put the script in that directory rather than changing the setting.
- Hooks inherit the PATH of whatever started them, and some git GUIs have a short one. Set `NO_AI_ATTRIBUTION` to the output of `which no-ai-attribution` in the script if it cannot find the binary.

### In one repo, without pre-commit

Copy the same script to `.git/hooks/commit-msg` and make it executable.
It notices that it is the repo hook and skips the handover.

## What it blocks

- Attribution trailers naming an AI tool: `Co-authored-by`, `Assisted-by`, `Generated-by`, `Helped-by`, and friends.
- Prose credits such as `generated with Claude Code`, `written by ChatGPT`, `made with Cursor`.
- Addresses AI committers use, like `noreply@anthropic.com` and `...[bot]@users.noreply.github.com`.
- The 🤖 robot emoji.

Comment lines and the verbose diff below git's scissors line are ignored, so a diff that happens to contain one of these strings will not fail the commit.

Mentioning an AI tool in a normal message is fine: `Document the claude/CLAUDE.md sync script` passes, only the crediting patterns fail.

## Configuration

Both flags take case-insensitive regexes and can be repeated.

`--extra-pattern` rejects more:

```yaml
      - id: no-ai-attribution
        args: [--extra-pattern, "robodev", --extra-pattern, "paired-with:"]
```

`--allow-pattern` exempts a line from every check, for the people the patterns misread.
A co-author called Ai, or a colleague whose address ends in `@cursor.com`, would otherwise be blocked:

```yaml
      - id: no-ai-attribution
        args: [--allow-pattern, "ai nguyen"]
```

## Development

```sh
uv sync
uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the rest: how to change what the hook catches, how to test it the way a consumer runs it, and how to cut a release.
