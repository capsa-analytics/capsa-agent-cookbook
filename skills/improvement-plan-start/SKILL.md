---
description: Start a Command Center improvement plan for one property from an AI assistant — pick the goal and target with the user, propose the exact plan with capsa_prepare_improvement_plan, get the user's explicit approval of that specific proposal, then save it with capsa_save_improvement_plan. A saved plan is live in Command Center immediately, not a draft, and one open plan per property and goal is enforced. Use when a user wants to commit a property to a measurable goal (gross margin, penetration, close rate, days past due, open complaints, property health), not to write free-text notes about future plans.
---

# Improvement plan start

Turn "let's get this property's late A/R under control" into a real,
measurable Command Center plan — the goal, the target, the date, the owner —
proposed first, saved only after the user approves that exact proposal.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Command Center improvement plans are how a team commits a property to a
specific, measurable outcome: gross margin, penetration, close rate, days
past due, open complaints, or property health. A plan carries its own
baseline (Capsa measures it at save time), a target, a date, and an owner,
and it is live the moment it is saved. This skill is the workflow for
creating one through the connector without surprises: agree the goal and
target with the user, prepare the proposal, show it back verbatim, save only
on explicit approval, and report what Capsa actually stored.

This is different from the **property-plan-builder** skill, which drafts a
property's free-text *future plans* note. Use that one for narrative
planning; use this one when the user wants a measurable goal Capsa will
track.

The steps are the same whether this runs as an installed skill, is pasted
into another agent, or is run ad-hoc. The "Configuration" section lists the
inputs a run needs; persist them in the Team specifics block below, a system
message, or a wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected, the improvement-plans capability is
  available, and this connection can create plans (the "Create plans"
  permission in Administration → AI Connectors).
- The user wants to commit a property to a measurable goal — not just read
  the plans already open (`capsa_list_improvement_plans` /
  `capsa_get_improvement_plan` need no write permission).
- A property is named or already resolved.

Skip it if plan creation isn't enabled for this connection — say so plainly
and offer to list the property's existing plans instead of pretending the
save step will work. Editing or closing an existing plan happens in Command
Center, not through the connector.

## Required connected apps

- **Capsa MCP connector.** Supplies property resolution, the existing plans
  to check against, and both the prepare and save calls. This is a Capsa
  write, not outbound communication — no email or messaging connector is
  needed.

## Configuration

- **Property resolution.** A property ID, or a name/query for
  `capsa_search_properties`.
- **Goal vocabulary.** Six objectives: `gm_pct` (gross margin),
  `penetration_pct`, `close_rate_pct`, `ar_days_past_due`, `complaints`
  (open complaints), `property_health`. The first three measure a period
  (they take `plan_start_on` through `target_date`); the last three use an
  achieve-by `target_date` alone. `target_value` is a percent, a number of
  days, a whole number of complaints, or — for property health — the band to
  reach (`green`, `yellow`, `red`).
- **Baseline window.** `baseline_preset` defaults to `custom`, which needs
  `baseline_start_date` and `baseline_end_date`; other presets are listed by
  `capsa_describe_tool`. Capsa measures the baseline itself at save time.
- **People (optional).** The plan's owner defaults to the connected Capsa
  user. Naming a different owner, an accountable-to person, or participants
  needs a Capsa user id or `aspire:<contact id>` — the connector does not
  resolve people by name yet, so ask the user for the id or keep the
  default.
- **Follow-through (optional).** `next_action` text and a `check_back_on`
  date.

## Workflow

### 1. Resolve the property

If the property isn't already identified, call `capsa_search_properties` and
confirm the match with the user — see
[Resolving ambiguous names](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/reference/patterns/resolve-ambiguous-names.md)
if more than one candidate comes back.

### 2. Check what's already open

Call `capsa_list_improvement_plans` with `property_ids: [<id>]`. Capsa
allows one open plan per property and goal, so if a plan for the same
objective already exists, this skill ends here: show it, and point the user
to Command Center for changes to it.

### 3. Agree the goal with the user

From the user's words, propose the objective and target in one line and
confirm: "Days past due for 10551 Barkley, target 30 days by December 2 —
right?" Never infer a goal silently. Remind them a target has to improve on
the baseline Capsa measures (a lower number for days past due and
complaints, a higher one for margin, penetration, and close rate, a better
band for property health) — Capsa refuses a plan whose target doesn't.

