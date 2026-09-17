---
description: Create or edit a Command Center budget item for one property — check what's already on file, propose the exact change with capsa_prepare_budget_item_change (near-duplicate warnings included), get the user's explicit approval of that specific proposal, then save it with capsa_save_budget_item_change. A saved budget item is live in Command Center planning immediately, not a draft. Use when a user wants to add or change a property's budget line, not just look at what's already saved.
---

# Budget item change

Propose a budget item change, show the user exactly what will be saved —
including anything that looks like a duplicate — and save only the specific
proposal they approve.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Budget items have no unique constraint in Capsa, so it's easy to accidentally
create a second line that overlaps an existing one instead of refining it.
This skill puts a review step in front of every save: prepare the change,
show the user the near-duplicate check and the exact before/after, and only
call the save tool after they approve that specific proposal.

The steps are the same whether this runs as an installed skill, is pasted
into another agent, or is run ad-hoc. The "Configuration" section lists the
inputs a run needs; persist them in the Team specifics block below, a system
message, or a wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected, the budget-planning capability is
  available, and this connection has budget-item write access.
- The user wants to add a new budget item or change an existing one for one
  property — not just view what's already saved (use
  `capsa_get_property_context`'s `planning_detail` drilldown for that, no
  write skill needed).
- A property is named or already resolved.

Skip it if write access isn't enabled for this connection — say so plainly
and offer to show the user what's currently saved instead of pretending the
save step will work.

## Required connected apps

- **Capsa MCP connector.** Supplies property resolution, the existing budget
  items to check against, and both the prepare and save calls. This is a
  Capsa write, not outbound communication — no email or messaging connector
  is needed.

## Configuration

- **Property resolution.** A property ID, or a name/query for
  `capsa_search_properties`.
- **Scope conventions (optional).** Any team default for `scope_type`
  (defaults to the whole property when omitted) and `category` (defaults to
  `total`) — ask rather than assume when the user's request implies a
  narrower scope (a specific division, service type, service, opportunity,
  or contract) without naming the ID.

## Workflow

### 1. Resolve the property

If the property isn't already identified, call `capsa_search_properties` and
confirm the match with the user — see
[Resolving ambiguous names](../../reference/patterns/resolve-ambiguous-names.md)
if more than one candidate comes back.

### 2. Check what's already on file

Before proposing a create, look at the property's existing budget items —
`capsa_get_property_context`'s compact `budget_items` block, or the
`planning_detail` drilldown for the full list. This is how you catch the
canonical case: a broad item already covers the scope the user is describing
and should be **edited**, not duplicated. If an existing line plausibly
covers the same thing the user is describing, say so and ask whether they
want to refine it instead of creating a new one.

### 3. Gather the exact fields with the user

Confirm, in plain terms: create or edit; which property; the scope (whole
property, or a specific division/service type/service/opportunity/contract —
get the matching ID from context you've already pulled, never guess one);
budget year and month (or none, for an annual line); category; amount; and
any note. Never invent an amount, year, or ID the user hasn't given you or a
prior Capsa read hasn't surfaced.

### 4. Prepare the proposal — no write yet

Call `capsa_prepare_budget_item_change` with the gathered fields. This writes
nothing. Take note of:

- `property.property_name` — hold onto this **verbatim**; you'll need it
  unchanged for the save call's `write_confirmation.selected_property_name`.
- `proposal.proposal_token` — hold onto this **verbatim**; the save call
  must echo it back exactly.
- `proposal.expected_updated_at` — edits only; also echoed back unchanged.
- `proposal.current` / `proposal.proposed` / `proposal.field_changes` — the
  exact before/after, edits only.
- `near_duplicates` — other active items on this property that look like the
  same thing, with `match_reasons` (`same_scope` and/or `similar_name`).

### 5. Surface near-duplicates before anything else

If `near_duplicates` came back non-empty, present them **first**: "this
looks like line X — want to edit that one instead?" Let the user decide:
switch to editing the near-duplicate, proceed with the create anyway, or
adjust the fields and re-prepare (a changed proposal needs a fresh prepare
call — an old `proposal_token` won't match a modified request).

### 6. Present the exact proposal for approval

Show the specific field values that will be saved — not a paraphrase. For an
edit, show the before/after diff (`field_changes`) line by line. Tell the
user plainly, before they approve: **a confirmed save is live in Command
Center planning immediately** — there is no draft or pending state for
budget items, unlike price recommendations.

### 7. Save only after explicit approval

Once the user approves that exact proposal, call
`capsa_save_budget_item_change` with the same fields plus (edits only)
`expected_updated_at`, and:

```json
{
  "write_confirmation": {
    "confirmed_by_user": true,
    "summary": "one line describing what the user approved",
    "selected_property_id": 12345,
    "selected_property_name": "the property.property_name value from step 4, verbatim",
    "proposal_token": "the proposal_token value from step 4, verbatim"
  }
}
```

### 8. Report the saved result

State the saved `budget_item` plainly: id, item name, scope, year/month,
category, amount, note, status, and `client_approval` (always "Awaiting
client" on a fresh create — this tool never sets client approval; that's a
person's action in Capsa). It is saved and live now — don't describe it as
pending review.

### 9. Handle a refusal without retrying blindly

A refusal names the reason: the item's client already approved it, its
renewal plan is approved internally, the target year/division lane is
already approved internally, the edit changed since it was reviewed
(`expected_updated_at` stale — re-run prepare for a fresh one), or a scope ID
didn't resolve to a valid label. Surface the reason to the user and ask how
they want to proceed; don't resubmit the same request hoping it clears.

## Stop rules

- **Never save without the user's explicit approval of that exact prepared
  proposal.** A new or edited request needs a fresh prepare call — its
  `proposal_token` won't match an old approval.
- **A confirmed save is live immediately.** Say this before asking for
  approval, not after saving. Never call a saved budget item a "draft."
- **Never invent a scope ID, amount, or year.** Every scope ID is
  independently checked against Capsa's own data before it's accepted, but
  don't rely on that as a safety net — confirm with the user first.
- **Always surface `near_duplicates` before proceeding with a create.**
- **This tool never touches client approval.** If the user wants something
  marked client-approved, that happens in Capsa, not through this skill.
- **`expected_updated_at` must come from the immediately preceding prepare
  call for that same edit.** If the user pauses and returns later, re-prepare
  first.
- **Surface a refusal verbatim and stop — don't retry with different
  wording to route around it.**

## Example user prompt

> "Greenleaf Corporate Campus has a broad mulch budget line for next year —
> can you set it up for May with the right service type instead?"

## Example agent output (fictional)

```
Checked Greenleaf Corporate Campus's budget items: there's one active 2027
line, "Mulch," scoped to the whole property, $12,000, no month set. That
matches what you're describing — I'll propose editing it rather than
creating a new one.

Proposed change (edit, not a new item):
- Scope: whole property -> Landscaping Enhancements service type
- Budget month: (none) -> May
- Item name, year, and amount unchanged: "Mulch," 2027, $12,000

Heads up: once you approve this, it saves immediately to Command Center
planning — there's no draft step. Confirm and I'll save it?
```

After approval:

```
Saved. Mulch — Greenleaf Corporate Campus, 2027, May, Landscaping
Enhancements, $12,000. Client approval: Awaiting client (unchanged — that's
recorded in Capsa by a person, not through this).
```

All names, dollar figures, and dates above are fictional.

## Team specifics

<!--
  Persist any team convention for default scope_type/category and how the
  user typically supplies scope IDs (from a prior context pull vs. named
  directly) here. Keep the steps and stop rules in sync with the cookbook;
  re-pull after a connector upgrade.
-->
