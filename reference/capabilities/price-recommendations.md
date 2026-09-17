# Price recommendations (`price_recommendations`)

Propose a create or edit to a property's DRAFT Command Center price increase
recommendation, review near-duplicate warnings, and save — always as a
draft — only after explicit approval.

> This page mirrors `capsa_describe_capability` for `price_recommendations`.
> The live output is the source of truth; availability is
> connection-specific — call `capsa_describe_capability` before assuming
> write access is enabled. For exact tool inputs/outputs, call
> `capsa_describe_tool`.

## Use when

- The user wants to draft a new price increase recommendation for a
  property.
- The user wants to edit an existing recommendation that is **still a
  draft**.

Not for reviewing, approving, dismissing, or applying a recommendation —
none of those actions exist through this connector; they happen in Command
Center. Not for reading what's already saved either — that's
[Property context](property-context.md)'s compact
`price_increase_recommendations` block or its `planning_detail` drilldown.

## Tools

- `capsa_prepare_price_recommendation_change` — build a create/edit
  proposal, with near-duplicate warnings. Writes nothing.
- `capsa_save_price_recommendation_change` — save exactly one reviewed
  proposal, always as a draft, after explicit user confirmation.

## Preparing (read, no write)

Input: `property_id`, `action` (`create` or `edit`), `recommendation_id`
(required for edit), `scope_type` (`property` default, `division`,
`service_type`, `service`, `opportunity`, or `contract`, plus the matching
`*_id`), `scope_label`, `recommendation_type` (`percent` or `dollar` —
required on create; determines which single value field applies),
`recommended_percent` or `recommended_amount` (display units — `6` means
6%, never a decimal fraction), `effective_year`/`effective_month`,
`target_margin_percent`/`current_margin_percent` (display units),
`expected_revenue_delta`, `note`.

Response: `property` (take `property_name` **verbatim** into the save
call), `proposal` (a `proposal_token` to echo back unchanged, `proposed`
with `status` always `draft`, and — for edits — `current`,
`field_changes`, and `expected_updated_at`), `near_duplicates` (other
non-dismissed recommendations on the property whose scope and timing
overlap), and `warnings`.

## Saving (confirmation-gated)

Same fields, plus `expected_updated_at` (required for edits) and the same
`write_confirmation` shape as [Budget planning](budget-planning.md):
`confirmed_by_user`, `summary`, `selected_property_id`,
`selected_property_name` (must match the prepare response's
`property.property_name` exactly), `proposal_token` (must match the prepare
response's exactly).

The save is refused, with no partial write, when: the recommendation being
edited is no longer a draft (a distinct message per status — reviewed,
approved, applied, or dismissed); a create would exactly duplicate an
existing non-dismissed recommendation (same scope, timing, type, and
value); a supplied scope id doesn't resolve to exactly one usable label; the
`proposal_token` doesn't match; or (edits) `expected_updated_at` no longer
matches the recommendation's live value.

Response: `price_recommendation` — `id`, `scope`, `recommendation_type`,
`recommended_percent`/`recommended_amount`, `effective_year`/
`effective_month`, `target_margin_percent`/`current_margin_percent`,
`expected_revenue_delta`, `note`, `status` (always `draft`), `updated_at`,
`updated_by` — plus `warnings`.

## Boundaries

- **Every save from this capability stays a draft, permanently.** There is
  no review, approve, dismiss, or apply transition through this connector,
  now or planned — a person does that in Command Center.
- Saving never notifies the customer and never changes a live price in
  Aspire.
- Only a `draft` recommendation can be edited through this capability — any
  other status must be reopened in Command Center or replaced with a new
  recommendation.
- Exactly one of `recommended_percent`/`recommended_amount` must be set,
  matching `recommendation_type` — the other is refused if supplied.
- Every scope id supplied is checked against Capsa's own data before it's
  accepted, at both prepare and save.
- Capsa resolves write access from the connection; prepare and save share
  one permission gate, separate from [Budget planning](budget-planning.md)'s.

## Freshness

Prepare and save read and write live, current-transaction data — not the
general 24-hour notice. Every response carries its own planning freshness
note instead.

## Related

- Capability: [Property context](property-context.md) — the `planning_detail`
  drilldown for reading what's already saved, and the receivables/revenue-mix
  context that typically informs a recommendation.
- Capability: [Budget planning](budget-planning.md) — the sibling write
  capability; contrast its immediate-live save with this capability's
  permanent-draft lifecycle.
- Skill: [price-recommendation-change](../../skills/price-recommendation-change/SKILL.md)