### 4. Prepare the proposal — no write yet

Call `capsa_prepare_improvement_plan` with the property, objective, goal
text, target, dates, and any people or follow-through fields. Nothing is
saved. The response carries:

- `property` — the stored property name, verified by Capsa; echo it back
  exactly as `write_confirmation.selected_property_name` later.
- `proposal` — the normalized fields Capsa will save, and `proposal_token`,
  which the save step must return unchanged.
- `existing_open_plan_id` — set when an open plan already covers this
  property and goal (step 2 should have caught it; if it appears here, stop
  and show that plan).
- `warnings` — always includes that plans are live on save.

The prepare response never includes the baseline number: Capsa computes it
only at save time.

### 5. Present the exact proposal for approval

Show the specific values that will be saved — property, goal, target and
date (and the measurement period for margin/penetration/close rate), owner,
next action, check-back date — not a paraphrase. Tell the user plainly,
before they approve: once saved, the plan is live in Command Center for the
whole team, and it can only be changed or closed there.

### 6. Save only after explicit approval

Call `capsa_save_improvement_plan` with the same fields and a
`write_confirmation` block: `confirmed_by_user: true`, a one-line
`summary` of what the user approved, `selected_property_id`, the
`selected_property_name` from the prepare response, and the
`proposal_token` unchanged. Any change to the fields needs a fresh prepare
call first — the token will not match otherwise.

### 7. Report the saved result

The save response returns the plan as Capsa stored it, including the
baseline Capsa measured and a `plan_url` into Command Center. Report the
stored values, not the requested ones — the baseline is new information the
user has not seen yet.

### 8. Handle a refusal without retrying blindly

Capsa refuses, with a plain message and no partial write, when: the property
isn't available to this connection; an open plan already exists for the
goal; the target doesn't improve on the baseline; the metric isn't
measurable in the chosen baseline window (for example no late A/R in that
window for a days-past-due plan); or the confirmation doesn't match the
prepared proposal. Show the message verbatim, then either adjust the goal,
window, or property with the user, or stop.

## Stop rules

- **Never save without the user's explicit approval of that exact prepared
  proposal.** A changed request needs a fresh prepare call — its
  `proposal_token` won't match an old approval.
- **A saved plan is live immediately.** Say this before asking for approval,
  not after saving. Never call a saved plan a "draft."
- **One open plan per property and goal.** Surface an existing plan instead
  of trying to create a sibling.
- **Never invent an objective, target, date, or person id.** Confirm the
  goal in the user's words; ask for ids rather than guessing.
- **Don't describe a plan's progress.** Plan identity and status are live;
  the metrics inside a plan's `outcome` may be up to 24 hours old, and a
  quiet plan means the property is owned, not that it is improving. Report
  the measurement and its date; let the user judge.
- **No edits or closes through the connector.** Point the user to Command
  Center.
- **Surface a refusal verbatim and stop — don't retry with different wording
  to route around it.**

## Example user prompt

> "10551 Barkley keeps paying late. Let's set a plan to get them under 30
> days past due by early December — I'll own it."

## Example agent output (fictional)

```
Checked 10551 Barkley's plans: none open for days past due.

Proposed plan (nothing saved yet):
- Property: 10551 Barkley
- Goal: Bring days past due under 30 by the end of next quarter
- Target: 30 days past due, by 2026-12-02
- Baseline window: 2026-06-20 to 2026-09-18 (Capsa measures the starting
  point when the plan is saved)
- Owner: you
- Next action: Call the AP contact about the two oldest invoices
- Check back: 2026-10-02

Once you approve, this plan is live in Command Center for the whole team and
can only be changed or closed there. Save it?
```

After approval:

```
Saved. 10551 Barkley — days past due plan, target 30 days by 2026-12-02.
Capsa measured the starting point at 50 days past due (as of 2026-09-18).
Owner: you. Open it in Command Center: <plan link>
```

All names, figures, and dates above are fictional.

## Team specifics

<!--
  Persist any team convention for default baseline windows per objective,
  who typically owns plans on which books, and how owner/participant ids
  are supplied (from an internal directory vs. asked each time). Keep the
  steps and stop rules in sync with the cookbook; re-pull after a connector
  upgrade.
-->
