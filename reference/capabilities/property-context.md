# Property context (`property_context`)

Search properties and retrieve operational context — contacts, relationship
status, production, satisfaction, sales, and upcoming-visit signals — for one
property, a selected set, or a filtered property book.

> This page mirrors `capsa_describe_capability` for `property_context`. The live
> output is the source of truth; filter **values** are connection-specific — call
> `capsa_list_property_context_filter_options` at runtime. For exact tool
> inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user gives a fuzzy or abbreviated property name and needs the right property
  identified.
- The user needs contact-ready property context before drafting customer
  communication.
- The user asks for one property's production, satisfaction, sales, or
  upcoming-visit context.
- The user asks to review a filtered property book for renewal, contact, or
  prioritization work.
- The user needs a focused drilldown behind one property.
- The user wants to rank or filter an entire property book by a specific
  metric threshold (margin, penetration, AR) rather than a capped portfolio
  pull — see Property book below.
- The user asks a fixed "what needs my attention today" triage question over
  their book — see Attention queue below.

## Tools

- `capsa_list_property_context_filter_options` — list the filter values available
  to the connection.
- `capsa_search_properties` — fuzzy-match a property, customer, contact, owner,
  tag, or ID and return contact-ready candidates (default 25 rows, up to 100).
- `capsa_find_properties_by_primary_contact` — resolve a primary-contact email
  or fuzzy name to accessible property candidates. Gated by this capability's
  read permission (it also appears in the Command Center notes workflow, but a
  connection needs only `property_context` to call it).
- `capsa_get_property_context` — compact context for one property, selected
  properties, or a capped, filtered property book.
- `capsa_get_property_context_drilldown` — one focused drilldown behind a single
  property.
- `capsa_query_property_book` — a lean, sortable, keyset-paginated summary
  row per property across a filtered book, plus book-level totals — for
  ranking or reviewing a whole book, not single-property depth.
- `capsa_get_attention_queue` — a fixed-order "what needs my attention
  today" triage queue over the caller's property book: health severity,
  then contract value at stake.

## Filter dimensions

Enumerable via `capsa_list_property_context_filter_options` — resolve names to
values first (see the
[Resolving ambiguous names](../patterns/resolve-ambiguous-names.md) pattern):

| Dimension | Field | Type |
| --- | --- | --- |
| Branch | `branch_ids` | int[] |
| Account Owner | `account_owner_ids` | int[] |
| Division | `division_ids` | int[] |
| Property type | `property_type_names` | string[] |
| Tag | `property_tags` | string[] |
| Industry | `industry_names` | string[] |
| Work-ticket status | `work_ticket_statuses` | string[] |
| Property | `property_ids` | int[] |

**Metric filters** (server-side; operators `eq`/`neq`/`gt`/`gte`/`lt`/`lte`/
`between`; ANDed within a group, ORed across groups; a `null` metric value
never matches):

| Metric ID | Available on |
| --- | --- |
| `total_revenue` | `capsa_get_property_context`, `capsa_query_property_book` |
| `contract_value` | Both |
| `gross_margin_percent` | Both |
| `gross_margin_dollars` | Both |
| `total_cost` | Both |
| `ar_outstanding` | Both |
| `ar_late_outstanding` | Both |
| `ar_weighted_days_past_due` | Both |
| `days_late_to_pay` | Both |
| `penetration_percent` | Both |
| `work_order_revenue` | Both |
| `contract_gross_margin_percent` | Both |
| `work_order_gross_margin_percent` | Both |
| `open_issues_count` | `capsa_query_property_book` only |
| `open_complaints_count` | `capsa_query_property_book` only |

`capsa_list_property_context_filter_options` lists the first 13 as
`metric_filter_metrics` (what `capsa_get_property_context` accepts) and all
15 as `property_book_metric_filter_metrics` (what `capsa_query_property_book`
accepts) — two separate fields, since the tools' metric sets differ.

**Date range:** a `preset` (`last_365_days`, `last_90_days`, `current_year`) or an
explicit `start_date`/`end_date`. Applies to `capsa_get_property_context` only
— see Property book below for how the book handles timing.

