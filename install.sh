#!/usr/bin/env bash
# Installs the whole Claude Code kit into ~/.claude (applies to every repo).
# Safe to re-run: copies files and merges hook settings without duplicating
# or overwriting unrelated settings.
set -euo pipefail

# Resolve the directory this script lives in, so it works from anywhere.
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST="$HOME/.claude"

echo "Installing Claude Code kit into $DST ..."

mkdir -p "$DST/skills/feature" "$DST/skills/setup-claude-md" "$DST/hooks" "$DST/agents"

# 1) Skills
cp "$SRC/skills/feature/SKILL.md"          "$DST/skills/feature/SKILL.md"
cp "$SRC/skills/setup-claude-md/SKILL.md"  "$DST/skills/setup-claude-md/SKILL.md"

# 1b) Review subagents
cp "$SRC"/agents/*.md                       "$DST/agents/"

# 1c) Global rules — appended to ~/.claude/CLAUDE.md, never overwriting it
python3 - "$SRC/global-CLAUDE.md" << 'PYEOF'
import os, sys
block = open(sys.argv[1]).read().strip() + "\n"
p = os.path.expanduser("~/.claude/CLAUDE.md")
existing = ""
if os.path.isfile(p):
    with open(p) as f:
        existing = f.read()
if ">>> claude-code-kit global rules >>>" in existing:
    print("Global rules already present in ~/.claude/CLAUDE.md — left as is")
else:
    sep = "\n\n" if existing.strip() else ""
    with open(p, "a") as f:
        f.write(sep + block)
    print(("Appended" if existing.strip() else "Created") + f" global rules in {p}")
PYEOF

# 2) Hooks
cp "$SRC/hooks/block-ai-attribution.py"     "$DST/hooks/block-ai-attribution.py"
cp "$SRC/hooks/protect-tests.py"            "$DST/hooks/protect-tests.py"
cp "$SRC/hooks/session-status.py"           "$DST/hooks/session-status.py"
chmod +x "$DST/hooks/block-ai-attribution.py" "$DST/hooks/protect-tests.py" "$DST/hooks/session-status.py"

# 4) Merge hooks into ~/.claude/settings.json (idempotent, non-destructive)
python3 - << 'PYEOF'
import json, os
p = os.path.expanduser("~/.claude/settings.json")
s = {}
if os.path.isfile(p):
    try:
        with open(p) as f:
            s = json.load(f)
    except Exception:
        s = {}
pre = s.setdefault("hooks", {}).setdefault("PreToolUse", [])
def already(sub):
    return any(sub in h.get("command", "")
               for e in pre for h in e.get("hooks", []))
if not already("block-ai-attribution.py"):
    pre.append({"matcher": "Bash", "hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/block-ai-attribution.py"}]})
if not already("protect-tests.py"):
    pre.append({"matcher": "Edit|MultiEdit|Write", "hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/protect-tests.py"}]})
start = s["hooks"].setdefault("SessionStart", [])
def already_start(sub):
    return any(sub in h.get("command", "")
               for e in start for h in e.get("hooks", []))
if not already_start("session-status.py"):
    start.append({"hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/session-status.py"}]})
with open(p, "w") as f:
    json.dump(s, f, indent=2)
print("Merged hooks into", p)
PYEOF

echo ""
echo "Done. Installed:"
echo "  /feature           skill  (build/fix anything)"
echo "  /setup-claude-md   skill  (generate a lean CLAUDE.md)"
echo "  6 review agents     (frontend/backend/db/test/deploy/ai — invoked when relevant)"
echo "  2 guardrail hooks   (block AI-attributed commits + test weakening)"
echo "  1 status hook        (prints git status into every new session)
  global rules         (appended to ~/.claude/CLAUDE.md — applies everywhere)"
echo ""
echo "Verify: open Claude Code in any repo, then run  /feature   and  /hooks"
