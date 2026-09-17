# Scorecard queries (`scorecard_queries`)

Run supported Ops Scorecard or Sales Scorecard analytics with explicit
dates, metrics, dimensions, and filters, and drill into the rows behind one
cell.

> This page mirrors `capsa_describe_capability` for `scorecard_queries`. The
> live output is the source of truth. Call `capsa_describe_analytics_catalog`
> first when the metric, dimension, or filter shape is uncertain. For exact
> tool inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user asks a supported Ops Scorecard question (e.g. gross profit per
  labor dollar by division by month).
- The user asks a supported Sales Scorecard question (e.g. won amount by
  Sales Rep by week).
- The user wants to know what's driving one scorecard cell.

Not for browsing what metrics or dimensions exist first — call
`capsa_describe_analytics_catalog` for that, then come here to run the
query.

## Tools

- `capsa_query_scorecard` — run supported Ops or Sales Scorecard analytics
  with explicit dates, metrics, dimensions, filters, and guidance.
- `capsa_get_scorecard_drilldown` — return Ops visit/work-ticket detail or
  Sales opportunity detail behind one selected scorecard cell.

## Filter dimensions

Discoverable via `capsa_describe_analytics_catalog` — resolve names to
values first (see the
[Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
pattern):

| Filter | Scope | Notes |
| --- | --- | --- |
| Branch | Both | Use stable IDs. |
| Division | Both | Use stable IDs. |
| Service Type | Ops | Use stable IDs. |
| Work Ticket Status | Ops | Defaults to Complete and Pending Approval. |
| Sales Rep | Sales | Use stable contact IDs. |
| Account Owner | Both | Use stable contact IDs. |
| Property Type / Industry | Sales | Use stable IDs when available. |
| Sales Group | Sales | `sales_group_name` input — resolves to that group's exact Opportunity Type/Sales Type/Division/Invoice Type/Job Status filters. An unresolvable explicit name is an error, never a silent unfiltered fallback. |
| Opportunity Type / Sales Type | Sales | Explicit `filters` values win over a resolved Sales Group's own value for the same field. |
| Crew Leader / Route / Route Manager | Ops | Exact labels. |

`capsa_query_scorecard`'s `dimension` groups rows (e.g. Division, Sales
Rep); `time_grain` buckets the date range (e.g. month, week); `date_basis`
picks which date drives the window (`production_activity` for Ops; `event`
or `start` for Sales).

## Boundaries

- Read-only — no write tool.
- Exact `start_date`/`end_date` required; no fuzzy date phrases.
- **Ops**: production-activity date basis. Earned (production) revenue, not
  invoiced revenue — except Division/Branch/Account-Owner invoiced-revenue
  pairings, which always use every Work Ticket Status and reject an
  explicit status filter. After-OT metrics include Capsa's approximate
  overtime premium. Ratio metrics are blank when the denominator is zero.
  Active-crew-leader filtering is a people-dimension default only.
- **Sales**: Event Date (each metric's own timing — Created/Proposed/Won can
  include different deals in the same period) vs. Start Date (all three line
  up to the same opportunity start). A Sales Group's exact saved filters and
  date basis apply when one resolves; falling back to Work Order/New Sale
  happens only when no group resolves at all. `created_count` includes
  never-sent opportunities; other metrics exclude them by default. Close
  rate is cohort-based (follows proposals from the selected period).
  Active-Sales-Rep filtering is a people-dimension default only.
- Drilldown requires the same metric/dimension/dimension_id/date range/
  filters as the originating query. Sales drilldown accepts only count/
  amount metrics, not averages.
- Capsa resolves data access from the connection.

## Freshness

Scorecard analytics may be up to 24 hours old; don't treat it as live
dispatch status.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Tool: `capsa_describe_analytics_catalog` — check the metric/dimension shape
  before querying.
- Capability: [Property analytics](property-analytics.md) — property-level
  penetration and profitability context.
- Skill: [scorecard-review](../../skills/scorecard-review/SKILL.md)
