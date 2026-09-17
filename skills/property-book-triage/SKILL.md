---
description: Morning triage over a property book — start with capsa_get_attention_queue for a fixed "what needs my attention today and why" ranking, broaden with capsa_query_property_book and server-side metric_filters for specific thresholds (penetration, margin, late AR), then pull capsa_get_property_context on the shortlist before handing off to a follow-up, note, or renewal recipe. Use for a recurring daily or weekly sweep over a branch, account-owner, or tagged property set — not a single-property question.
---

# Property book triage

Start the day with a ranked "what needs attention" queue, broaden it with
specific thresholds the fixed queue doesn't cover, then hand the properties
that need action to the recipe that actually does something about them.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

A property book is too big to read end to end every morning, and the
properties that need attention today aren't always the ones at the top of a
revenue report. This skill combines Capsa's own opinionated triage order
with a configurable metric sweep, so a manager gets a short, explained list
instead of a spreadsheet.

The steps are the same whether this runs as an installed skill, is pasted
into another agent, or is run ad-hoc. The "Configuration" section is the
contract; persist those inputs in the Team specifics block below, a system
message, or a wrapper script.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the property-context capability is
  available on this connection.
- The user wants a recurring or broad sweep over a book — a branch, an
  account owner's properties, a tagged set — not a single property they
  already have in mind.
- The team's metric thresholds below are set, or the user is ready to set
  them.

Skip it when the user already has one property in mind — go straight to
`capsa_get_property_context`, or to
[renewal-deep-dive](../renewal-deep-dive/) if it's a renewal question.

## Required connected apps

- **Capsa MCP connector.** Provides the attention queue, the property book,
  and single-property context. This capability is read-only — nothing here
  sends or saves anything on its own. Hand-off recipes (below) bring their
  own connectors when the next step needs one.

## Configuration

All defaults below are placeholders — the team's numbers are the source of
truth. Never substitute an industry benchmark for an unset value; ask.

- **Scope defaults.** Call `capsa_list_property_context_filter_options` to
  see the branches, account owners, and tags available. Record which
  branch/account-owner/tag values constitute "the book" for a recurring run.
- **Attention queue page size.** 1–100, default 25 — how many rows to pull
  per call before deciding there's enough to work with.
- **Metric sweep thresholds.** The specific conditions the fixed attention
  queue doesn't filter on but the team wants checked every run — e.g.
  `penetration_percent lt 20`, a `gross_margin_percent` floor, or
  `ar_late_outstanding gt 0`. Call `capsa_list_property_context_filter_options`
  for the full `property_book_metric_filter_metrics` vocabulary.
- **Enrichment shortlist cap.** How many properties get a full
  `capsa_get_property_context` pull in one pass (a common default is 15).
- **Hand-off preferences.** Which recipe a flagged property typically goes
  to — [proposal-followup-batch](../proposal-followup-batch/) for
  outstanding follow-ups, [property-plan-builder](../property-plan-builder/)
  or [property-site-update](../property-site-update/) for notes and
  customer-facing updates, [renewal-portfolio-triage](../renewal-portfolio-triage/)
  for renewal-flagged properties.

## Workflow

### 1. Learn the capability (only if needed)

If you haven't used property context recently, call
`capsa_describe_capability` for `property_context` once to confirm shape and
filters.

### 2. Resolve the scope

Call `capsa_list_property_context_filter_options` and resolve the configured
branch / account-owner / tag values to IDs (see the
[Resolving ambiguous names](../../reference/patterns/resolve-ambiguous-names.md)
pattern).

### 3. Pull the attention queue first

Call `capsa_get_attention_queue` with the resolved `branch_ids` /
`account_owner_ids` / `property_tags`. This is Capsa's own opinionated
triage order — **not configurable** — so present it as-is:

- Order: health group ascending (`at_risk`, then `needs_attention`, then
  `healthy`, then `no_health_set`), then contract value in production
  descending, then property ID.
- Report the scoreboard (`at_risk_count`, `needs_attention_count`,
  `healthy_count`, `no_health_set_count`, `property_count_in_scope`) — it's
  computed over the whole filtered scope, not just the page returned.
- For each row, read the "why" straight off the response: `health.summary`,
  the `signals` block (open issues/complaints, stale-activity flag, late AR,
  next renewal date, days since last touch), and `top_recommendation` when
  present (Capsa's single highest-signal pending suggestion, at most 7 days
  old — never treat it as a complete task list, and it's `null` for most
  rows).
- Page through (`page.next_cursor`) while `has_more` is true and the user
  wants more than the first page.

### 4. Broaden with a metric sweep (optional)

