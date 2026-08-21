---
description: Build or evolve a property's forward-looking plan with the user — target outcomes, planned work by season/quarter, budget notes, and client conversations needed — grounded in Capsa's property context (health, satisfaction, planning, pipeline) and any existing future-plans notes. On the user's explicit approval, save the plan as a Command Center property note flagged for future plans. Use when a user wants to write down or update where a property is headed, not just what already happened.
---

# Property plan builder

Turn a planning conversation into a durable, evolving plan for one property.
Pull the property's full picture — health, satisfaction, relationship status,
planning signals, and pipeline — surface any plan already on file, then draft
the next version of the plan with the user. Only after the user approves the
exact text does it get saved back to Capsa as a Command Center property note
flagged for future plans, so the next person who opens the property sees the
latest thinking instead of starting from scratch.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Plans for a property — what to push for next season, what to raise at the
next client conversation, where budget is headed — tend to live in someone's
head or a scattered note, and get rebuilt from memory every time someone
revisits the account. Capsa now has a place for this: a property note flagged
"future plans" that `capsa_get_property_context` returns back on the next
pull, so a plan can evolve instead of being reconstructed each time. This
skill is the workflow for that: read the full picture, read what's already
been planned, draft the next version with the user, and save only the text
they approve.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section lists the inputs a
run needs; persist them in the Team specifics block below, a system message,
or a wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the `property_context` capability
  is available (check `capsa_describe_capability` if unsure).
- The user wants to build or evolve a forward-looking plan for one property —
  not a status update on what already happened (that's
  [property-site-update](../property-site-update/)) and not a single ad-hoc
  data question.
- A property is named, or there's enough contact context to resolve one.

Saving the plan also needs the `command_center_notes` capability's note-write
permission, but don't skip the recipe for lack of it — draft the plan either
way, and only the save step (4) is affected; see Stop rules. Skip this recipe
entirely if `property_context` itself isn't enabled; ask the user to enable it
first.

## Required connected apps

- **Capsa MCP connector.** Supplies property resolution, single-property
  context (including any existing future-plans notes), the drilldowns this
  recipe reads from, and — when the note-write permission is enabled — the
  save step via `capsa_create_command_center_note`.

This recipe has no send step. The plan note it saves is internal to Capsa, not
customer-visible, so no email or messaging connector is required. If the user
wants part of the plan communicated to the property manager, that's a separate,
explicit follow-through — step 5 below — never something this recipe does on
its own.

## Configuration

The inputs a run needs. Most vary session-to-session, so leaving them
runtime-only is fine.

- **Property.** A property ID, a name/query for `capsa_search_properties`, or
  a contact (email or name) for `capsa_find_properties_by_primary_contact`
  when there's no property named yet.
- **Planning horizon (optional).** How far out the plan should look — next
  quarter, next season, the rest of the contract term. Ask if the user doesn't
  say; don't assume a default.
- **Dollar/budget visibility (optional).** Default: include budget notes and
  price-recommendation context freely — this note is internal-only, not a
  customer draft. Ask only if the user wants figures left out of the saved
  note for some other reason.
- **Aspire property-note append (optional).** `capsa_create_command_center_note`
  supports `append_to_aspire_property_note`. Default off — use it only when the
  connection has it ready and the user asks, same discipline as
  [meeting-notes-to-command-center](../meeting-notes-to-command-center/).

## Workflow

### 1. Resolve the property

If a property is named, call `capsa_search_properties` to find the exact
match — see
[Resolving ambiguous names](../../reference/patterns/resolve-ambiguous-names.md)
if more than one candidate comes back. If starting from a contact instead, call
`capsa_find_properties_by_primary_contact` and apply the same
corroborate-before-trusting discipline
[property-site-update](../property-site-update/) and
[meeting-notes-to-command-center](../meeting-notes-to-command-center/) use: a
lone match isn't proof of uniqueness, and a property hint only ranks
candidates — it never filters them. Present every candidate and let the user
choose; never guess a property before drafting or saving a plan.

