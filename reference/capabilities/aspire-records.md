# Aspire records (`aspire_records`)

Governed, read-only access to current Aspire records: describe a resource,
list individual records, or summarize them with totals, counts, and date
buckets, following related resources such as `Opportunity.Property`.

> This page mirrors `capsa_describe_capability` for `aspire_records`. The live
> output is the source of truth. This capability is enabled per connection;
> if `capsa_list_capabilities` does not list it, the tools are not available.

## Use when

- The user asks about records or fields that no named Capsa capability reports
  on: materials and purchases, completed jobs, ticket schedules, invoices,
  payments, specific opportunities.
- The user wants a list of specific records with filters, or a total, average,
  or count grouped by a field or by month, week, or day.
- A named capability answers the question already: prefer it, and use Aspire
  records to drill into detail.

## Tools

- `capsa_describe_aspire_resources` — with no arguments, the index of
  resources and reporting concepts. With `resource`, that resource's fields
  (filter with `fields`: `dates`, `dimensions`, `measures`, `identifiers`,
  `text`), related resources, and applicable concepts. With `concept`, one
  reporting concept: definition, how to query it, pitfalls, and the question
  to ask the user.
- `capsa_find_aspire_records` — individual current records of one resource,
  with filters, sort, and pages.
- `capsa_summarize_aspire_records` — totals, averages, counts, and distinct
  counts, optionally grouped by fields or date buckets.

## How to navigate

Drill down only as far as the question needs:

1. The index (once per task) to pick a resource.
2. `resource` with `fields: "dates"` or `"dimensions"` to find the date field
   and the filters that define the population.
3. `concept` for the idea the question depends on — for example
   `date_basis_map` (which date means what), `opp_status_canonical`,
   `sales_type`, `wip_completed_jobs`, `estimated_margin`, `item_allocations`.

Find and summarize responses also carry short `guidance` lines for the
concepts a request touches; carry them into the answer.

## Record guides

For questions about one family of records, read its guide instead of
exploring from the index:

- [Activities](../aspire-records/activities.md) — tasks, issues and complaints,
  appointments, and logged emails.

## Boundaries

- Read-only; current records only (records removed in Aspire are excluded).
- Personal HR and payroll fields, email content, and private activities are
  never returned.
- Related fields follow child to parent only, up to 4 levels.
- `sum` and `avg` apply only to fields of the requested resource.
- Page and group limits apply, plus a per-connection request rate; requests
  that would read too much data are refused before running.
- Capsa resolves data access from the connection.

## Freshness

Data may be up to 24 hours old; don't treat it as live dispatch status.

## Related

- Skill: [answer-a-data-question](../../skills/answer-a-data-question/SKILL.md)
- Capability: [Scorecard queries](scorecard-queries.md) — prefer a scorecard
  metric when one fits.