**Drilldowns** (`capsa_get_property_context_drilldown`, one property at a time):
gross margin by division / service type / service / opportunity / work ticket; open
and recent complaints; open and recent-completed issues; delivered proposals;
proposed opportunities; active contracts; upcoming visits; last-touch activity.

## Property book and attention queue

Two summary/triage tools, not single-property depth — call
`capsa_get_property_context` for contacts, satisfaction detail, sales,
receivables, revenue mix, and drilldowns.

**`capsa_query_property_book`** reuses the same filters as
`capsa_get_property_context` (Branch, Account Owner, Division, Property
Type, Property Tag, Industry, Work Ticket Status) plus the metric filters
above, and returns a lean row per property (identity, `health_status`, the
metric-filter fields, `last_touch_at`). `sort_by`: `property_name` (default),
`gross_margin_percent`, `total_revenue`, `active_contract_value`,
`next_contract_end_date`, `open_issues_count`, `open_complaints_count`,
`last_touch_at`, `health_status`, `penetration_percent`, `ar_outstanding`,
`ar_late_outstanding`, `days_late_to_pay`. No `date_range` input:
`gross_margin_percent`/`total_revenue`/`penetration_percent`/the two
work-order margin fields default to the same trailing-365-day window
`capsa_get_property_context` uses; `active_contract_value`,
`next_contract_end_date`, and `health_status` are current, not date-ranged;
`ar_outstanding`, `ar_late_outstanding`, `ar_weighted_days_past_due`, and
`days_late_to_pay` are point-in-time as of today. **`division_ids` is an
advanced lens here, not a plain filter**: when set, revenue/margin/contract
value/dates reflect only that division's work at each property while open
issues, complaints, last-touch, and health stay whole-property — the
response carries an explicit warning, and division-scoped figures must never
be combined with whole-property ones.

**`capsa_get_attention_queue`** has a narrower filter set — `branch_ids`,
`account_owner_ids`, `property_tags` only, no `division_ids` and no
`property_ids` — and **no `sort_by`**; the order is fixed: health group
ascending (`at_risk`, `needs_attention`, `healthy`, `no_health_set`), then
`in_production_contract_value` descending, then property ID. Each row
carries a `signals` block (open issues/complaints, a stale-activity flag,
late AR, next renewal date, days since last touch) and an optional
`top_recommendation` (Capsa's single highest-signal pending suggestion, at
most 7 days old — never a complete task list). Use
`capsa_query_property_book` instead when a configurable sort or a specific
metric threshold is what's needed.

Both tools' totals (`book`/`queue`) are computed over the full filtered
scope before paging, and both use Capsa's standard, uncustomized metric
definitions — a company that has customized which contracts, issue
categories, or activity types count toward its Command Center screen may see
small differences there.

## Boundaries

- Property context is read-only — no completion-write tool.
- Broad property-book pulls (`capsa_get_property_context` with no property
  IDs or narrow filters) are capped; use filters, property IDs,
  `capsa_query_property_book`, or `capsa_get_attention_queue` for exhaustive
  or ranked book-level reads.
- Drilldowns are one-property detail pulls, not default portfolio payloads.
- `capsa_query_property_book` and `capsa_get_attention_queue` return
  summary/triage rows only, not contacts, satisfaction detail, sales,
  receivables, revenue mix, or drilldowns.
- Capsa resolves data access from the connection.
- Capsa does not parse personal pronouns as filters — use explicit filter options
  or ask the user to narrow.

## Freshness

Data may be up to 24 hours old; don't treat it as live dispatch status. The
property book and attention queue mix bases within one row — trailing
365-day revenue/margin figures alongside point-in-time contract-value, AR,
and health figures — state both when reporting a row, not one snapshot age.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Skills: property context supplies the drafting context used across the
  pack; [property-book-triage](../../skills/property-book-triage/SKILL.md)
  is the dedicated workflow built on the property book and attention queue.