### 2. Read the full picture — including what's already planned

Call `capsa_get_property_context` with the resolved `property_ids: [id]`.
This returns the `health` block (`status`, `summary`, and — when present — a
standing recommendation with a plain-English `explanation`), `satisfaction`
(open and recent complaint/issue counts), `relationship_status` (active
contract, construction, or renewal timing), a planning summary, a compact
`property_card` (`brief` and `whats_changed`), and the `future_plans` block —
the notes already flagged for future plans on this property: note text,
created date, author name, and a `total_available` count, capped, with its own
freshness note. **Read `future_plans` before drafting anything.** It may
legitimately come back as an honest "not available yet" block on connections
pending upgrade — treat that as a real answer, not an error, and say so
plainly rather than treating the property as plan-free.

Pull drilldowns for whatever the compact context doesn't cover, one call at a
time via `capsa_get_property_context_drilldown` (exactly one `property_id` and
one `drilldown_id` per call):

- **Full narrative** — `property_card` for the complete picture beyond the
  compact `brief`/`whats_changed` (activity digest, emerging risks, open
  opportunities, client priorities).
- **Budget and pricing** — `planning_detail` for budget items and price
  recommendations to ground the plan's budget notes.
- **Pipeline context** — `delivered_proposals` and `proposed_opportunities`
  for what's already in motion, so the plan doesn't duplicate or contradict
  open pipeline.

Most property data may be up to 24 hours old; `property_card` narrative
sections are nightly-generated with their own per-section `as_of` date. The
`future_plans` block is called out as a live read at call time — carry each
block's real freshness forward distinctly rather than treating the whole
context as one snapshot age.

### 3. Draft the plan with the user

Write a concise narrative plan: target outcomes, planned work by
season/quarter, budget notes, and client conversations that still need to
happen. Ground every line in what the reads in step 2 showed or what the user
says in this conversation — nothing else. Keep the two sources distinguishable
in the draft itself (e.g. "data says the last recommendation flagged margin
below target" vs. "you said the client wants to phase in the irrigation
upgrade next spring") so the user can tell which parts are evidence and which
are their own judgment when they review it.

If `future_plans` came back with existing notes, don't draft a fresh plan that
ignores them. Propose an **updated** plan that explicitly references what
changed or carried forward from the prior version — supersede it, don't
duplicate it next to it.

### 4. Save only on explicit approval

Once the user approves the exact text, save it with
`capsa_create_command_center_note`:

- `property_id` = the confirmed property's id;
- `note` = the approved plan text, exactly as approved — no silent edits after
  the fact;
- `add_to_future_plans = true` so it lands in the `future_plans` block the next
  read returns;
- `write_confirmation.confirmed_by_user = true`, plus `summary`,
  `selected_property_id`, and `selected_property_name` matching the confirmed
  property — the connector rejects the write if these don't match, exactly as
  documented in
  [Command Center notes](../../reference/capabilities/command-center-notes.md).
- `append_to_aspire_property_note = true` only when the connection has it ready
  and the user asked for it in Configuration.

**One note per plan revision.** If the plan is long, keep it as one coherent
note — don't chunk a single plan across multiple saved notes; that fragments
`future_plans` for the next reader instead of giving them one current version.

### 5. Offer the optional follow-through — never send from here

After saving (or after handing off the drafted brief, if it wasn't saved),
offer to hand relevant parts of the plan to
[property-site-update](../property-site-update/) for a customer-safe update to
the property manager. Say plainly that the plan note itself is internal by
default — it is **not** customer-visible — so nothing about it reaches the
customer unless the user separately runs that recipe and approves a
customer-safe draft from it. This recipe's job ends at the save (or the
document handoff); it never drafts or sends a customer-facing message itself.

## Stop rules

- **Never save without explicit approval of the exact text.** Approval of an
  earlier draft, or of the general direction, doesn't cover a version with
  further edits — reconfirm before calling
  `capsa_create_command_center_note`.
- **Never invent data.** Every fact in the plan must trace to a specific
  property-context field, drilldown, or something the user said in this
  conversation — labeled as such. If a read doesn't show it and the user
  didn't say it, it doesn't go in the plan.
- **Surface existing plans before drafting.** Read `future_plans` in step 2
  before writing anything; propose an update that supersedes prior plans
  rather than a duplicate that leaves two conflicting versions on file.
- **The plan note is internal.** Nothing in this recipe sends anything to the
  customer — the note is not customer-visible, and step 5's follow-through is
  a separate, explicitly approved recipe, not an automatic next step.
- **Handle "not available yet" and disabled writes honestly.** If
  `future_plans` comes back as the connector's honest "not available yet"
  state, or the note-write permission isn't enabled for this connection, say
  so plainly — don't retry, don't fake a save, and don't imply the plan is
  saved when it isn't. Offer the drafted plan as a document (chat output, or a
  connected docs tool if available) instead, and continue from there once
  writes are available.
