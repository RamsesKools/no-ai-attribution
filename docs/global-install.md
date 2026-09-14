# Install the hook globally

This guide installs the checker once and makes it available to Git repositories on a device.

## Install the checker for a global hook

Install the command with `uv`:

```sh
uv tool install git+https://github.com/RamsesKools/no-ai-attribution
```

Use `pipx install git+https://github.com/RamsesKools/no-ai-attribution` if you prefer pipx.

## Approach 1: Git template for new repositories

This is the preferred approach if you use pre-commit regularly.
It avoids changing `core.hooksPath` and automatically adds the hook to repositories created afterwards.

```sh
mkdir -p ~/.config/git/template/hooks
curl -fsSL https://raw.githubusercontent.com/RamsesKools/no-ai-attribution/main/hooks/commit-msg \
  -o ~/.config/git/template/hooks/commit-msg
chmod +x ~/.config/git/template/hooks/commit-msg
git config --global init.templateDir ~/.config/git/template
```

For an existing repository, copy the hook into its local hooks directory:

```sh
install -d .git/hooks
curl -fsSL https://raw.githubusercontent.com/RamsesKools/no-ai-attribution/main/hooks/commit-msg \
  -o .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

If the repository already uses pre-commit, the preferred option is to add this repository to its `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/RamsesKools/no-ai-attribution
    rev: v0.1.0
    hooks:
      - id: no-ai-attribution
```

Then install the commit-message stage:

```sh
uvx pre-commit install --hook-type commit-msg
```

If you do not want to change the pre-commit configuration, the copied `.git/hooks/commit-msg` also works alongside a normal `uvx pre-commit install`.

## Approach 2: global hooks path

This approach applies to existing and new repositories automatically, but it is not the preferred approach for machines where pre-commit is used frequently.

```sh
mkdir -p ~/.config/git/hooks
curl -fsSL https://raw.githubusercontent.com/RamsesKools/no-ai-attribution/main/hooks/commit-msg \
  -o ~/.config/git/hooks/commit-msg
chmod +x ~/.config/git/hooks/commit-msg
git config --global core.hooksPath ~/.config/git/hooks
```

The global hook hands over to a repository's own `commit-msg` hook when one exists.

Important: setting `core.hooksPath` makes `pre-commit install` refuse to install hooks.
This affects future repositories where you want to enable pre-commit, even though already-installed repository hooks continue to work.

If you choose this approach and need to install pre-commit in a repository, temporarily clear the global setting, install the repository hooks, and restore it:

```sh
global_hooks=$(git config --global --get core.hooksPath)
git config --global --unset-all core.hooksPath
uvx pre-commit install
git config --global core.hooksPath "$global_hooks"
```

The global `commit-msg` hook and the repository's pre-commit hooks will then both run.

## Choosing an approach

- Prefer the Git template when you use pre-commit regularly.
- Use the global hooks path when existing repositories must be covered automatically and the installation tradeoff is acceptable.
- Do not combine both approaches, or the hook may run twice.
