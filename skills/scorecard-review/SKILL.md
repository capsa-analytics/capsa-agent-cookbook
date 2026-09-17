---
description: Answer an Ops or Sales Scorecard question end to end — check capsa_describe_analytics_catalog first for the right metric/dimension/date basis and any default Sales Group, run capsa_query_scorecard, drill into a specific cell with capsa_get_scorecard_drilldown when a number needs explaining, and bring in capsa_query_property_analytics for property-level penetration or profitability context. Always states which definitions were used. Use for scorecard and property-analytics questions, not ad hoc metric math.
---

# Scorecard review

Answer a scorecard question the way an analyst would: confirm the metric and
its definition before running anything, run the query, drill into whatever
looks surprising, and bring in property-level analytics when the question is
really about specific properties — always naming exactly which definitions
produced the answer.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Scorecard numbers are only useful with their definition attached — which
date basis, which default filters, which Sales Group. This skill makes that
check a habit instead of an afterthought: look up the shape before querying,
report the resolved defaults alongside every number, and drill in before
calling a ratio meaningful at scale.

The steps are the same whether this runs as an installed skill, is pasted
into another agent, or is run ad-hoc. The "Configuration" section lists the
inputs a run needs; persist them in the Team specifics block below, a system
message, or a wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected with the analytics-catalog and
  scorecard-queries capabilities available (and property-analytics, if the
  question also touches property-level margin or penetration).
- The user asks an Ops Scorecard, Sales Scorecard, or property-level
  Penetrations/Profitability question with a specific metric or shape in
  mind, not a request to browse Capsa's full metric catalog.
- An exact date range can be established, even if the user only gave a fuzzy
  phrase like "this quarter."

Skip it when the user wants a fuzzy exploration of what's possible — start
with `capsa_describe_analytics_catalog` alone and stop there. Skip it too
for property-level context that isn't a scorecard or analytics-report
question (contacts, satisfaction, drilldowns) — that's
[property-context](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/reference/capabilities/property-context.md), not
this skill.

## Required connected apps

- **Capsa MCP connector.** Provides the catalog, both scorecards, their
  drilldowns, and property analytics. This capability is read-only — no
  other connector is required unless the user wants the result exported.

## Configuration

- **Default scorecard scope (optional).** Any standing branch/division
  filter the team applies by default, and whether to leave
  `use_scorecard_defaults` on (recommended — it applies Capsa's own
  Work-Ticket-Status and Sales Group defaults).
- **Sales Group convention (optional).** If the team has a named Sales Group
  they mean by default ("Work Order Sales"), record it — otherwise the
  connection's own configured default group (if any) applies automatically
  when none is specified.
- **Property analytics defaults (optional).** Whether the team usually wants
  extended metrics on Property Profitability, and any standing
  branch/division/property-tag scope.

## Workflow

### 1. Check the catalog first

Call `capsa_describe_analytics_catalog` with the user's request (and
`surface` if you already know which one). This tells you the exact metric
IDs, supported dimensions, time grains, and default behavior before you run
anything — including, for Sales, whether a default Sales Group is
configured. If `request_analysis` says the shape isn't queryable today, stop
here and go to step 7 instead of guessing at a workaround.

### 2. Nail the date range and basis

Convert any fuzzy phrase ("this quarter," "last month") to an explicit
`start_date`/`end_date` with the user — both scorecard tools require exact
dates. State the basis in one line: Ops Scorecard always uses production
activity date; Sales Scorecard's Event Date basis groups Created, Proposed,
and Won by each metric's own event timing (so the same period can include
different deals across those totals), while Start Date lines all three up to
the same opportunity start-date group of work.

### 3. Run the scorecard query

Call `capsa_query_scorecard` with the resolved `scorecard`, `metrics`,
`dimension`, and any `filters`. Read back — and report to the user —
`query.resolved_defaults` and, for Sales, `query.sales_group_definition`
(the resolved group's name and its exact Opportunity Type / Sales Type /
Division / Invoice Type / Job Status filters, `null` when no group applied).
An explicit `sales_group_name` that doesn't resolve is a hard error, not a
silent unfiltered fallback — if that happens, say so and ask the user to
pick a real group name from the connection. Carry `plain_english_guidance`
and any `warnings` into your answer.

