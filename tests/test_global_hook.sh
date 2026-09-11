#!/bin/sh
# Checks hooks/commit-msg in the layouts people install it in.
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

export NO_AI_ATTRIBUTION="$repo/src/no_ai_attribution/main.py"
mkdir "$work/global-hooks"
cp "$repo/hooks/commit-msg" "$work/global-hooks/commit-msg"

new_repo() {
    rm -rf "$work/$1"
    mkdir "$work/$1"
    git -C "$work/$1" init -q
    git -C "$work/$1" config user.email test@example.com
    git -C "$work/$1" config user.name Test
}

commit() { git -C "$work/$1" commit -q --allow-empty -m "$2"; }

fail() { echo "FAIL: $1" >&2; exit 1; }

# Machine-wide install, with a repo-local hook that must keep running.
new_repo global-plus-local
git -C "$work/global-plus-local" config core.hooksPath "$work/global-hooks"
printf '#!/bin/sh\ntouch "$(dirname "$0")/../../ran"\n' > "$work/global-plus-local/.git/hooks/commit-msg"
chmod +x "$work/global-plus-local/.git/hooks/commit-msg"
commit global-plus-local 'Fix x' || fail "clean message rejected"
[ -f "$work/global-plus-local/ran" ] || fail "repo-local hook did not run"
! commit global-plus-local 'Fix x

Co-authored-by: Claude <noreply@anthropic.com>' >/dev/null 2>&1 || fail "attributed message accepted"

# Machine-wide install, no repo-local hook to chain to.
new_repo global-only
git -C "$work/global-only" config core.hooksPath "$work/global-hooks"
commit global-only 'Fix x' || fail "clean message rejected without a repo-local hook"

# Installed straight into .git/hooks: must not exec itself.
new_repo self
cp "$repo/hooks/commit-msg" "$work/self/.git/hooks/commit-msg"
perl -e 'alarm 20; exec @ARGV' git -C "$work/self" commit -q --allow-empty -m 'Fix x' \
    || fail "recursed or rejected a clean message"

echo "hooks/commit-msg: all layouts OK"
