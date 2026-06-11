# Renewal opportunities (`renewal_opportunities`)

Pull the renewal book for a window — prior contract baseline, current renewal
pipeline by status, retention, price/scope change tags — and drill into one
property's service-level comparisons and prior-year performance review.

> This page mirrors `capsa_describe_capability` for `renewal_opportunities`.
> The live output is the source of truth; filter **values** are
> connection-specific — call `capsa_list_renewal_filter_options` at runtime.
> For exact tool inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user asks what's coming up for renewal in a division, window, branch,
  account-owner book, or tagged property set.
- The user asks which prior contracts have **no renewal started yet**.
- The user asks where the renewal pipeline stands by status, or how retention
  is tracking.
- The user asks which renewals carry price/scope changes or performance flags
  before re-pricing.
- The user wants one property's prior-year estimate-vs-actual review or
  service-level price/hours comparison.

## Tools

- `capsa_list_renewal_filter_options` — list the Status, Division, Branch,
  Account Owner, and Property Tag values available to the connection, plus the
  change-tag and performance-flag vocabularies and window presets.
- `capsa_find_renewals` — the renewal book, paged in batches of up to 100 with
  a book-level summary on every page: per property/division, the prior
  contract baseline (value, end date), the current renewal pipeline by status
  (`New`/`Bidding`/`Approved`/`Delivered`/`Won`/`Lost`), days to start, change
  tags (`price_increase`, `price_decrease`, `scope_increase`,
  `scope_decrease`, `potential_duplicate`), and contacts.
- `capsa_get_renewal_drilldown` — one property, one drilldown:
  `service_comparisons` (per-service price-per-hour and hours deltas, prior vs
  current), `performance_review` (estimated vs actual vs forecast margin,
  cost/hours variance, confidence level), or `renewal_opportunities` (the
  underlying prior- and current-window opportunity lists).

## Filter dimensions

Enumerable via `capsa_list_renewal_filter_options` — resolve names to values
first (see the
[Resolving ambiguous names](../patterns/resolve-ambiguous-names.md) pattern):

| Dimension | Field | Type |
| --- | --- | --- |
| Status | `statuses` | string[] — pipeline statuses plus `"none"` (baseline with no renewal started) |
| Sales type | `sales_types` | string[] — defaults to `Renewal`; teams that label renewals differently pick their value here |
| Division | `division_ids` | int[] |
| Branch | `branch_ids` | int[] |
| Account Owner | `account_owner_ids` | int[] |
| Tag | `property_tags` / `exclude_property_tags` | string[] |
| Property | `property_ids` | int[] |

**Renewal window:** a `preset` (`current_year`, `next_90_days`,
`next_180_days`) or explicit `start_date`/`end_date` over renewal start dates,
at most 12 months. The prior-contract baseline is the same window one year
earlier.

## Boundaries

- Read-only — no completion-write tool; renewal decisions and outreach are
  recorded outside Capsa.
- Book pulls are paged (up to 100 rows per call) with a true book-level
  summary on every page — keep pulling until the response says no rows
  remain; never present a partially paged book as full coverage.
- An empty pull at the default sales type usually means the team labels
  renewals differently — the response lists the available values; confirm with
  the user.
- Drilldowns are one property at a time; a multi-division property requires
  picking a division rather than summing.
- A `potential_duplicate` row (one prior contract, multiple active renewals)
  must be presented per opportunity, never as one summed forecast.
- Performance reviews carry a confidence level (`strong`, `directional`,
  `low`, `unavailable`) — carry it into any recommendation.
- Capsa resolves data access from the connection.

## Freshness

Data may be up to 24 hours old; don't treat the pipeline as live sales status,
especially for imminent start dates.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Capability: [Property context](property-context.md) — payment behavior,
  penetration, satisfaction, and margin context for renewal decisions.
- Skills: [renewal-portfolio-triage](../../skills/renewal-portfolio-triage/SKILL.md),
  [renewal-deep-dive](../../skills/renewal-deep-dive/SKILL.md)
