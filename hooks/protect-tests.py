#!/usr/bin/env python3
"""PreToolUse(Edit|MultiEdit|Write) hook: block edits that weaken tests.

Fires before Claude edits a file. If the target is a test file and the change
removes assertions or adds a skip/pending marker, it exits 2 to block the edit
and tells Claude to fix the code under test instead of gaming the suite.

This is a heuristic tripwire, not a proof. It catches the common cases
(deleted assertions, newly skipped tests). It can occasionally fire on a
legitimate refactor that consolidates assertions — when that happens, make the
edit manually, or temporarily disable the hook. Non-test files always pass.
"""
import json
import os
import re
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = data.get("tool_name", "")
if tool not in ("Edit", "MultiEdit", "Write"):
    sys.exit(0)

ti = data.get("tool_input", {}) or {}
path = ti.get("file_path", "") or ""


def is_test_file(p):
    p = p.replace("\\", "/")
    low = p.lower()
    base = os.path.basename(low)
    if "/__tests__/" in low or "/test/" in low or "/tests/" in low:
        return True
    if ".test." in base or ".spec." in base:
        return True
    if base.startswith("test_") and base.endswith(".py"):
        return True
    if base.endswith(("_test.py", "_test.go", "_test.rb", "_spec.rb", "test.ts", "test.js")):
        return True
    return False


if not is_test_file(path):
    sys.exit(0)

ASSERT_RE = re.compile(
    r"(\bassert\b|\bassert_\w+|\bassertEqual\b|\bassertTrue\b|\bassertFalse\b|"
    r"\bassertRaises\b|\bassertIn\b|\bassertIs\b|\bexpect\s*\(|\.should\b|"
    r"\bEXPECT_\w+|\bASSERT_\w+|\.to\.(equal|be|deep|have|contain|throw))",
    re.IGNORECASE,
)
SKIP_RE = re.compile(
    r"(\.skip\b|\bxit\b|\bxdescribe\b|@pytest\.mark\.skip|@unittest\.skip|"
    r"\bit\.skip\b|\btest\.skip\b|\bdescribe\.skip\b|\bt\.Skip\(|\bpending\b)",
    re.IGNORECASE,
)


def count(rx, s):
    return len(rx.findall(s or ""))


pairs = []  # list of (old_text, new_text)
if tool == "Edit":
    pairs.append((ti.get("old_string", ""), ti.get("new_string", "")))
elif tool == "MultiEdit":
    for e in ti.get("edits", []) or []:
        pairs.append((e.get("old_string", ""), e.get("new_string", "")))
elif tool == "Write":
    new = ti.get("content", "")
    old = ""
    try:
        if path and os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                old = f.read()
    except Exception:
        old = ""
    pairs.append((old, new))

old_assert = sum(count(ASSERT_RE, o) for o, _ in pairs)
new_assert = sum(count(ASSERT_RE, n) for _, n in pairs)
old_skip = sum(count(SKIP_RE, o) for o, _ in pairs)
new_skip = sum(count(SKIP_RE, n) for _, n in pairs)

reasons = []
if new_assert < old_assert:
    reasons.append(f"removes {old_assert - new_assert} test assertion(s)")
if new_skip > old_skip:
    reasons.append("adds a skip/pending marker that disables a test")

if reasons:
    sys.stderr.write(
        "Blocked: this edit to a test file " + " and ".join(reasons) + ". "
        "Do not weaken, skip, or delete tests to make the suite pass — fix the "
        "code under test instead. If the test itself is genuinely wrong, explain "
        "why and ask before changing it.\n"
    )
    sys.exit(2)

sys.exit(0)
