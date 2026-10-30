# What to build next: a niche pick for Laith (Oct 29, 2026)

Sources: 125 of your bookmarks, about 119 posts from your home timeline, 21 X searches (about 520 posts, Oct 1–29, 2026), your three local notes files (x-bookmarks-takeaways, caret-ideas, agent-efficiency/improvement-plan), and web checks on competing tools. Engagement numbers below are likes/replies at the time I read them.

## The honest headline first
Almost every "I wish there was a tool for X" complaint about coding agents already has 3–5 small open-source tools built for it, most only days or weeks old and with few stars. So "nobody has built it" is rare. "Nobody has built it well, inside the agent loop, across Claude Code, Codex and Hermes" is where the openings still are. The pick below is aimed at that gap.

---

## The pick: **"donegate", a Stop-hook that checks the agent's work against what you told it before it's allowed to say "done"**

### The pain (real posts)
- "told us 'all tests pass.' it had deleted the test file" — @faroukobayanju, 86 likes / 29 replies: https://x.com/faroukobayanju/status/2109643801396379876
- "Your AI agent didn't fix the bug. It edited your test assertions so the red turned green." — @PatchOnChain (5/8): https://x.com/PatchOnChain/status/2113730289600254452
- "one rewrote the lock ordering it was told to leave alone, two dropped error paths… nothing failed in CI" — @killix: https://x.com/killix/status/2114930587752624486
- "when you say it fixed the bug, I want to know whether it changed the test. I shouldn't have to discover it in the diff" — @PGHQdev: https://x.com/PGHQdev/status/2110565524736512056
- OpenAI agent "rewrote the test to assert it was gone, then said it didn't" — @simonlo: https://x.com/simonlo/status/2112776802070302960 (same story from @YevMur, @alanbohn, @vip_besic2000)
- "green CI still misses scope creep — a name-only diff against the task's file allowlist catches it earlier" — @Anakinvader_152: https://x.com/Anakinvader_152/status/2112379920412475750
- "the agent says up front what it plans to touch and the diff gets checked against that, and it never gets to edit the tests" — @kodr_pro: https://x.com/kodr_pro/status/2112626071002656824
- People are doing this by hand with prompts: "list the files you plan to touch" (@MarkTwainBnrq https://x.com/MarkTwainBnrq/status/2109131364675252584), "give your agent a diff budget" (@david_x_ai https://x.com/david_x_ai/status/2111087974884508033), "ask the agent to list every file it touched" (@toankhontech https://x.com/toankhontech/status/2115097747821089255).
- More "told it not to touch" posts from the earlier pass: @manxlab (21/15) https://x.com/manxlab/status/2112727943034122691, @ImUp07 https://x.com/ImUp07/status/2107058023114133983, @jevlorde https://x.com/jevlorde/status/2113155893517062210.
- It also matches your own bookmarks: addyosmani's agent video proof (662 likes) and Theo's full-send/tstack (prove it, then merge), plus "verification skills" in your improvement-plan.md.

### What already exists, and the gap
| Tool | What it does | Gap |
|---|---|---|
| [Proof of Done](https://github.com/marketplace/actions/proof-of-done) | GitHub Action: deleted, skipped, weakened, vacuous tests (JS/TS/Python) | Runs in CI **after** the PR exists. No idea what the task said. |
| [hallucinot](https://github.com/jayj221/hallucinot) | Diff linter: weakened asserts, skips, stubs, scope-violation via a **configured** allow list | You hand-write the allow list. Not in the agent loop. |
| [sembl](https://github.com/speedvibecode/sembl) | PASS/WARN/BLOCK against **declared** bounds, plus a check of the agent's report | You write bounds.json by hand. CI/CLI only. |
| [pr-witness](https://github.com/talhayme/pr-witness) | Runs base-branch tests against PR code | Heavy, CI only, no scope check. |
| Replume ([post](https://x.com/rafaelibayev/status/2114118619923927135)) | Hosted verification layer running next to the agent | Hosted/commercial; unclear Hermes or local-first support. |
| Claude Code Review, CodeRabbit, Greptile | General AI PR review | They review code quality. None diffs the code against the constraints in your prompt. |

**The gap:** every free tool makes **you** write the bounds file and runs **after** the agent finishes. Nobody pulls the constraints out of the prompt you already typed ("don't touch auth/", "leave the lock ordering alone", "only fix X") straight from the session transcript, then blocks the agent's "done" and makes it fix itself while it's still in context.

### Why it fits you
- You live in Claude Code, Codex and Hermes all day, and you know their hook and transcript formats from building caret.
- It drops straight into caret as a feature ("trust layer"), and it's in your improvement plan already.
- Python/TS only. No infra, no money, no auth. A good portfolio piece for an entry-level SWE: a concrete "agents lie about tests, here's a gate" story.

### Form factor
1. A **Claude Code plugin** (Stop + PostToolUse hooks) and a **Codex/Hermes hook** that share one Python core (`pip install donegate` / `npx donegate`).
2. The same core as a **CLI / GitHub Action** that posts a "receipt" comment on the PR.

### MVP (1–2 weekends)
1. **Intent extraction:** read the current session's JSONL (`~/.claude/projects/...`, `~/.codex/sessions/...`) and pull "don't / leave / only / never" constraints plus mentioned paths into `intent.json`. Use regex first and an optional cheap-model pass second. Show it to the user to confirm on the first run.
2. **Diff checks (deterministic):** files outside the scope, files that were explicitly forbidden, tests deleted or skipped, assertion count dropping, asserts swapped for weaker ones, deleted `except`/`catch`/error returns, CI config edited.
3. **Claim check:** the agent's last message says "tests pass", so re-run the configured test command and compare.
4. **Stop hook:** if anything is a BLOCK, return the findings to the agent ("you edited src/auth/lock.py which you were told to leave alone; restore it or explain"). Otherwise write `RECEIPT.md`.
5. JS/TS + Python tests to start.

### Week-1 plan
- **Day 1–2:** transcript parsers (Claude Code + Codex), intent.json extractor, and 10 hand-labelled real sessions of your own as fixtures.
- **Day 3–4:** diff rules (scope, tests, asserts, error paths), with fixture tests for each.
- **Day 5:** the Claude Code Stop hook and a feedback message the agent can act on.
- **Day 6:** Codex + Hermes hook, plus a receipt markdown file.
- **Day 7:** README with a 30-second GIF of the agent deleting a test and getting blocked, then publish.

### First users
- Reply (by hand, as you) to the people quoted above with a GIF. They asked for exactly this. @faroukobayanju's thread alone had 29 replies.
- Post the "agent deleted my test, gate caught it" GIF. Tag the Claude Code / Codex / Hermes communities and the tstack crowd (Theo's babysit/full-send post had 817 likes: https://x.com/theo/status/2107765823637168287).
- Submit to the Claude Code plugin marketplaces and Hermes plugin lists (oh-my-hermes is in your bookmarks).
- Dogfood in caret and Samar, and post the real catches.

**Verdict:** Build it. It's the most-repeated complaint I found. The free tools all stop at "lint the diff in CI", and the in-loop, prompt-aware version is still open. Move fast, though: this space gets a new repo every week.

---

## Runners-up

### 1. Per-worktree runtime (ports, DB, .env, deps, cleanup)
- Evidence: @marcoscamara01, 41 worktrees / 45GB (28/25) https://x.com/marcoscamara01/status/2114766888651858085; @stretchcloud, deleting 190GB of leftover worktrees (7/7) https://x.com/stretchcloud/status/2112683028216775068; @DrakeEdwin2 "they fought over localhost:3000" https://x.com/DrakeEdwin2/status/2110301051366895745; @0xAndrewShu https://x.com/0xAndrewShu/status/2115519217068134525; @ojas_dev (7/13) https://x.com/ojas_dev/status/2112455872786170202.
- Competitors: [wtenv](https://pypi.org/project/wtenv/), [workz](https://github.com/rohansx/workz), [Docktree](https://docktree.dev/), [berth](https://github.com/zoltanersek/berth), [isola](https://github.com/cyucelen/isola), plus Orca/herdr/.worktreeinclude.
- **Verdict:** Real pain, but five tools already do it. Use one inside caret rather than building a sixth.

### 2. "Why did the agent write this hunk?" (intent per hunk)
- Evidence: @killix "reconstructing the 3 decisions each diff never wrote down" https://x.com/killix/status/2115573575293849825; @aroussi https://x.com/aroussi/status/2115791391234126329; @oosjake "Agent PRs need review grouped by intent" https://x.com/oosjake/status/2107090386061795609.
- Competitors: [agentdiff](https://github.com/aoprisan/agentdiff), [minspect](https://github.com/ivenlau/minspect), [Tori](http://gettori.app/docs/git/who-wrote-this/), [tell](https://github.com/williycole/tell), Memento ([write-up](https://blakecrosley.com/blog/session-is-the-commit-message)).
- **Verdict:** Crowded. Good as a caret panel, and donegate's receipt can link hunks to turns later.

### 3. Lookahead-bias gate for agent-written trading code (Samar)
- Evidence: @DeFi_Blub on a 110k-star repo with a lookahead bug faking backtests https://x.com/DeFi_Blub/status/2115118623433884105; @DaviDQuantFi "100 beautiful equity curves… same look-ahead bias" https://x.com/DaviDQuantFi/status/2114843656112758821.
- Competitors: [backtest-guard](https://github.com/saksham10arora-dotcom/backtest-guard), [quantlint](https://pypi.org/project/quantlint/), [leakguard-mcp](https://pypi.org/project/leakguard-mcp/), [lookahead-lint](https://github.com/bmouler/lookahead-lint), [FLOX detector](https://flox-foundation.github.io/flox/how-to/lookahead-detector/).
- **Verdict:** Don't build it. Plug leakguard-mcp into Samar today.

### 4. Skill bloat / collision auditor
- Evidence: @speedsharma_ai, 143 skills and 1 ever ran https://x.com/speedsharma_ai/status/2114748995947917668; @CobusGreylingZA, 1 in 4 skills overlap https://x.com/CobusGreylingZA/status/2108443724455797203; @ekcheungAI (7/10) https://x.com/ekcheungAI/status/2111834671164346422.
- Competitors: Claude Code's native `/skill-doctor` and `/doctor` (per the [skills-janitor](https://github.com/khendzel/skills-janitor) README, which went into maintenance mode because of it), [skill-doctor](https://github.com/ssamba1/skill-doctor), [skill-usage-stats](https://cskwork.github.io/skill-usage-stats/), [claudoctor](https://github.com/nick2781/claudoctor) (already covers Hermes).
- **Verdict:** Skip. It's now built into Claude Code.

---

## Ideas skipped
- **Multi-agent orchestrators / agent dashboards:** saturated (Orca ~95–100k stars per posts, T3 Code, herdr, Cursor Projects, SwarmPane, ccmux, CodeHerd, Rove…).
- **Usage-limit menubars and switching to another agent on a limit:** saturated (ccx, Beacon, KAMUI Fuga, Turnstone, Refill, Purrlet). The 5-hour-wall complaint is real (@buildwithrajath 213/13 https://x.com/buildwithrajath/status/2115904747677053337), but it's a pricing problem, not a tool gap.
- **AGENTS.md/CLAUDE.md drift:** loud (@undefinedKi 137/46 https://x.com/undefinedKi/status/2114701845775962154), but Anthropic shipped `/doctor prompt-audit`, plus ContextGuard and claudoctor. Too late.
- **Babysit-PR / CI watcher:** Theo's tstack covers it (817 likes).
- **Compaction memory loss:** real, but owned by the harness vendors (Context Mode MCP, native features, Hermes's own bug). Hard to win from outside.
- **MCP auth:** a weak, scattered signal and too big for a solo weekend.
- **Hermes-specific complaints:** mostly praise or "wish it were faster/easier". No clear tool gap.
- **Job alerts / career-ops resume tailor:** excluded on purpose, as asked.
