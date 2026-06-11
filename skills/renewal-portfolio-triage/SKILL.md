---
description: Pull the Capsa renewal book for a scope (division, start-date window, optional branch, account owner, or property tags), tier each property with explainable rules — dollars at risk, time pressure, margin flags, payment and satisfaction risk, upsell upside — and present a ranked worklist the user prunes before any deep dive. Use at the start of a renewal cycle or for a recurring renewal review.
---

# Renewal portfolio triage

Pull the renewal book from Capsa, tier it with explainable rules, present a
ranked worklist, and hand the properties the user picks to the
**renewal-deep-dive** skill.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Renewal season is a prioritization problem: dozens of contracts, a few weeks,
and the expensive mistakes are letting a big renewal sit unbid until its start
date and re-sending last year's price on a job that lost money. This skill
turns the renewal book into a short, explainable worklist — every tier
placement reads back as a sentence the user can verify.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section is the contract;
persist those inputs in the Team specifics block below, a system message, or a
wrapper script.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the renewal-opportunities capability
  is available on this connection.
- The user is working a **set** of renewals — a division's book, a quarter's
  starts, an account owner's portfolio — not one property.
- The team has set (or is ready to set) the scope and threshold configuration
  below.

Skip it when the user asks about a single property (go straight to
**renewal-deep-dive**) or only wants raw pipeline numbers with no
prioritization.

## Required connected apps

- **Capsa MCP connector.** Provides the renewal book, property context, and
  contact context. Nothing else is required; if the user wants the worklist in
  a doc or message, that destination's connector is also needed and the post is
  approval-gated like any outbound.

## Configuration

All defaults below are placeholders — the team's numbers are the source of
truth. Never substitute industry benchmarks for unset values; ask.

- **Scope defaults.** Call `capsa_list_renewal_filter_options` to see the
  divisions, branches, account owners, statuses, and property tags available.
  Record which division IDs constitute "the renewal book," plus any standing
  branch/owner/tag filters.
- **Renewal window convention.** How far out the team works renewals (e.g.,
  contracts starting next quarter, or in the next 120 days).
- **Urgency window.** Days-to-start at which a renewal still in `New` or
  `Bidding` becomes act-now. A common starting point is 60 days; the user picks.
- **Pricing guardrails** (shared with renewal-deep-dive — keep one copy):
  target gross margin %, expected labor-cost inflation % for the coming year,
  default price-increase %, and the maximum increase % the agent may propose
  without flagging for management review.
- **Payment-risk thresholds.** Dollar-weighted days past due and/or late
  balance that counts as a poor payer (e.g., more than 15 days, or late
  balance over a set amount).
- **Penetration target.** Non-contract revenue as a % of contract value below
  which a property is underpenetrated (e.g., under 10%).
- **Enrichment policy.** Whether to always/ask/never run the property-context
  pass on the shortlist, and the shortlist cap (a common default is 15).

## Workflow

### 1. Learn the capability (only if needed)

If you haven't used the renewal-opportunities capability recently, call
`capsa_describe_capability` for `renewal_opportunities` once to confirm shape,
filters, and freshness. Skip on later runs in the same session.

### 2. Resolve the scope

Call `capsa_list_renewal_filter_options` and resolve the configured division /
branch / account-owner names to IDs (see the
[Resolving ambiguous names](../../reference/patterns/resolve-ambiguous-names.md)
pattern). Confirm the start-date window with the user in one line before
pulling.

### 3. Pull the renewal book — all of it

Call `capsa_find_renewals` with the resolved filters and window. Expect one row
per property/division: prior-year contract value and end date, the current
renewal's status breakdown, days to start, change tags (price/scope movement,
potential duplicates), contacts, and which rows have **no renewal started at
all**. Every page also carries the book-level scoreboard (total value, status
totals, rows without a renewal started), so totals are true from the first
call.

Work through the list the way a manager would — completely:

- Results come in pages (up to 100 rows). While the response says more rows
  remain, pull the next batch (advance the offset by the rows returned) until
  the book is covered. Tier as you go and accumulate.
- Rows arrive biggest prior-year dollars first, so the most consequential
  renewals are tiered in the first batch even while later pages load.
- For very large books, agree on slices with the user (by account owner or
  branch), finish a slice before starting the next, and report progress as
  "X of Y rows processed."
- If the pull comes back empty, check whether the team labels renewals under a
  different sales type — the response will list the available values; confirm
  with the user instead of assuming there are no renewals.

### 4. Tier the book (pass 1 — no extra calls)

Apply these rules using only the `capsa_find_renewals` output. A property gets
the highest tier it matches, with **every** matched signal listed. Sort within
tier by dollars at risk (prior-year value not yet Won), descending.

