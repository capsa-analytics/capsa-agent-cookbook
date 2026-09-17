# Property analytics (`property_analytics`)

Run Property Penetrations or Property Profitability by-property report
analytics with explicit dates, filters, defaults, and guidance.

> This page mirrors `capsa_describe_capability` for `property_analytics`.
> The live output is the source of truth. For exact tool inputs/outputs,
> call `capsa_describe_tool`.

## Use when

- The user asks a property-level penetration question — non-contract
  (work-order) revenue against the contract base, by property.
- The user asks a property-level profitability question — earned revenue,
  actual cost, and margin, by property.

Not the same basis as [Property context](property-context.md)'s
`revenue_mix` block — see Boundaries before comparing the two.

## Tools

- `capsa_query_property_analytics` — run Property Penetrations or Property
  Profitability by-property report analytics with explicit dates, filters,
  defaults, and guidance (`report: "property_penetration"` or
  `"property_profitability"`).

## Filter dimensions

Blank filters mean all values available to the connection, except where a
report default is listed (see Boundaries):

| Filter | Notes |
| --- | --- |
| Property | Stable property IDs. |
| Branch | Report Branch names. |
| Account Owner | Report Account Owner names. |
| Property Group | Property group names. |
| Division | Division names. |
| Property Type | Property type names. |
| Property Tag | Property tag names. |
| Industry | Industry names. |
| Work Ticket Status | Property Profitability only; blank means all statuses. |

## Boundaries

- Read-only — no write tool.
- Exact `start_date`/`end_date` required; no fuzzy date phrases.
- **Property Penetrations**: `base_revenue` is earned revenue matching
  Capsa-configured base-business filters; `penetration_revenue` is earned
  revenue matching Capsa-configured penetration/work-order filters;
  `penetration_percentage` is penetration revenue over base revenue;
  `py_penetration_revenue` is the prior-year figure for the same window
  shifted back one year. Active-contracts-only and
  never-sent-to-client-excluded both default on.
- **Property Profitability**: earned revenue minus actual production cost
  for the date range; `total_margin_percent` is null when revenue is zero.
  Active-contracts-only and indirect/overhead-division-excluded both default
  on. Extended metrics (actual/estimated hours, cost-category detail) are
  optional.
- **Not the same basis as `property_context`'s `revenue_mix`.** This report
  uses Capsa-configured base/penetration/profitability group definitions;
  `revenue_mix` is a plain Contract-vs-Work-Order split. Explain the
  difference rather than treating the two as interchangeable.
- Large property lists are capped; use `filters`/`property_ids` for
  exhaustive detail.
- Capsa resolves data access from the connection.

## Freshness

Property analytics may be up to 24 hours old; don't treat it as live
dispatch status.

## Related

- Capability: [Scorecard queries](scorecard-queries.md) — the metric-level
  Ops/Sales Scorecard surface.
- Capability: [Property context](property-context.md) — single-property
  `revenue_mix` and receivables context (different basis — see Boundaries).
- Skill: [scorecard-review](../../skills/scorecard-review/SKILL.md)
