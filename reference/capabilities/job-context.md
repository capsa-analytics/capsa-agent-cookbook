# Job context (`job_context`)

Review or rank a whole branch/division book of active (WIP) jobs at once,
then go deep on one job: a compact card plus focused drilldowns for ticket,
change-order, issue, crew-leader, billing, and health detail.

> This page mirrors `capsa_describe_capability` for `job_context`. The live
> output is the source of truth; filter **values** are connection-specific —
> call `capsa_list_job_filter_options` at runtime. For exact tool
> inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user wants to rank or review a whole branch/division book of active
  jobs — "which jobs are behind, over budget, or losing margin."
- The user asks for one active job's compact card: identity, health,
  job-to-date financials, budget, progress, schedule, billing summary,
  change orders, ticket status counts, or open issue count.
- The user needs ticket-level, change-order, issue, crew-leader, billing, or
  health-history detail behind one job.

This is the job-grain equivalent of
[Property context](property-context.md) — contacts, visit notes, and
manually-authored job notes are out of scope here; see Boundaries.

## Tools

- `capsa_list_job_filter_options` — list the Branch, Division, and
  Operations Manager filters available to the connection, plus the job-grain
  metric-filter vocabulary.
- `capsa_query_job_book` — a lean, sortable, keyset-paginated summary row per
  active job across a filtered book, plus book-level totals.
- `capsa_get_job_context` — a compact single-job card for one active job.
- `capsa_get_job_context_drilldown` — one focused block of detail for one
  active job: `ticket_breakdown`, `change_orders`, `open_issues`,
  `recent_completed_issues`, `crew_breakdown`, `billing_breakdown`, or
  `health_history`.

## Filter dimensions

Enumerable via `capsa_list_job_filter_options` — resolve names to values
first (see the
[Resolving ambiguous names](../patterns/resolve-ambiguous-names.md) pattern):

| Dimension | Field | Type | Notes |
| --- | --- | --- | --- |
| Branch | `branch_ids` | int[] | Also a permission axis. |
| Division | `division_ids` | int[] | Also a permission axis; a plain narrowing filter here (contrast Property Book's division lens). |
| Operations Manager | `operations_manager_contact_ids` | int[] | Query-only, not a permission axis. |

**Metric filters** (on `capsa_query_job_book`, server-side, job-to-date
basis): threshold conditions on `gross_margin_percent`,
`margin_erosion_pct_points`, `estimated_margin_percent`, `revenue_to_date`,
`cost_to_date`, `current_estimated_revenue`, `current_estimated_cost`,
`percent_complete`, `change_order_count`, and `open_issues_count` (operators
`eq`/`neq`/`gt`/`gte`/`lt`/`lte`/`between`; ANDed within a group, ORed across
groups; a `null` metric value never matches).

**Sort options** (`capsa_query_job_book`'s `sort_by`): `job_name`,
`health_status` (default — most urgent first), `gross_margin_percent`,
`margin_erosion_pct_points`, `estimated_margin_percent`, `revenue_to_date`,
`cost_to_date`, `current_estimated_revenue`, `percent_complete`,
`change_order_count`, `open_issues_count`, `scheduled_start_date`,
`scheduled_end_date`.

**No date range.** Job money and progress fields are cumulative since the
job's own start ("job to date"), never a rolling window — there is no
`date_range` input anywhere in this capability.

## Boundaries

- Read-only — no completion-write tool. Job-health review/acceptance and any
  other job mutation stay outside this capability entirely.
- `capsa_get_job_context` and `capsa_get_job_context_drilldown` accept only a
  `job_id` exactly as `capsa_query_job_book` returned it. A change order's
  own id, a completed (non-WIP) job, a nonexistent id, and a job outside the
  connection's allowed Branch/Division set all return the identical "not
  available" message — there is no way to tell the cases apart from the
  response.
- `health_status` is the raw, human-reviewed status on file. Jobs have no
  live, system-computed suggestion the way properties do — see
  [Property context](property-context.md)'s `health.recommendation` for that
  contrast.
- `crew_breakdown` is crew-leader attribution only (hours and cost pro-rated
  by each leader's share on a ticket), scoped to active ticket statuses.
- Gross margin and margin erosion use actual costs excluding overtime
  premium — the app's standard before-overtime margin.
- Contacts, visit notes, and manually-authored job notes are not part of
  this capability.
- Capsa resolves data access from the connection.

## Freshness

Data may be up to 24 hours old; don't treat it as live dispatch status.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Capability: [Property context](property-context.md) — the property-grain
  equivalent (book, single-property context, drilldowns).
- Skill: [job-book-review](../../skills/job-book-review/SKILL.md)