| Tier | Name | Rule |
|---|---|---|
| 1 | Act now — dollars at risk on the clock | Status still `New` or `Bidding` inside the urgency window; or no renewal started and the start date is inside the window; or a `Lost` the user hasn't acknowledged. |
| 2 | Economics need review before send | Any performance flag (margin at risk, cost or hours over expected); no price increase tagged (or a price decrease) on a renewal carrying a cost/hours flag; scope increase without matching price movement; or a potential duplicate (must be untangled — never present summed numbers for a duplicate). |
| 3 | Relationship / payment risk | Enrichment-pass signals: late balance or days past due over the configured thresholds; open complaints or issues. |
| 4 | Upside — upsell alongside renewal | No Tier 1–3 signals, penetration below target, payment healthy. A good renewal conversation to also sell enhancements into. |
| 5 | On track — monitor | Won, or Approved/Delivered with no flags and no enrichment hits. |

Report the scope scoreboard alongside: total book value, dollars at risk, and
rows with no renewal started. Retention so far is context for the user, not a
per-property tiering input.

### 5. Enrich the shortlist (optional, one batched call)

Per the configured enrichment policy, make **one** `capsa_get_property_context`
call covering Tier 1–2 plus anything the user asks about (respect the
shortlist cap). Add payment behavior, open complaints/issues, penetration, and
last-touch columns; promote/demote into Tiers 3–4 with stated reasons. If
enrichment is skipped, say plainly which signals were not checked.

### 6. Present the worklist

One scoreboard line, then a ranked list: tier, property, prior-year value,
status, days to start, plain-English signals, suggested next step. The user
prunes, reorders, or overrides tiers — overrides are accepted without
argument; tiering is a proposal.

### 7. Hand off

For each property the user picks, run **renewal-deep-dive**
(../renewal-deep-dive/SKILL.md). Do not call `capsa_get_renewal_drilldown` or
any property drilldown during triage — those are the deep dive's job, one
property at a time.

### 8. No completion record

The renewal-opportunities capability has no completion-write tool. The run ends
at the worklist and handoffs. If the user wants the worklist in a doc or
message, draft it and post only after explicit approval.

## Stop rules

- **Tiering is a proposal.** The user's ordering wins; never argue an override.
- **No drilldowns in triage.** `capsa_get_renewal_drilldown` and property
  drilldowns belong to the deep dive.
- **No partial book presented as full coverage.** If pages remain or a slice
  hasn't been processed, say exactly what has and hasn't been covered.
- **No invented thresholds.** Unset guardrails or risk thresholds mean ask,
  never assume an industry number.
- **Never sum a potential duplicate.** Present each active opportunity
  separately.
- **Freshness.** Capsa data may be up to 24 hours old — surface that whenever a
  start date is imminent or a payment figure drives the tier.
- **Nothing leaves chat without approval.**

## Example user prompt

> "Renewal season is starting for our maintenance book. Can you pull everything
> starting January through March and tell me which ones I should worry about
> first?"

## Example agent output (fictional)

```
Renewal book — Maintenance division, contracts starting Jan 1 – Mar 31
(Capsa data may be up to 24 hours old):

Scoreboard: 14 renewals · $612k prior-year value · $284k not yet won ·
retention so far 54%

Tier 1 — act now (dollars at risk on the clock)
1. Maple Ridge HOA — $84k prior-year · Bidding · starts in 35 days
   Signals: still in Bidding inside your 60-day urgency window
2. Stoneridge Grounds — $61k prior-year · no renewal started · starts in 48 days
   Signals: prior contract ends, nothing in the pipeline yet

Tier 2 — economics need review before send
3. Cedar Creek Lawn Care — $47k prior-year · Approved · starts in 70 days
   Signals: costs ran over expected last year; no price increase tagged
4. Greenleaf Landscaping — $39k prior-year · Bidding · starts in 66 days
   Signals: potential duplicate — two active opportunities map to last
   year's contract; shown per opportunity, not summed

Tier 3 — payment/relationship (from the enrichment pass on the four above)
   Cedar Creek also shows a $9.8k late balance, ~22 days past due
   dollar-weighted — flagged for a terms conversation in the deep dive.

Tiers 4–5: 10 renewals on track or upsell candidates — list on request.

Want me to start a deep dive on Maple Ridge HOA?
```

All names and figures above are fictional.

## Team specifics

<!--
  Persist your division/branch/owner scope IDs, renewal window convention,
  urgency window, pricing guardrails (target GM%, labor inflation %, default
  and max increase %), payment-risk thresholds, penetration target, and
  enrichment policy here. Keep the tier rules and stop rules in sync with the
  cookbook; re-pull after a connector upgrade.
-->
