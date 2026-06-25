# Claude Code Kit

A personal Claude Code setup that works in **every** repo. Install once into `~/.claude`, update with a `git pull`. No persona costumes, no inflated claims — just the right tool for each job.

> Built for Claude Code as of mid-2026. Claude Code evolves; if a command name changes, the kit's principles still hold — update the affected file and send a PR.

## The problem it solves

Working with an AI coding agent, the same friction shows up every day:

- You **re-type the same instructions** on every task — "plan first, write tests, check accessibility, verify, don't put AI in the commit message."
- Output is **inconsistent** — thorough one session, sloppy the next.
- The agent **over-engineers** simple fixes, **over-comments** (a banner on every file, a note on every obvious line), or **commits before you're ready**.
- Commits get **AI-attribution footers** you don't want; tests quietly get **weakened or skipped** to make a suite pass.
- Long sessions **bloat with context** and quality drops; after `/clear` you start blind.

This kit fixes each with the right mechanism — a workflow skill for the repetition, read-only review agents for domain depth, deterministic hooks for the rules that must never break, and a lean global rules file for universal preferences.

| Friction | Handled by |
|---|---|
| Re-typing the workflow every time | `/feature` skill |
| Vague request → wrong build | `/feature` intake: restates & confirms before building |
| Inconsistent / shallow output | `/feature` + domain review agents |
| Over-engineering, premature commits | `/feature` (simplicity-first, commit only on request) |
| Banner/narration & noisy comments | `/feature` + global rules (essentials only) |
| AI footers in commits | commit-block hook (enforced) |
| Weakened / skipped tests | test-protect hook (enforced) |
| Bloated CLAUDE.md | `/setup-claude-md` (generate / audit / prune) |
| Losing your place after `/clear` | session-status hook |

## What's inside

| Piece | Type | What it does |
|---|---|---|
| `/feature` | skill | Build/fix anything end to end. Run it bare to brain-dump and have it restate + confirm; or `/feature <task>` directly. Understands → (asks if unclear) → recommends a model → plans (writes a plan file for big tasks) → implements (clean comments) → verifies with evidence → routes to a review agent → commits **only when you ask**, with no AI attribution. |
| `/setup-claude-md` | skill | Generate, **audit**, or prune a lean CLAUDE.md for the current project. On an existing file it leaves good lines alone and proposes only genuine gaps/trims — written like onboarding a new senior engineer, with a repo-specific pitfalls section. |
| 6 review agents | subagents | Read-only domain reviewers — frontend, backend, db, test, deploy, ai — that run in their own context and return a prioritized list. Auto-invoked when a change is in their domain. |
| 3 hooks | guardrails/context | Block AI-attributed commits, block test weakening, and print git status into every new session. The first two are enforced every time. |
| global rules | `~/.claude/CLAUDE.md` | A few universal rules (no banner/narration comments, no AI-attributed commits, ask-don't-assume, keep-it-simple) appended to your global CLAUDE.md so they apply in **every** session. Non-destructive — existing content is preserved. |

## Rough impact (honest estimates, not benchmarks)

Directional estimates from general usage, **not** measured benchmarks. Measure your own with `/context`, `/cost`, `/usage`.

- **Manual effort: ~30–50% less hands-on work per feature** — less re-prompting the workflow and domain checks. The kit's biggest, most reliable win.
- **Main-context tokens: meaningfully lower** — review/investigation run in subagents' own context.
- **Total tokens: roughly flat to slightly higher** — each review agent is a real call. This kit buys **consistency and less typing**, not a lower token bill. Real token savings come from the habits it encourages (`/clear`, lean CLAUDE.md, right model).

## Requirements

- **Claude Code** installed and working (`claude` runs in your terminal)
- **Python 3** (for the hooks) — `python3 --version`
- **git**

## Install

**From the repo (recommended — easy to update later):**

```bash
git clone https://github.com/<your-username>/claude-code-kit.git
cd claude-code-kit
bash install.sh
```

**Or from the zip:** unzip, `cd` in, `bash install.sh`.

Everything installs into `~/.claude/`, so it applies to every repo. The installer is non-destructive and safe to re-run.

## Update

```bash
cd claude-code-kit
git pull
bash update.sh
```

Then **restart Claude Code** so it picks up updated agents and skills (hooks and settings reload automatically). `update.sh` is the same safe install plus a restart reminder; it preserves your `~/.claude/CLAUDE.md` and never duplicates hooks or rules.

## Verify

In any repo: `/feature` and `/setup-claude-md` appear in the menu, `/hooks` lists 3 hooks, `/agents` lists 6 review agents.

## Use

```
/feature                                    # bare: brain-dump, it restates & confirms
/feature add a logout button that clears the session
/feature redesign the auth page to match the attached HTML — logic intact, design only
/setup-claude-md                            # generate/audit this project's CLAUDE.md
use the backend-review agent on these changes
```

Attach an image or paste an error log in the same message as `/feature` when relevant. Review agents auto-route by domain, or invoke one explicitly. Don't run all six on every task — use the one(s) the change touches. For big multi-session tasks the skill keeps a worklog in `.claude/plans/` (add that to `.gitignore`).

## Where everything lands

```
~/.claude/
├── settings.json          # hooks merged in here
├── CLAUDE.md              # global rules appended (your content preserved)
├── skills/
│   ├── feature/SKILL.md
│   └── setup-claude-md/SKILL.md
├── agents/
│   ├── frontend-review.md   backend-review.md   db-review.md
│   └── test-review.md       deploy-review.md    ai-review.md
└── hooks/
    ├── block-ai-attribution.py
    ├── protect-tests.py
    └── session-status.py
```

## Publishing your own copy

1. Create an empty GitHub repo named `claude-code-kit`.
2. From the unzipped folder: `git init && git add . && git commit -m "initial kit" && git branch -M main && git remote add origin https://github.com/<you>/claude-code-kit.git && git push -u origin main`
3. Share the clone command. Others install and update with the exact steps above.

When you tweak a skill/agent/hook, commit and push; users get it on their next `git pull && bash update.sh`.

## Roadmap / future goals

This is an evolving, in-testing project — these are honest goals, not promises, and they'll shift based on real use and feedback (I'm learning as I build it):

- **Wider tool support.** Today it's Claude Code only. The aim is to adapt the workflow and rules to other AI coding tools and IDEs (e.g. Cursor, Codex, and others) where the formats differ — Claude Code uses `SKILL.md` + hooks; other tools use their own (`AGENTS.md`, rule files), so this is a port, not a copy.
- **Battle-testing.** Refine the heuristics (test-protection, model recommendation, audit logic) as real usage exposes false positives and gaps.
- **Smarter defaults.** Better complexity → model suggestions, and optional per-stack presets so less trimming is needed.
- **More review depth** where people actually want it, kept opt-in so nothing fires when it shouldn't.

If a goal here matters to you, open an issue or PR — feedback decides what gets built first.

## Notes

- **Skills vs hooks:** skills *follow* rules reliably; hooks *enforce* the two non-negotiable ones every time, even outside `/feature`.
- **Team scope:** to give a repo's team the `/feature` skill, copy it to that repo's `.claude/skills/feature/SKILL.md` and commit. Project skills override personal ones.
- **Limits, honestly:** the test-protect hook is a heuristic (can occasionally flag a legit refactor); the model recommendation is a judgment call; skills are reliable, not guaranteed. Tune to your stack as you use it.

## License

MIT — see [LICENSE](LICENSE).
