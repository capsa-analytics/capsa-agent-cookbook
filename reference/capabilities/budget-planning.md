# Budget planning (`budget_planning`)

Propose a create or edit to a property's Command Center budget item, review
near-duplicate warnings, and save only after explicit approval. A saved
budget item is live in Command Center planning immediately.

> This page mirrors `capsa_describe_capability` for `budget_planning`. The
> live output is the source of truth; availability is connection-specific —
> call `capsa_describe_capability` before assuming write access is enabled.
> For exact tool inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user wants to add a new budget item to a property.
- The user wants to refine or correct an existing budget item — check for a
  near-duplicate first; a broad existing line usually should be edited, not
  duplicated.

Not for reviewing what's already saved — that's
[Property context](property-context.md)'s compact `budget_items` block or
its `planning_detail` drilldown, both read-only and available without this
capability's write permission.

## Tools

- `capsa_prepare_budget_item_change` — propose a create or edit; return the
  proposed change and any near-duplicate items to review. Writes nothing.
- `capsa_save_budget_item_change` — execute exactly one reviewed proposal
  after explicit user confirmation.

## Preparing (read, no write)

Input: `property_id`, `action` (`create` or `edit`), `line_id` (required for
edit), and the writable fields — `item_name`, `scope_type` (`property`
default, `division`, `service_type`, `service`, `opportunity`, or
`contract`, plus the matching `*_id`), `scope_label`, `budget_year`
(required on create), `budget_month`, `category` (`total` default, `base`,
`penetration`, `ar`, `other`), `amount` (required on create), `note`,
`status` (`active` default; `archived` is refused on create).

Response: `property` (`property_id`/`property_name` — take
`property_name` **verbatim** into the save call), `proposal` (a
`proposal_token` to echo back unchanged, `proposed`, and — for edits —
`current`, `field_changes`, and `expected_updated_at`), `near_duplicates`
(other active items on the property that look like the same thing, with
`match_reasons`: `same_scope` and/or `similar_name`), and `warnings`.

## Saving (confirmation-gated)

Same fields, plus `expected_updated_at` (required for edits, from the
prepare response) and a `write_confirmation` object: `confirmed_by_user`,
`summary`, `selected_property_id`, `selected_property_name` (must match the
prepare response's `property.property_name` exactly), and `proposal_token`
(must match the prepare response's exactly).

The save is refused, with no partial write, when: the target item's client
already approved it; its renewal plan is approved internally; the target
year/division lane is already approved internally (checked independently of
whether any budget line exists in it yet); a create would exactly duplicate
an existing active item; a create sets `status: "archived"`; a supplied
scope id doesn't resolve to exactly one usable label in Capsa's own data;
the `proposal_token` doesn't match; or (edits) `expected_updated_at` no
longer matches the item's live value.

Response: `budget_item` — `id`, `item_name`, `scope`, `budget_year`,
`budget_month`, `category`, `amount`, `note`, `status`, `client_approval`
(`Awaiting client`, `Client approved`, or `Client declined` — always
`Awaiting client` on a fresh create; this tool never sets it), `updated_at`,
`updated_by` — plus `warnings`.

## Boundaries

- **A confirmed save is live in Command Center planning immediately.** There
  is no draft or pending state for budget items — never describe a saved
  item as a draft.
- Never sets or reads `client_approval` status, or the internal renewal-plan
  `approved_by`/`approved_at` sign-off — those are a person's actions in
  Capsa, and a different authority than each other (see
  [Property context](property-context.md)'s client-approval note).
- Every scope id supplied is checked against Capsa's own data before it's
  accepted, at both prepare and save — a bogus, deleted, or cross-property
  id is refused, never silently accepted.
- Prepare performs no database write at all; only save does.
- Capsa resolves write access from the connection; prepare and save share
  one permission gate.

## Freshness

Prepare and save read and write live, current-transaction data — not the
general 24-hour notice. Every response carries its own planning freshness
note instead.

## Related

- Capability: [Property context](property-context.md) — the `planning_detail`
  drilldown for reading what's already saved.
- Capability: [Price recommendations](price-recommendations.md) — the
  sibling write capability; contrast its permanent-draft lifecycle with this
  capability's immediate-live save.
- Skill: [budget-item-change](../../skills/budget-item-change/SKILL.md)
