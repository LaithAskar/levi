You are building "Levi" (package and CLI name `levi`; SPEC.md calls it "donegate", which is the old working name, so use levi everywhere). Read SPEC.md, specifically the section "The pick", its MVP and its Week-1 plan. Ignore the runners-up.

Goal for this run: MVP steps 1 and 2 only.
1. Transcript parsers for Claude Code session logs (~/.claude/projects/**/*.jsonl) and Codex session logs (~/.codex/sessions/**/*.jsonl), and an intent extractor that pulls the user's stated constraints (allowed/forbidden files or dirs, "don't touch tests", "don't change CI", scope limits, claims like "tests pass") from them. Include small realistic fixture transcripts under tests/fixtures.
2. Deterministic diff rules, each a separate unit with at least one test: out-of-scope or forbidden file edits, deleted or skipped tests, fewer or weaker asserts, removed except/catch blocks, CI config edits. Support Python and JS/TS tests.

Do not build the Stop hook, Codex/Hermes hooks, plugin packaging, or README demo yet.

Constraints:
- Python 3, standard library only. No third-party dependencies.
- No code comments or docstrings.
- No features beyond what is listed above.
- Package layout: levi/ (core), tests/ (unittest).

Pass/fail: `python3 -m unittest` from the repo root passes, with at least one test per diff rule and tests for each parser and the intent extractor. Run it yourself and fix until it passes.

When done, commit your work on the current branch (mvp-1) with a clear message. Do not push.

Then start a fresh review: run `claude -p` in a new session (same model, --permission-mode acceptEdits) asking it to review the code against SPEC.md MVP steps 1-2 only, ignoring style, and to fix any gaps it finds, rerun `python3 -m unittest`, and commit. Write its review summary to REVIEW.md and commit that.
