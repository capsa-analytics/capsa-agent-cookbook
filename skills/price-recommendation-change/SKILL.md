---
description: Draft or edit a Command Center price increase recommendation for one property — propose the exact change with capsa_prepare_price_recommendation_change (near-duplicate warnings included), get the user's explicit approval of that specific proposal, then save it with capsa_save_price_recommendation_change. Every save this skill makes stays a draft for a person to review, approve, or dismiss in Command Center — it never applies a price change itself. Use when a user wants to propose a price increase for a property, not just review one already on file.
---

# Price recommendation change

Propose a price increase recommendation, show the user exactly what will be
saved — including anything that overlaps an existing draft — and save only
the specific proposal they approve. Every recommendation this skill saves
stays a draft for a person to act on in Command Center.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

A price increase recommendation is a starting point for a manager's renewal
or pricing conversation, not a decision. This skill drafts or edits one
recommendation at a time: propose the change, show the user the
near-duplicate check and the exact before/after, and save only after they
approve that specific proposal — always leaving it as a draft for a person
to review.

The steps are the same whether this runs as an installed skill, is pasted
into another agent, or is run ad-hoc. The "Configuration" section lists the
inputs a run needs; persist them in the Team specifics block below, a system
message, or a wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected, the price-recommendations capability
  is available, and this connection has price-recommendation write access.
- The user wants to draft a new price increase recommendation or edit an
  existing **draft** one for one property.
- A property is named or already resolved.

Skip it if write access isn't enabled — say so plainly. Skip it too if the
user wants to review, approve, dismiss, or apply an existing recommendation:
none of those actions are available through this connector; they happen in
Command Center. If the recommendation the user wants to change is no longer
a draft (already reviewed, approved, applied, or dismissed), say so and
point them to Command Center or to creating a new recommendation instead.

## Required connected apps

- **Capsa MCP connector.** Supplies property resolution and both the
  prepare and save calls. This is a Capsa write, not outbound communication
  — no email or messaging connector is needed, and nothing here reaches the
  customer.

## Configuration

- **Property resolution.** A property ID, or a name/query for
  `capsa_search_properties`.
- **Scope conventions (optional).** Any team default for `scope_type`
  (defaults to the whole property when omitted) — ask rather than assume
  when the user's request implies a narrower scope (a specific
  division/service type/service/opportunity/contract) without naming the ID.
- **Pricing guardrails (optional).** If the team already has target margin
  or increase guardrails from [renewal-deep-dive](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/renewal-deep-dive/SKILL.md), the
  same numbers can inform the proposed percent or amount here — this skill
  itself doesn't compute a recommended number; it saves the one the user
  gives it.

## Workflow

### 1. Resolve the property

If the property isn't already identified, call `capsa_search_properties` and
confirm the match with the user — see
[Resolving ambiguous names](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/reference/patterns/resolve-ambiguous-names.md)
if more than one candidate comes back.

### 2. Check what's already on file

Look at the property's existing price recommendations —
`capsa_get_property_context`'s compact `price_increase_recommendations`
block, or the `planning_detail` drilldown for the full list. If the user
wants to change one that already exists, confirm its `id` and current
`status` here: **only a `draft` can be edited** through this skill.

### 3. Gather the exact fields with the user

Confirm: create or edit; which property; the scope (whole property, or a
specific division/service type/service/opportunity/contract — use an ID
already surfaced by a prior Capsa read, never a guess); `recommendation_type`
(`percent` or `dollar` — required on create, and determines which single
value field applies); the recommended percent or dollar amount; effective
year/month; and, if the user has them, target margin %, current margin %,
expected revenue delta, and a note. `recommended_percent` and the margin
percents are **display units** — 6 means 6%, never a decimal fraction.
Never invent a value, scope ID, or margin figure the user hasn't given you
or a prior Capsa read hasn't surfaced.

### 4. Prepare the proposal — no write yet

Call `capsa_prepare_price_recommendation_change` with the gathered fields.
This writes nothing. Take note of:

- `property.property_name` — hold onto this **verbatim**; needed unchanged
  for the save call's `write_confirmation.selected_property_name`.
- `proposal.proposal_token` — hold onto this **verbatim**; the save call
  must echo it back exactly.
- `proposal.expected_updated_at` — edits only; also echoed back unchanged.
- `proposal.current` / `proposal.proposed` / `proposal.field_changes` — the
  exact before/after, edits only. `proposed.status` always reads `draft`.