### 4. Drill in when a number needs explaining

When a value looks surprising, or the user asks "why," call
`capsa_get_scorecard_drilldown` with the **same** metric, dimension,
`dimension_id`, date range, and filters as step 3, narrowed to
`detail_scope: "period"` (with `period_start`) or `"range"`. For Ops, this
returns the visit/work-ticket rows behind the cell; for Sales, the
opportunity rows. Sales drilldown only accepts count/amount metrics
(`created_count`, `created_amount`, `proposed_count`, `proposed_amount`,
`won_count`, `won_amount`, `win_rate_count`, `win_rate_amount`) — not
averages.

### 5. Bring in property-level analytics when relevant

When the question is really about specific properties' margin or
penetration rather than a scorecard-wide total, call
`capsa_query_property_analytics` for the same date range — `report:
"property_profitability"` for margin, or `report: "property_penetration"`
for non-contract revenue against the contract base. State plainly that
these reports use Capsa's own configured base/penetration and profitability
group definitions, and are **not** the same basis as
`capsa_get_property_context`'s `revenue_mix` block — don't let the two
numbers get compared as if they were.

### 6. Synthesize

Answer in plain English, and always name what produced it: the metric
definition, the date basis, the dimension, the resolved Sales Group (Sales)
or report defaults (property analytics), and any denominator caveat. A
number with no definition attached is not a finished answer.

### 7. Offer to log a gap

If `capsa_describe_analytics_catalog` or a query response says the shape
isn't supported, offer to record it with `capsa_log_feature_request` (loop
step 5 in [capsa-orientation](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/capsa-orientation/SKILL.md)) — log only after the
user agrees, including the closest catalog match you found.

## Stop rules

- **Never report a bare number.** Every answer states the metric, date
  basis, dimension, and resolved Sales Group / report defaults that produced
  it.
- **Exact dates only.** Resolve fuzzy date phrases with the user before
  calling either scorecard tool or property analytics.
- **Don't conflate bases.** Ops earned/production revenue is not invoiced
  revenue (except the one Division/Branch/Account-Owner invoiced-revenue
  pairing, which always uses every Work Ticket Status and rejects an
  explicit status filter). Sales Event Date and Start Date group different
  opportunities in the same window. Property-analytics penetration and
  profitability are not `property_context`'s `revenue_mix`.
- **An unresolvable Sales Group name is an error, not a fallback.** Surface
  it and ask the user to choose a real one.
- **Ratio metrics are blank at a zero denominator.** Report that plainly —
  never render it as 0%.
- **Never reimplement scorecard or report math.** Only state what the tools
  actually returned.
- **Freshness.** Every figure may be up to 24 hours old — never describe it
  as live dispatch status.
- **No writes.** This capability is entirely read-only.

## Example user prompt

> "Gross profit per labor dollar looked off for Irrigation in February —
> what's going on, and how does that division's overall profitability look
> this year?"

## Example agent output (fictional)

```
Checked the catalog: gross_profit_per_labor_dollar is an Ops Scorecard
ratio metric (production activity date basis; defaults to Complete and
Pending Approval tickets).

Ops Scorecard — Irrigation division, Jan–Jun 2026, by month
(Capsa data may be up to 24 hours old):

Jan  0.61   Feb  0.22   Mar  0.58   Apr  0.63   May  0.66   Jun  0.60

February is the outlier. Drilling into that cell (same filters, February
only): 340 visits, earned revenue $48,200, labor cost actual $41,600 — labor
cost is high relative to revenue for the period, concentrated in 12 visits
with unusually high actual hours against estimate.

For the year-to-date picture, Property Profitability (Jan–Jun 2026, active
contracts only, indirect divisions excluded — Capsa's standard report
defaults) shows Irrigation-division properties averaging a 28% margin, in
line with the rest of the book except for the February dip above.

Want the list of those 12 high-hour visits, or a look at specific
properties in Irrigation?
```

All names and figures above are fictional.

## Team specifics

<!--
  Persist your default scorecard scope, Sales Group convention, and property
  analytics defaults (extended metrics, standing branch/division scope)
  here. Keep the steps and stop rules in sync with the cookbook; re-pull
  after a connector upgrade.
-->
