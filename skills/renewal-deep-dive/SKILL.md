---
description: Build a renewal recommendation for one property. Pull Capsa's renewal drilldowns (service-level price/hours comparisons, prior-year performance review) and full property context (margin by service type, payment behavior, penetration, open issues and notes), then synthesize a price/hours/terms recommendation memo with cited evidence. The agent proposes; the user decides. Use per property, usually after renewal-portfolio-triage.
---

# Renewal deep dive

One property, one decision: what should this renewal look like? Combine last
year's estimate-vs-actual performance with how the customer pays, what else
they buy, and how the relationship feels — into a memo the account owner can
act on.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Re-pricing a renewal from last year's estimate alone repeats last year's
mistakes. This skill assembles the evidence — did the contract actually make
its margin, where did hours run over, does the customer pay on time, is there
unsold enhancement potential, are there open complaints — and turns it into a
structured recommendation with every line cited to the datapoint it came from.

The output is analysis to support the user's pricing decision. It is never a
pricing instruction, and the user's judgment overrides every rule below.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section is the contract;
persist those inputs in the Team specifics block below, a system message, or a
wrapper script.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected with the renewal-opportunities and
  property-context capabilities available.
- One specific property is identified (resolve fuzzy names with
  `capsa_search_properties` first).
- The pricing guardrails below are configured, or the user is ready to supply
  them.

Skip it for portfolio questions (use **renewal-portfolio-triage**) or when the
user wants raw numbers without a recommendation.

## Required connected apps

- **Capsa MCP connector.** Provides renewal drilldowns and property context.
- Optionally a docs or email connector if the memo should leave chat — that
  delivery is approval-gated.

## Configuration

Shared with renewal-portfolio-triage — keep one copy (see its Team specifics):

- **Pricing guardrails.** Target gross margin %, expected labor-cost
  inflation %, default price-increase %, maximum increase % the agent may
  propose without flagging for management review.
- **Payment-risk thresholds** and **penetration target.**
- **Memo destination.** Chat by default; anywhere else is outbound and
  approval-gated.

All defaults are placeholders the team must set. If a guardrail is unset when
it's needed, ask — never assume an industry number.

## Workflow

### 1. Resolve the property (only if needed)

If the property reference is fuzzy, call `capsa_search_properties` and confirm
the right property with the user (see
[Resolving ambiguous names](../../reference/patterns/resolve-ambiguous-names.md)).

### 2. Pull renewal drilldowns

Call `capsa_get_renewal_drilldown` for the property:

- `performance_review` — prior-year estimated vs actual margin, cost and hours
  variance, projected cost, and a confidence level. Carry that confidence into
  everything downstream; partial-season actuals get an explicit caveat.
- `service_comparisons` — per-service price-per-hour and hours deltas between
  last year's contract and this year's renewal bid, with change tags.

If the property has renewals in more than one division, the tool will ask you
to pick one — confirm with the user rather than summing divisions.

### 3. Pull property context

Call `capsa_get_property_context` for the property. The context row already
carries the payment-behavior health check (current balance, past-due balance,
dollar-weighted days past due, average days late to pay) plus penetration and
satisfaction counts — triage those numbers first, like an analyst would:

- **All four payment measures healthy?** Skip the invoice drilldown entirely.
  Unhealthy? Pull the open-invoices drilldown to see which invoices drive it.
- Then only the other targeted `capsa_get_property_context_drilldown` calls
  the synthesis needs: gross margin by service type, the contract vs
  non-contract margin split (penetration detail), open complaints and issues,
  and last-touch activity.

If a drilldown isn't available on this connection, say so and proceed without
that signal — never fabricate it.

### 4. Synthesize — walk these rules in order

1. **Margin reality check.** Compare prior-year estimated margin % vs actual
   margin % vs the configured target. Note cost variance % and the review's
   confidence level.
2. **Price-adjustment floor.** If margin eroded or costs over-ran: proposed
   increase floor = cost variance % + configured labor inflation %. Cap the
   proposal at the configured max — and if the computed floor exceeds the max,
   do **not** silently cap; flag that pricing alone can't fix this within the
   guardrails and it's a scope or management conversation. If margin was
   healthy and costs in line: propose the team default increase.
3. **Hours/scope rebalance.** If hours over-ran, name the services driving it
   and present both options — price for the real hours, or rebalance the
   schedule/scope. If hours materially under-ran, present returning value as
   added scope vs holding price. Present options with numbers; don't pick.
