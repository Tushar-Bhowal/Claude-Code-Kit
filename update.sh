#!/usr/bin/env bash
# Updates an existing Claude Code Kit install to this version.
# Same as install.sh (idempotent + non-destructive) plus a clear post-update note
# about what needs a restart to take effect.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SRC/install.sh"

cat << 'NOTE'

──────────────────────────────────────────────
UPDATE APPLIED. To make the changes take effect:

1. Quit any running Claude Code session and start it again.
   (Agents and skills edited on disk are only picked up on restart.
    Hooks and settings reload on the next session automatically.)

2. Verify in any repo:
     /feature           and   /setup-claude-md   appear in the menu
     /hooks             lists the 3 hooks
     /agents            lists the 6 review agents

That's it — your kit is up to date.
──────────────────────────────────────────────
NOTE
