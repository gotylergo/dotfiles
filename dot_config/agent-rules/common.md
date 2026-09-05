# Shared agent rules

Cross-tool rules consumed by every agent (Claude Code, OpenCode, Antigravity).
Edit this file once; each tool pulls it in via its own include mechanism.

## Commit & comment style
- Commit messages: one-line subject by default (keep each repo's emoji/prefix convention, e.g. gitmoji). Add a body only when intent isn't obvious — a single sentence or a few short bullets, never long multi-paragraph bodies.
- Comments: default to none. Add one only when the "why" isn't recoverable from the code — a non-obvious constraint, a workaround, an external quirk. Never narrate what the code does or use unnecessary numbered comments (e.g. `# 1. ...`); write direct explanations without fluff. One line where possible, two at most; if it needs more, the code needs better naming or a doc block instead. Section-header comments to break up a long function are fine.
- Split commits by concern: per-site/app-config changes separate from reusable code.

## Context management
- Delegate large reads to a subagent instead of reading them directly into the main session: files over ~500 lines, logs, or anything where only a small distilled answer is actually needed (e.g. "find the errors in this log," "summarize this doc"). The subagent's context absorbs the bulk; only its summary returns to the main session.
- Read directly (no subagent) when the content itself is the point — small/medium files being edited, code under active review, anything where you need the full text in context to act on it.
- When in doubt on a large file, default to delegating; the cost of an extra agent call is far smaller than a large blob permanently occupying the rest of the session's context.

## Token optimization (RTK)
- Prefix shell/CLI commands with `rtk` (`rtk git`, `rtk cargo`, `rtk npm`, `rtk pnpm`, `rtk docker`, `rtk test`, `rtk grep`, etc.) to filter and compress tool output before it enters context.
- Use `rtk gain` to check savings analytics and `rtk proxy <cmd>` if raw, unfiltered output is required for debugging.
