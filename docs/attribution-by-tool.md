# How coding agents attribute commits

What each tool writes into a commit, and how to switch it off at the source where that is possible.
This hook exists because several of them cannot be switched off, and one that can does not always honour the setting.

## What each tool writes

| Tool | Commit attribution | Default | Disable |
|---|---|---|---|
| Claude Code | `Co-Authored-By: Claude <noreply@anthropic.com>`, a `🤖 Generated with [Claude Code]` footer, and a `Claude-Session:` trailer on web and Remote Control sessions | On | Yes, see below |
| Copilot coding agent (cloud) | Commit author set to `copilot-swe-agent[bot]`, the human who assigned the task credited with `Co-authored-by:`, plus an `Agent-Logs-Url:` trailer | On | No ([community#179983](https://github.com/orgs/community/discussions/179983)) |
| Copilot CLI and VS Code | `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` | On | No ([copilot-cli#975](https://github.com/github/copilot-cli/issues/975)) |
| Codex CLI | `Co-authored-by: Codex <noreply@openai.com>`, sometimes a `Generated with [Codex]` footer | Off | Already off |
| Aider | `Co-authored-by: aider (model) <noreply@aider.chat>`, plus `(aider)` appended to the git author and committer names | On | Yes, see below |
| Cursor | `Made-with: Cursor` | On, varies by version | Yes, see below |
| Gemini CLI | Nothing built in, people wire up `Co-authored-by: gemini-cli ...` in `GEMINI.md` themselves | Off | Drop the instruction |
| Devin, Windsurf | No public documentation on a default trailer | Unknown | Unknown |

Cursor's `Made-with:` footer is reported by users rather than documented by Cursor, so treat that row as the least certain one.

## Turning it off

### Claude Code

In `~/.claude/settings.json`, an empty string hides that piece of attribution:

```json
{
  "attribution": { "commit": "", "pr": "", "sessionUrl": false }
}
```

`"includeCoAuthoredBy": false` still works but is deprecated.
Open issues report the setting is not always honoured ([#41873](https://github.com/anthropics/claude-code/issues/41873), [#77830](https://github.com/anthropics/claude-code/issues/77830)).

### Aider

```sh
aider --no-attribute-co-authored-by --no-attribute-author --no-attribute-committer
```

The same keys work in `.aider.conf.yml`.
See the [aider git docs](https://aider.chat/docs/git.html).

### Cursor

Toggle it in the IDE settings, or set it in `~/.cursor/cli-config.json`.

### Codex

Off by default, and [Codex adds no commit attribution of its own](https://github.com/openai/codex/discussions/9449).
Both `.codex/config.toml` and `AGENTS.md` can ask for it back, so the only thing to do is not ask.

## What this hook cannot see

A `commit-msg` hook gets the message file and nothing else.
Aider's `(aider)` name suffix and the Copilot coding agent's bot author live in the author and committer fields, so they pass.
Check those separately:

```sh
git log --format='%an <%ae> | %cn <%ce>'
```

## Assisted-by, the non-vendor alternative

Several foundations settled on `Assisted-by:` instead of `Co-authored-by:`, because co-authorship implies a legal status an AI cannot hold and a CLA it cannot sign.
The [Linux kernel](https://docs.kernel.org/process/coding-assistants.html) wants `Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL]`; [Fedora](https://docs.fedoraproject.org/en-US/council/policy/ai-contribution-policy/), [LLVM](https://llvm.org/docs/AIToolPolicy.html) and [OpenTelemetry](https://github.com/open-telemetry/community/blob/main/policies/genai.md) recommend the same trailer, and [Apache](https://www.apache.org/legal/generative-tooling.html) and [OpenInfra](https://openinfra.org/legal/ai-policy/) add `Generated-by:` for mostly generated content.
[All Things Open has the background](https://allthingsopen.org/articles/open-source-ai-contributions-assisted-by-git-trailer-standard).

This hook blocks those too.
A better convention is still attribution.
