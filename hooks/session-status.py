#!/usr/bin/env python3
"""SessionStart hook: print a short factual git status into each new session.

For SessionStart, stdout is injected as context Claude can see — so after a
/clear (or on startup/resume) Claude isn't starting blind. Kept fast and small:
a few lines of plain facts, no repo-wide scans. Outside a git repo it prints
nothing. Always exits 0 (never blocks a session).
"""
import subprocess
import sys


def git(args):
    try:
        out = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=3,
        )
        if out.returncode != 0:
            return ""
        return out.stdout.strip()
    except Exception:
        return ""


# Only emit anything inside a git work tree.
if git(["rev-parse", "--is-inside-work-tree"]) != "true":
    sys.exit(0)

branch = git(["rev-parse", "--abbrev-ref", "HEAD"]) or "(detached)"
last = git(["log", "-1", "--pretty=%h %s"])
porcelain = git(["status", "--porcelain"])

changed = [ln[2:].lstrip() for ln in porcelain.splitlines() if ln.strip()]
lines = ["Session status (from git):", f"- Branch: {branch}"]
if last:
    lines.append(f"- Last commit: {last}")
if changed:
    shown = ", ".join(changed[:5])
    more = f" (+{len(changed) - 5} more)" if len(changed) > 5 else ""
    lines.append(f"- Uncommitted changes: {len(changed)} file(s): {shown}{more}")
else:
    lines.append("- Working tree clean")

print("\n".join(lines))
sys.exit(0)