- `near_duplicates` — other non-dismissed recommendations on this property
  whose scope and timing overlap the proposed one.

### 5. Surface near-duplicates before anything else

If `near_duplicates` came back non-empty, present them first, each with the
`status` it actually carries. Only a `draft` can be edited through this
connector: for a draft, offer "there's already a draft recommendation for this
scope and year — want to edit that one instead?" For a recommendation that is
already reviewed, approved, or applied, say so plainly and point the user to
Command Center for any change to it — this recipe can only propose a new
recommendation alongside it. Let the user decide: switch to editing an
existing draft, proceed with the new one anyway, or adjust the fields and
re-prepare (a changed proposal needs a fresh prepare call).

### 6. Present the exact proposal for approval

Show the specific field values that will be saved — scope, type, the
percent or dollar value, effective timing, margins, expected revenue delta,
and note — not a paraphrase. For an edit, show the before/after diff
(`field_changes`) line by line. Tell the user plainly, before they approve:
**this always saves as a draft.** It does not notify the customer, does not
change any price in Aspire, and does not get reviewed, approved, or applied
by this skill — a person does that later in Command Center.

### 7. Save only after explicit approval

Once the user approves that exact proposal, call
`capsa_save_price_recommendation_change` with the same fields plus (edits
only) `expected_updated_at`, and:

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

State the saved `price_recommendation` plainly: id, scope, type, the percent
or dollar value, effective timing, margins, expected revenue delta, note,
and status (always `draft`). Remind the user it's saved as a draft for
review in Command Center — not sent anywhere and not yet in effect.

### 9. Handle a refusal without retrying blindly

A refusal names the reason: the recommendation being edited is no longer a
draft (already reviewed, approved, applied, or dismissed — a distinct
message per status), an exact duplicate already exists on create, a scope ID
didn't resolve to a valid label, or the edit changed since it was reviewed
(`expected_updated_at` stale — re-run prepare for a fresh one). Surface the
reason to the user and ask how they want to proceed; don't resubmit the same
request hoping it clears.

## Stop rules

- **Never save without the user's explicit approval of that exact prepared
  proposal.** A new or edited request needs a fresh prepare call — its
  `proposal_token` won't match an old approval.
- **Every save from this skill is a draft, permanently.** It never reviews,
  approves, dismisses, or applies a recommendation, and never notifies the
  customer. Say this before asking for approval, not after saving.
- **Only a draft can be edited.** A recommendation that's already reviewed,
  approved, applied, or dismissed must be reopened in Command Center or
  replaced with a new recommendation — never resubmit it as an edit here.
- **`recommended_percent` and the margin fields are display units.** 6 means
  6% — never divide by 100 or otherwise convert.
- **Never invent a scope ID, value, or margin figure.** Every scope ID is
  independently checked against Capsa's own data before it's accepted, but
  don't rely on that as a safety net — confirm with the user first.
- **Always surface `near_duplicates` before proceeding with a create.**
- **`expected_updated_at` must come from the immediately preceding prepare
  call for that same edit.** If the user pauses and returns later, re-prepare
  first.
- **Surface a refusal verbatim and stop — don't retry with different
  wording to route around it.**

## Example user prompt

> "Draft a 6% price increase for Greenleaf Corporate Campus for next year —
> margin's been under target for a couple of seasons."

## Example agent output (fictional)

```
Checked Greenleaf Corporate Campus: no existing draft recommendations for
2027, so this would be a new one, not an edit.

Proposed recommendation (new draft):
- Scope: whole property
- Type: percent — 6%
- Effective: 2027, no specific month
- Current margin: 31.2% · Target margin: 34.5% · Expected revenue delta:
  +$4,200
- Note: "Margin has been under target for two seasons."

This saves as a draft only — it won't notify the customer or change
anything in Aspire. A manager still reviews, approves, or dismisses it in
Command Center. Confirm and I'll save it?
```

After approval:

```
Saved as a draft. 6% price increase recommendation on Greenleaf Corporate
Campus, effective 2027, target margin 34.5%. Status: draft — still needs
review in Command Center.
```

All names, dollar figures, and dates above are fictional.

## Team specifics

<!--
  Persist any team convention for default scope_type and how the user
  typically supplies scope IDs and pricing guardrails here. Keep the steps
  and stop rules in sync with the cookbook; re-pull after a connector
  upgrade.
-->
