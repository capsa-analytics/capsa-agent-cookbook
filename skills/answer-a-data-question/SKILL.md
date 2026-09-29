---
description: Answer a business numbers question ("how much did we sell", "who is closest to estimate", "what did we spend on mulch") by framing it before computing — pick the Capsa report or Aspire resource, settle the population, date field, measure, and grouping, ask the user once when a choice changes the answer, and finish with a one-line scope statement. Use for any ad hoc metric question; hand off to scorecard-review, job-book-review, or renewal-portfolio-triage when the question is really one of those.
---

# Answer a data question

Most wrong answers to a numbers question are not math errors. They are
framing errors: the wrong date field, the wrong slice of work, or the wrong
kind of dollars. The same question can be off by 3x depending on whether "last
month" means won date or start date. This skill makes the framing explicit
before any number is computed.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Turn a plain-language question into a framed query — route, population, date
field, measure, grouping — confirm it with the user only where it matters, run
it with the smallest response that answers it, and show the frame next to the
number. The steps are framework-agnostic; the "Configuration" section lists
the inputs a run needs.

## When to use

- The user asks for a total, count, rate, ranking, or comparison over a period.
- The question uses business words that could map to several Capsa or Aspire
  fields ("sold", "done", "enhancement", "late", "over budget", "new").

Hand off when the question is squarely one workflow:
[scorecard-review](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/scorecard-review/SKILL.md)
for a scorecard metric,
[job-book-review](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/job-book-review/SKILL.md)
for active jobs,
[renewal-portfolio-triage](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/renewal-portfolio-triage/SKILL.md)
for a renewal book.

## Required connected apps

- **Capsa MCP connector.** Read-only for this skill. Aspire records tools
  (`capsa_describe_aspire_resources`, `capsa_find_aspire_records`,
  `capsa_summarize_aspire_records`) are used only when the connection has them.

## Configuration

- **Team vocabulary (optional).** Words your team uses for configured groups
  ("new contract sales", "enhancements") and which Sales Group or Penetration
  Group each means. Without it, discover groups at runtime (step 2).
- **Default date conventions (optional).** Calendar vs fiscal year; whether
  "this year" means year to date.

## Workflow

### 1. Route to the narrowest source

| The user says | Start with |
| --- | --- |
| sold, won, proposed, close rate, pipeline | Sales Scorecard (`capsa_query_scorecard`) or `capsa_get_sales_pace` |
| hours, efficiency, earned revenue, invoiced, margin by crew/division | Ops Scorecard (`capsa_query_scorecard`) |
| enhancement, upsell, add-on work vs contract base | `capsa_query_property_analytics` `property_penetration` |
| over budget, behind, margin slipping (active jobs) | `capsa_query_job_book` |
| renewals, retention, not renewed | `capsa_find_renewals` |
| anything else: materials, vendors, completed jobs, schedule, specific records | Aspire records, if enabled — else say it is not available and offer the closest report |

For a report route, call `capsa_describe_analytics_catalog` to confirm metric
IDs and defaults. Treat its `request_analysis` as a hint: if a listed metric
fits and the dimension, time grain, and date basis you need are also listed
for it, use it even when `request_analysis` reports no match.

For an Aspire records route, call `capsa_describe_aspire_resources` with no
arguments to see which resources this connection can read, and pick one
before framing the query.

### 2. Frame four slots

Fill each slot from the connector, not from memory:

- **Population** — which records count: Contract vs Work Order, sales type
  (New Sale, Renewal, …), status, division, and any configured Sales Group or
  Penetration Group. Group names come back from a scorecard query
  (`needs_sales_group`) or from the report's own group definitions.
- **Date field** — which date puts a record in the period. For Aspire records,
  call `capsa_describe_aspire_resources` with `resource` and `fields: "dates"`,
  and the `date_basis_map` concept for what each date means.
- **Measure** — which number: estimated price, won dollars, earned revenue,
  invoiced revenue, actual cost; count vs dollars; weighted total vs per-item
  average.
- **Grouping** — which person or bucket: sales rep, account owner, crew leader
  (primary or assigned), division, month. Group by ID, label by name.

### 3. Ask once, only where it moves the answer

If a slot has two reasonable readings that would change the answer
materially, ask one short question that offers your default ("By won date —
or by when the work starts?"). Otherwise proceed and state the default.
Common ones to ask: renewals included?; won date vs start date; earned vs
invoiced vs sold; include still-open proposals in a close rate?; all
properties or active-contract properties only?

### 4. Compute with the smallest response

- For totals, use the report's summary block (`max_rows: 1`) or
  `capsa_summarize_aspire_records`; never page through rows to add them up.
- Use exact dates. Keep the same frame when comparing two periods.
- Read and carry forward every `warnings` and `guidance` line.

### 5. Answer with a scope line

Lead with the number, then one line that names every slot and default, e.g.
"Scope: Contract, New Sale, won in August by won date, estimated price, by
sales rep; never-sent excluded." Flag immature periods (recent proposals
still open) and rows that are not comparable (placeholder budgets, overhead
tickets, zero-revenue jobs).

## Stop rules

- The data needed is not available on this connection: say so plainly, offer
  the closest available answer, and log a feature request if the user wants.
- A slot is ambiguous and the readings differ materially: ask before answering.
- A response is too large to read: re-run with a summary or smaller page.
- Never fill a missing value with zero or blend incompatible populations
  (for example contract and work-order margins) into one number.

## Example user prompt

> Which of our reps sells work that comes in closest to the estimated margin?

## Example agent output (fictional)

> Quick check: work orders only (contracts close out on a different cycle)? I'll
> use jobs marked complete this year unless you'd rather use won date.
>
> Closest to estimate (completed work orders, 2026 YTD, weighted by dollars):
>
> | Rep | Jobs | Est. margin | Actual margin | Gap |
> |---|---|---|---|---|
> | Jordan Vega | 212 | 61.8% | 62.4% | +0.6 pts |
> | Casey Lin | 145 | 58.1% | 60.3% | +2.2 pts |
> | Riley Shaw | 38 | 55.0% | 48.9% | −6.1 pts |
>
> Scope: won Work Orders with job status Complete and completion date in
> 2026, estimated vs actual gross margin summed per rep, change orders
> included. Per-job gaps are wider than the totals suggest (median about
> 7 pts), so "closest" by total and by typical job can differ.