The attention queue doesn't filter by penetration, a specific margin floor,
or a specific AR threshold — it has one fixed order by design. For those,
call `capsa_query_property_book` with the configured `metric_filters`,
sorted by whichever field matters most (e.g. `penetration_percent` ascending,
`ar_late_outstanding` descending). Disclose two things every time you use
this tool:

- **Mixed basis.** `gross_margin_percent`, `total_revenue`,
  `penetration_percent`, and the two work-order margin fields reflect the
  trailing 365 days. `active_contract_value`, `next_contract_end_date`,
  `health_status`, `ar_outstanding`, `ar_late_outstanding`,
  `ar_weighted_days_past_due`, and `days_late_to_pay` are point-in-time as of
  today. Don't describe the whole row as one snapshot age.
- **Standard definitions, not the team's customized ones.** Both this tool
  and the attention queue run server-side over the whole book using Capsa's
  standard metric definitions. A company that has customized which
  contracts, issue categories, or activity types count toward its Command
  Center screen may see small differences there — say so if the user
  compares the two.

If the sweep sets `filters.division_ids`, that's an advanced lens, not a
plain filter: revenue, margin, contract value, and dates then reflect only
that division's work at each property, while open issues, complaints,
last-touch, and health stay whole-property. The response carries an explicit
warning when this applies — repeat it to the user and never combine a
division-scoped figure with a whole-property one.

### 5. Merge and present the worklist

Combine the attention-queue rows and any metric-sweep hits into one list,
noting which source flagged each property and why (a property can appear in
both). The user prunes, reorders, or adds — this is a proposal, not a
verdict.

### 6. Enrich the shortlist (one batched call)

For the properties the user wants to act on now (respect the configured
cap), call `capsa_get_property_context` for single-property depth: contacts,
satisfaction detail, receivables, revenue mix, and `available_drilldowns`
for anything that needs a closer look. Don't pull drilldowns during the
broad sweep — that's this step's job, one property at a time.

### 7. Hand off, and stop

For each property the user wants to act on, hand off to the recipe that
matches the need — outstanding follow-ups, a plan or customer update, or a
renewal deep dive (see Configuration). This skill's own capabilities have no
completion-write tool; nothing is recorded as done here. If the user wants
the worklist itself in a doc or message, draft it and post only after
explicit approval.

## Stop rules

- **The attention queue's order is the product.** There is no `sort_by` for
  `capsa_get_attention_queue` — present it in the order returned. If the
  user wants a specific sort, use `capsa_query_property_book` instead.
- **State both freshness bases.** Revenue/margin figures are trailing
  365 days; contract value, AR, and health figures are point-in-time as of
  today. Never present a mixed row as one snapshot age.
- **Standard definitions, disclosed.** Neither tool applies a company's
  Command Center metric customizations — say so if a number might look
  different from what the app shows.
- **Division filter is a lens on property book, not a plain filter.** Surface
  the response's warning whenever `division_ids` is set, and never combine a
  division-scoped figure with a whole-property one.
- **No invented thresholds.** Unset metric thresholds mean ask the user,
  never assume an industry number.
- **No drilldowns during the broad sweep.** Both triage tools return summary
  rows only — pull `capsa_get_property_context` (and its drilldowns) for the
  shortlist, one property at a time.
- **`top_recommendation` is a hint, not a task list.** It's at most 7 days
  old and often `null` — never imply it covers everything that needs doing.
- **Nothing leaves chat without approval**, and hand-off recipes carry their
  own approval and evidence-gated completion rules — don't shortcut them.

## Example user prompt

> "Good morning — what needs my attention today across my properties?"

## Example agent output (fictional)

```
Attention queue — your book (Capsa data: contract value/AR/health are as of
today; revenue and margin figures below are trailing 365 days):

Scoreboard: 3 at risk · 9 needs attention · 118 healthy · 6 no health set ·
136 properties in scope

AT RISK
1. Riverbend Office Park — $96k in production · health: red — "Crew turnover
   causing missed visits three weeks running" · 3 open issues, 1 complaint ·
   late balance $1,250 (~18 days weighted) · suggested: review overtime
   spend on this route (High)

NEEDS ATTENTION
2. Cedar Creek Lawn Care — $47k in production · health: yellow — "Irrigation
   complaints trending up" · stale-activity flag: no update on an open issue
   in 4+ days

Broadening with your usual sweep (penetration under 20%, late AR over $0):
3. Stoneridge Grounds — penetration 3.1% against a healthy 41% margin — good
   upsell candidate, not urgent today.

Want me to pull full context on Riverbend and Cedar Creek and set up
follow-ups?
```

All names and figures above are fictional.

## Team specifics

<!--
  Persist your branch/account-owner/tag scope, attention-queue page size,
  metric-sweep thresholds, enrichment shortlist cap, and hand-off recipe
  preferences here. Keep the steps and stop rules in sync with the cookbook;
  re-pull after a connector upgrade.
-->
