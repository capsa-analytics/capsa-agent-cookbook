# Contributing

This cookbook is two things in one repo: documentation of how agents use the
Capsa MCP connector with other connected apps, and a pack of installable skills
built from it. Contributing covers both — adding recipes and skills, **and**
keeping what's here in sync with the connector as it ships. New contributions are
welcome; the upkeep runbook below is as important as the authoring guidance.

## Document types

The cookbook has three altitudes. Know which you're writing:

- **Orientation** (`start-here.md`, `skills/capsa-orientation/`) — the briefing
  an agent reads (or installs) before anything else: the mental model, the
  universal loop, the safety contract, and example prompts. Rarely changes;
  changes here ripple everywhere.
- **Reference** (`reference/capabilities/`) — one page per capability, mirroring
  `capsa_describe_capability`. The comprehensive map; the connector's live output
  is the source of truth.
- **Patterns** (`reference/patterns/`) — always-on disciplines a skill invokes,
  like resolving a name to a dimension. Not end-to-end.
- **Workflows** (`skills/<name>/SKILL.md`) — end-to-end skills for a specific
  job. These compose the patterns and follow the structure below.
- **Machine index** (`index.json`, `llms.txt`) — the fetch-time map of the
  cookbook for agents arriving via `capsa_discover_playbooks`. Keep in lockstep
  with the files above.

## What a good recipe looks like

A recipe should:

- **Explain how an agent uses the Capsa connector to complete work.** The
  reader should be able to follow the recipe end-to-end without needing
  internal product knowledge.
- **Use fictional, generic examples.** Names, emails, companies, and dates
  in examples must not refer to real customers, prospects, or accounts.
- **Keep the user in the approval loop.** Any action that sends mail, edits
  external data, or otherwise leaves the agent's context should require
  explicit user approval first.
- **Treat completion recording carefully.** Record completion only after
  evidence the work actually happened — a draft, a plan, or an intent is
  not completion.

A recipe should not:

- Include secrets, tokens, internal URLs, or anything that wouldn't belong
  in customer-facing product documentation.
- Reference real customer data, real account names, or anything pulled
  from a private system.
- Describe Capsa's internal implementation, infrastructure, or storage —
  this cookbook is about how to *use* the connector, not how it's built.

## Workflow skill structure

Use the existing skills as a template — the `SKILL.md` body follows:

- Purpose (include a short note that the recipe is framework-agnostic and
  point readers at the Configuration section)
- When to use
- Required connected apps
- Configuration (the inputs a run needs, with optional persistence
  pointers — skill, system message, wrapper script). Include this even
  when most inputs vary session-to-session; the recipe should still name
  them in one place.
- Workflow (numbered steps)
- Stop rules
- Example user prompt
- Example agent output (fictional)

Keep recipes short. If a recipe is growing past a page or two, consider
splitting it.

## Keeping the cookbook current as Capsa ships

The cookbook tracks the connector. When the MCP changes, the docs and skills have
to follow — otherwise agents act on stale guidance. Two standing principles, then
a change-by-change runbook.

**Principles**

- **The connector's live output is the source of truth.** Anything the cookbook
  says about capabilities, tools, or dimensions should match what
  `capsa_describe_service`, `capsa_list_capabilities`, `capsa_describe_capability`,
  and the `capsa_list_*_filter_options` tools actually return.
- **Design discovery-first so docs degrade gracefully.** Prefer telling the agent
  to *discover* the current surface over hardcoding a list. A discovery-first
  skill keeps working when a capability is added; a hardcoded one silently lies.

**When something ships, update in this order** — orientation first, because teams
install and paste it, so stale guidance there propagates the furthest:

| What changed in the MCP | Update in the cookbook |
| --- | --- |
| **New capability** | `start-here.md` "things to try" + the `capsa-orientation` skill's capability list; a `reference/` capability page; `index.json` + `llms.txt`; a flagship skill if it warrants one. |
| **New tool on an existing capability** | Add the tool name to README's "Public MCP tools" **first** (CI flags any tool not listed there); then the capability's reference page and any skill/recipe that should use it. |
| **Dimension or filter added/renamed** | The [resolve-ambiguous-names](reference/patterns/resolve-ambiguous-names.md) dimension table, the orientation skill's dimension list, and the affected `reference/capabilities/` page(s). Re-verify the cross-capability naming map (e.g. "Sales Rep" vs "Account Owner"). |
| **Boundary or safety rule changed** (a capability gains a completion write, the freshness window moves) | The safety contract and stop rules in orientation and every affected recipe. Completion-write changes are highest-risk — "record only on evidence" depends on which capabilities can write. |
| **Tool or capability renamed/removed** | Search the whole repo for the old name; update or delete. Leave no dangling references or links. |

(`index.json` and `llms.txt` are the machine-readable map — update them whenever
you add or move a skill, capability, or pattern so the runtime-fetch path stays
accurate.)

**Verify against the live connector.** The authoritative diff is the MCP itself.
On each connector release — and on a periodic drift check even without one — run
`capsa_describe_service` / `capsa_list_capabilities` / `capsa_describe_capability`
/ `capsa_list_*_filter_options` and compare to what the cookbook claims. These
return live data, so **do the comparison privately and never paste real filter
values, IDs, or account names into committed files.** Document the *shape* with
fictional values.

**Keep installed copies un-stale.** Skills get installed and pasted *out* of this
repo, so downstream copies can't see your edit. Stamp orientation with the
connector version or date it was last verified against, tell users to re-pull
after a connector upgrade, and use absolute cookbook URLs inside skills (not
repo-relative paths) so installed copies don't break. When you ship skill
changes, bump `version` in `.claude-plugin/plugin.json` — plugin installs only
pick up updates when that version changes.

**Don't create internal drift.** Skills are self-contained and canonical for
workflows; `reference/` is canonical for capabilities; patterns are canonical for
cross-cutting disciplines. Where the same thing is necessarily restated (the loop
appears in both `start-here.md` and the orientation skill), pick one canonical
copy and keep the other a brief echo.

**A check enforces the basics.** `scripts/check_consistency.py` runs on every pull
request (the Consistency workflow) and asserts that every referenced tool is listed
in README, every capability and pattern is in `index.json` and on disk, skills
carry a `description`, and all internal links resolve. Run it before opening a PR:
`python3 scripts/check_consistency.py`.

**Safety review still applies.** Keep-current edits often touch dimension names and
examples — exactly the real-data-adjacent surface. Every change still goes through
the public-safety review; keep examples fictional and live values out.

## Submitting changes

Open a pull request with a clear description of:

- the workflow the recipe covers,
- the connectors it expects,
- anything reviewers should look at closely.

We review for clarity, safety (user approval, no invented data), and that
examples stay fictional.
