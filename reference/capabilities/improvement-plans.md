# Improvement plans

Read the Command Center improvement plans the connected Capsa user can see,
and — where the connection has the "Create plans" permission — start a new
one through a prepare-then-save flow. A plan commits a property to one
measurable goal with a baseline Capsa measures, a target, a date, and an
owner. A saved plan is live in Command Center immediately.

Capability id: `improvement_plans`. Confirm it is available on the
connection with `capsa_list_capabilities` before relying on it, and check
`capsa_describe_capability` for the current field list.

## Use when

- The user asks what plans are open on a property or across their book, or
  wants the full picture on one plan (its measurement, why it is surfacing,
  its event history).
- The user wants to commit a property to a measurable goal — gross margin,
  penetration, close rate, days past due, open complaints, or property
  health — and the connection can create plans.

Not for free-text planning notes (see the property-context capability's
Command Center note tools and the **property-plan-builder** skill), and not
for editing or closing an existing plan — both happen in Command Center.

## Tools

- `capsa_list_improvement_plans` — plans visible to the connected user,
  optionally narrowed to `property_ids` (up to 500), open only by default
  (`include_closed: true` adds closed plans).
- `capsa_get_improvement_plan` — one plan by `plan_id`, plus `attention`
  (why it is surfacing), `health` (the property's current health context),
  `outcome` (the live measurement versus the target), and up to 50 recent
  `events`; an optional IANA `timezone` interprets the measurement period.
- `capsa_prepare_improvement_plan` — read-only proposal of a new plan; no
  write.
- `capsa_save_improvement_plan` — creates exactly one plan from a prepared
  proposal the user approved.

## Reading

Every plan row carries: `id`, `property {id, name}`, `objective {id,
label}`, `goal`, `status` (`open` / `closed`), `needs_target`, `owner` and
`accountable_to` (name plus an `unassigned` flag — never a raw id),
`target {value, kind, health_band, text}`, `baseline {value, window,
as_of}`, `plan_start_on`, `target_date`, `next_action`, `check_back_on`,
`close` (null while open; `kind`, `disposition`, `reason`, `closed_at` once
closed), `created_at`, `updated_at`.

`close.kind` is either `health_recovered` — a verified outcome — or
`disposition`, a statement about the plan (for example "no longer
relevant"), never evidence that the property improved.

## Preparing (read, no write)

`capsa_prepare_improvement_plan` takes `property_id`, `objective_type`,
`goal` (one sentence), `target_value`, `target_date`, and for the
period-based objectives (`gm_pct`, `penetration_pct`, `close_rate_pct`) a
`plan_start_on`; optional `owner_user_id` or `owner_person_id`,
`accountable_to_user_id` or `accountable_to_person_id`, `participants`,
`next_action`, `check_back_on`, `baseline_preset` (default `custom`, which
needs `baseline_start_date` and `baseline_end_date`), and `measurement_scope`
(gross margin only).

It returns the verified `property {id, name}`, the normalized `proposal`
with a `proposal_token`, `existing_open_plan_id` when an open plan already
covers this property and goal, and `warnings`. It never returns the
baseline number — Capsa measures the baseline only at save time.

`target_value` is one field for every objective: a percent for gross
margin, penetration, and close rate; days for days past due; a whole number
for open complaints; and the health band to reach (`green`, `yellow`,
`red`) for property health.

## Saving (confirmation-gated)

`capsa_save_improvement_plan` takes the same fields plus a
`write_confirmation` block: `confirmed_by_user: true`, a short `summary` of
what the user approved, `selected_property_id`, `selected_property_name`
(echo the prepare response's `property.name` exactly), and the
`proposal_token` unchanged. Any change to the fields needs a fresh prepare
call. It returns the saved `plan` (with the baseline Capsa measured) and
`links` back into Command Center and Aspire.

Capsa refuses — with a plain message and no partial write — when the
property is not available to this connection, an open plan already exists
for the same property and goal, the target does not improve on the measured
baseline, the metric is not measurable in the chosen baseline window, or the
confirmation does not match the prepared proposal.

## Boundaries

- Create only. No edit or close through the connector; those happen in
  Command Center.
- One open plan per property and goal, enforced by Capsa.
- Reads follow the connected user's own Command Center access; the
  connector cannot widen what that user can see.
- People are referenced by Capsa user id or `aspire:<contact id>`; the
  connector does not resolve names to ids.
- A plan is live the moment it is saved. There is no draft state.
- Plan identity and status are live; the metrics inside a plan's `outcome`
  may be up to 24 hours old. A quiet plan means the property is owned, not
  that it is improving.

## Freshness

Plan identity, status, and events reflect Command Center as of the call.
Property metrics inside `outcome` and `health` may be up to 24 hours old;
every response says so.

## Related

- Skill: [improvement-plan-start](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/improvement-plan-start/SKILL.md)
- Reading a property before planning for it: [property-context](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/reference/capabilities/property-context.md)
- Free-text future-plans notes: [property-plan-builder](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/property-plan-builder/SKILL.md)