- **Respect each block's as-of date.** Carry real freshness markers forward —
  property data can be up to 24 hours old, `property_card` narrative is
  nightly-generated per section, and `future_plans` is a live read — never
  present any of it as "as of right now" without checking.
- **Log what the connector can't answer — with consent.** If the user needs
  planning context the `property_context` capability doesn't provide, offer to
  record the gap with `capsa_log_feature_request`; log a concise, redacted
  description only after the user agrees, per
  [capsa-orientation](../capsa-orientation/) loop step 5.

## Example user prompt

> "Let's build out the plan for Maple Ridge HOA for the rest of the year —
> pull what we know and let's work through it together. I'll tell you what I
> want to add."

## Example agent output (fictional)

```
Pulled context for Maple Ridge HOA (active contract, Northgate branch).

WHAT'S ALREADY ON FILE

- One future-plans note on record (saved 2026-05-02, Sam Lee): "Push irrigation
  upgrade conversation before summer; watch margin on turf program." That's the
  plan we'd be evolving, not replacing.

WHAT THE DATA SHOWS

- Health: yellow — "Irrigation complaints trending up; renewal at risk"
  (reviewed 2026-08-01). Standing recommendation: red — Gross Margin % 18%
  (threshold 25%).
- Satisfaction: 1 open complaint, 3 open issues.
- Planning detail: irrigation upgrade budget item logged at $14,200 (no price
  recommendation attached yet); turf program flagged for a price review.
- Pipeline: 1 delivered proposal (irrigation repair, no decision yet), 0
  proposed opportunities.

DRAFT PLAN (rest of 2026)

  Target outcome: get the irrigation upgrade approved and margin back above
  threshold before the winter slowdown.

  - Q3: close the outstanding irrigation repair proposal; use it to open the
    upgrade conversation the prior plan flagged. (Carried forward from the
    May plan — still open.)
  - Q3/Q4: run the turf program price review the planning data is flagging;
    you told me the client has already hinted they'd accept a modest increase
    if it comes with a service change, so lead with that framing.
  - Ongoing: watch the open complaints — three open is above what we'd want
    heading into a renewal conversation.
  - Client conversation needed: irrigation upgrade budget ($14,200 logged) —
    not yet discussed with the client per the notes on file.

Does this read right, and is the "client hinted at accepting an increase"
detail accurate the way I've framed it? Once you confirm the text, I'll save
it to Maple Ridge HOA as the new future-plans note (this supersedes the May
note, not adds alongside it).

---

Saved. New future-plans note on Maple Ridge HOA, replacing the working
context of the May 2026 note with this version.

Want me to pull the property-site-update recipe next and see what, if
anything, from this plan is worth surfacing to Jordan at the property? The
plan note itself stays internal either way.
```

All names, emails, dollar figures, and dates above are fictional.

## Team specifics

<!--
  Persist your default planning horizon, whether budget/pricing figures are
  ever excluded from the saved note, and whether the Aspire property-note
  append is allowed on your connection here. Keep the steps and stop rules in
  sync with the cookbook; re-pull after a connector upgrade.
-->