4. **Payment behavior → terms, not just price.** A chronic late payer gets a
   terms option alongside price — deposit, shorter terms, autopay incentive —
   plus any outstanding late balance to resolve **before** the renewal
   conversation. These are options for the user, not contract advice.
5. **Penetration → upsell motion.** Low penetration + healthy margin + decent
   payer → recommend attaching an enhancement-proposal motion to the renewal
   touch. If non-contract margin is poor, flag that as an estimating problem
   to fix before selling more of it.
6. **Satisfaction gate.** Open complaints plus a price increase is a
   churn-risk combination — the memo must lead with "resolve first," and the
   price recommendation's confidence drops accordingly.
7. **Duplicate guard.** If the renewal is flagged a potential duplicate,
   present each active opportunity separately; never one summed forecast.

### 5. Draft the recommendation memo

Fixed shape: **Recommendation** (price % range, hours/scope option, terms
note, optional upsell) → **Evidence** (every line cites its datapoint and
which pull it came from) → **Risks & caveats** (confidence level, freshness,
open issues, timing) → closing line: "This is analysis to support your pricing
decision, not a pricing instruction."

### 6. Review with the user

The user accepts, adjusts (re-run the affected math at their number), or
rejects. Record the user's final call in the session summary.

### 7. Deliver (optional) and stop

If the memo goes to a doc, email, or message, post only after explicit
approval. The renewal-opportunities capability has no completion-write tool —
if the user wants the decision recorded somewhere external, produce it from
the user's stated decision, never from the draft.

## Stop rules

- **The user decides the price.** Never present the proposal as final or
  required.
- **Floor above the max guardrail → flag, don't silently cap.**
- **Missing guardrails → ask.** Never substitute "industry standard" numbers.
- **No invented data.** A signal a tool didn't return is omitted or asked
  about, never estimated.
- **Open complaints + proposed increase must be surfaced together.**
- **Potential duplicate → per-opportunity numbers only.**
- **Carry confidence and freshness.** The performance review's confidence level
  and the 24-hour data window appear in the memo.
- **Nothing leaves chat without approval; no fabricated completion record.**

## Example user prompt

> "Before I send the Maple Ridge HOA renewal, walk me through how that contract
> actually performed and what you'd change."

## Example agent output (fictional)

```
Renewal review — Maple Ridge HOA, Maintenance (renewal in Bidding, starts in
35 days; Capsa data may be up to 24 hours old)

RECOMMENDATION (for your decision — not a pricing instruction)
- Price: +7–9% on the maintenance contract. Your default is +4%; the floor
  here is last year's 4.1% cost overrun + your 3% labor inflation. Your max
  without management review is 10%.
- Hours: mowing ran 9% over estimate. Either price for the real hours
  (included in the range above) or trim the enhancement-bed schedule — both
  shown below.
- Terms: payment is healthy (≈6 days to pay, no late balance) — no change.
- Upsell: non-contract work is 4% of contract value against your 10% target,
  with contract margin at 38% — good candidate for an enhancement proposal
  alongside the renewal.

EVIDENCE
- Prior year: estimated margin 40%, actual 36.7% (performance review,
  confidence: strong — full season of actuals)
- Costs ran 4.1% over estimate, driven by Mowing (+9% hours) and Irrigation
  (+6% cost); Snow came in under (service comparisons)
- Payment: no late balance; ~6 days to pay dollar-weighted (payment behavior —
  all four measures healthy, so I skipped the invoice drilldown)
- Satisfaction: no open complaints; one issue closed in October (issues)
- Penetration: $3.4k non-contract on $84k contract = 4% (revenue mix)

RISKS & CAVEATS
- The renewal is still in Bidding 35 days before start — timing is a bigger
  risk than price right now.
- If you take the schedule-trim option instead of the full increase, margin
  recovers to roughly 40% at +5%.

This is analysis to support your pricing decision, not a pricing instruction.
How would you like to proceed — a number in that range, an adjustment, or the
scope option?
```

All names and figures above are fictional.

## Team specifics

<!--
  Persist your pricing guardrails (target GM%, labor inflation %, default and
  max increase %), payment-risk thresholds, penetration target, and memo
  destination here — shared with renewal-portfolio-triage; keep one copy.
  Re-pull after a connector upgrade.
-->
