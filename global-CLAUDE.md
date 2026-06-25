# >>> claude-code-kit global rules >>>
# Universal personal preferences — apply in every project and every session.
# Keep this block short. Project-specific rules belong in the project's own CLAUDE.md.

- Start files with code. Never add a descriptive header/banner comment block at the top of a new or edited file (no "This file does X / ported from Y / scoped as Z"), and never write comments that narrate the change ("logic unchanged, only markup redesigned", "refactored to…", "updated per request"). That belongs in the commit message and git history. Comment only where a specific line is genuinely non-obvious.
- Commit messages: write them as a human engineer would. Never mention Claude, AI, an assistant, or which model was used; no "Generated with…" footer; no co-author trailer.
- When a requirement, file, value, or behavior is unclear, ask a specific question rather than guessing or inventing it.
- Prefer the simplest change that fully solves the problem. Don't over-engineer or add abstractions the task doesn't need.
# <<< claude-code-kit global rules <<<
