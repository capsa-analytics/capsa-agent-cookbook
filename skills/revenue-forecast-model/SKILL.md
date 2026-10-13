---
description: Build, explain, or tune a forward production revenue forecast from Aspire data with the Capsa connector — layer earned, pending, scheduled, backlog, weighted open pipeline, and expected renewals by certainty, settle recognition timing and close-rate choices with the user, and present period totals with the assumptions and reconciliation checks beside them. Use when a team wants its own forecast model, wants to understand what a forecast assumes, or wants to change one assumption and see the effect.
---

# Revenue forecast model

Build a production revenue forecast the team can see into and adjust: a
stack of layers ordered by certainty, each with a stated timing rule and
probability, assembled from current Aspire records through the Capsa
connector. The agent proposes every assumption from the team's own history;
the user confirms each one before it drives a number.

The thinking behind the layers, timing, close rates, and renewals is in
[FRAMEWORK.md](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/revenue-forecast-model/FRAMEWORK.md).
Read it once; this file is the procedure.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Most forecasts fail on framing, not math: pipeline added on top of scheduled
work that already covers it, a stale proposed start treated as work in
progress, a close rate measured on this month's wins over this month's
proposals. This skill makes each of those choices explicit, measures the
inputs from the team's history, and shows the assumptions next to the
totals so a manager can argue with one assumption instead of the whole
number.

The steps are the same whether this runs as an installed skill, is pasted
into another agent, or is run ad hoc. The "Configuration" section is the
contract; persist those inputs in the Team specifics block below, a system
message, or a wrapper script.

## When to use

- The team wants its own forecast model, built from its Aspire data, that it
  can tune without a vendor.
- A manager asks what a forecast assumes, or why this month's number moved.
- The user wants to change one assumption (count Bidding proposals, turn
  expected renewals off, use the probability field) and see the effect.
- A sales goal needs a bookings view beside the revenue view.

Hand off when the question is really one of these:
[answer-a-data-question](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/answer-a-data-question/SKILL.md)
for a single total or rate,
[scorecard-review](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/scorecard-review/SKILL.md)
for close-rate trends,
[renewal-portfolio-triage](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/renewal-portfolio-triage/SKILL.md)
for working the renewals themselves.

## Required connected apps

- **Capsa MCP connector** with the Aspire records capability enabled
  (`capsa_describe_aspire_resources`, `capsa_find_aspire_records`,
  `capsa_summarize_aspire_records`). Read-only against Capsa and Aspire;
  nothing in this skill writes to either.
- Optional: a spreadsheet or docs connector to hold the model and its
  assumptions sheet, approval-gated like any outbound.

Without Aspire records on the connection, the Sales Scorecard
(`capsa_query_scorecard`) still supplies open pipeline and close-rate history
for the pipeline layer; say plainly that the ticket-level layers are not
available and offer that partial view.

## Configuration

All values below are starting points, not defaults to assume silently. Each
one changes the forecast; read the recorded choices back to the user before
every build and ask about any that are unset.

- **Scope.** Branches and divisions in the forecast. Resolve names with the
  connector's filter options, never from memory.
- **Horizon and grain.** For example 12 months monthly, with the next 8 weeks
  weekly.
- **Pipeline statuses.** Which open `OpportunityStatus` values count as
  pipeline. Starting point: Delivered only.
- **Probability method.** Manual field, flat rate, empirical by segment, or
  factor model (FRAMEWORK §6.2), plus the history window in months and
  whether rates are dollar-weighted.
- **Close-rate denominator.** Won + Lost, or Won + Lost + Delivered, by
  proposed-date cohort; whether never-sent proposals are excluded.
- **Timing basis.** Whether `AnticipatedCloseDate` is trusted; the default lag
  for undated proposals.
- **Staleness.** Created-date lookback and past-start cutoff for proposals;
  months-before-current-month cutoff for past-due backlog; whether undated
  backlog is included.
- **Contract spread.** Even by month, or a seasonal curve.
- **Expected renewals.** On or off; renewal rate source; planned price
  increase; whether late renewals (shifted start already passed) are dropped.
- **Capacity caps.** Off, or hours per month-of-year by branch and division.
- **Today.** The business date and its time zone. Scheduled dates are
  calendar labels and are never shifted.

## Workflow

### 1. Learn the resources (once per session)

Call `capsa_describe_aspire_resources` with no arguments, then for
`Opportunities`, `WorkTickets`, `WorkTicketVisits`, `WorkTicketRevenues`, and
`WorkTicketTimes` with `fields: "dates"` and `"measures"`. Read the
`date_basis_map`, `forecast_layers`, `earned_revenue`, `scheduled_visits`,
`labor_acceptance`, `close_rate_cohort`, and `opp_status_canonical`
concepts. Carry every `guidance` line the responses return into the
assumptions sheet.

### 2. Confirm the frame

State the scope, horizon, grain, and today's date in one line and get a
yes. Then walk the Configuration list: for each unset item, propose the
starting point with a one-sentence reason and ask. Batch the questions; do
not ask one at a time across many turns.

### 3. Measure the inputs from history

Use `capsa_summarize_aspire_records` for every total, never paged rows added
by hand; use `capsa_find_aspire_records` only for per-record lookups such as
the earliest accepted labor date on a job's tickets:

- **Close rates** per segment the team chose: count and sum of
  `EstimatedDollars` on `Opportunities` grouped by `OpportunityStatus` within
  the segment, filtered to Won, Lost (and Delivered if in the denominator)
  with `ProposedDate` in the history window. Compute the ratio; note segments
  with too little history and which parent segment they fall back to.
- **Proposed→won days** and **won→first-work days**, from Won opportunities
  in the window (first work from the earliest accepted labor date on the
  job's tickets).
- **Typical daily production hours** for a job in each division: accepted
  `WorkTicketTimes` hours per ticket per day actually worked, averaged over
  the history window.
- **Retention rate** for expected renewals, from prior-year contracts that
  did or did not get a Won successor at the same property and division.

Show the measured values and let the user override any of them. An override
is recorded as an assumption with its reason.

### 4. Build the ticket layers

For Open and Scheduled tickets in scope:

1. Remaining revenue = `Price − EarnedRevenue`, floored at zero; remaining
   hours = `HoursEst − accepted hours − pending hours`, floored at zero, where
   both come from `WorkTicketTimes` (accepted entries, and unaccepted entries
   on the same Open or Scheduled ticket). Pending hours leave the pool here
   because step 5 shows them as their own layer.
2. Future visits (`WorkTicketVisits.ScheduledDate` ≥ today): allocate
   remaining value across them by visit hours, netting labor once per
   ticket-day (accepted labor dated that day; for today only, also the
   unaccepted labor dated today, so it is not both pending and scheduled).
   These tickets are **scheduled**.
3. Every other ticket with remaining value is **backlog**: current (plan date
   today or later, spread from it), past due (plan date before today, spread
   from today, excluded beyond the staleness cutoff), or undated (per the
   configuration).
4. Earned revenue by `RevenueMonth` fills the closed periods and the current
   period to date; amounts dated after today are shown where dated and
   labelled posted ahead.
5. Pending-acceptance labor (unaccepted `WorkTicketTimes` on Open or Scheduled
   tickets, current and prior month) is its own layer in the hours view.

### 5. Build the pipeline layer

For open opportunities matching the configured statuses, types, and
staleness rules:

1. Resolve probability per the chosen method; Won is never in this layer.
2. Resolve the estimated win date with the decision table in FRAMEWORK §6.3,
   then the work-start date (§6.4): add won→first-work days, floor at a future
   `StartDate`, floor at today.
3. Contracts with a usable `StartDate`/`EndDate` spread across the term;
   everything else spreads from work-start over the configured duration.
4. Keep gross and weighted side by side. Count the rows that used the
   last-resort date and the rows excluded as stale; both go in the report.

### 6. Build expected renewals (if on)

Completed or active contracts whose one-year-shifted term overlaps the
horizon, with no overlapping Contract opportunity at the same property and
division that is not Lost or cancelled (a Lost renewal attempt does not
suppress the candidate; list it as a signal and let the team decide): shift, apply the price increase to revenue, apply the renewal rate
to revenue and hours. List candidates whose shifted start already passed.

### 7. Assemble, cap, and reconcile

Sum the layers per period, branch, and division. If capacity caps are on,
push expected renewals, then pipeline, then backlog later in that order
until each period fits; never move earned, pending, or scheduled work. Then
run every check in FRAMEWORK §11 and report any that fail; a failed check
stops the build until the user decides.

### 8. Present

Lead with the period table (earned to date, scheduled, backlog, weighted
pipeline, expected renewals, total, and gross pipeline for context), then:

- the assumptions sheet: every Configuration value with measured vs.
  overridden and the reason;
- the review lists: past-due backlog, stale exclusions, last-resort-dated
  proposals, future-dated actuals, late renewals, each with counts;
- the reconciliation results;
- one line on freshness (connector data may be up to 24 hours old).

If the user wants the model in a sheet or doc, draft it and post only after
approval. Offer a sensitivity line ("counting Bidding proposals adds $X to
Q3 weighted") when the user asks what-if; rates measured on delivered
proposals overstate earlier statuses, so discount them or measure the rate
by status, and say which.

## Stop rules

- Aspire records are not enabled on the connection: say so, offer the
  scorecard-only pipeline view, and offer to log a feature request.
- A Configuration value is unset and the readings differ materially: ask
  before building; never pick silently.
- A reconciliation check fails: report it and stop; do not adjust layers to
  make it pass.
- A segment's close-rate history is too thin and no fallback is agreed: ask.
- Never fill missing dates, prices, or hours with invented values; count
  and list them instead.
- Never present weighted pipeline or expected renewals as booked revenue.

## Example user prompt

> Build us a 12-month revenue forecast for the Maintenance and Enhancement
> divisions in the North branch, and show me what it assumes.

## Example agent output (fictional)

> Frame: North branch, Maintenance + Enhancement, May 2026 – Apr 2027 by
> month (May shows earned to date plus what remains), today 2026-05-20.
> Before I build, four choices that move the number:
>
> 1. Pipeline statuses: **Delivered only** (proposals that reached the
>    customer), or include Bidding?
> 2. Probability: I measured dollar close rates by division and sales type
>    over the last 18 months — Maintenance/Renewal 82%, Maintenance/New 38%,
>    Enhancement/New 44% (Enhancement/Renewal has 6 proposals, so it falls
>    back to Enhancement overall, 45%). Use these, or your reps' probability
>    field?
> 3. Expected renewals: on, with measured retention 85% and the 4% increase
>    you planned?
> 4. Stale proposals: drop open proposals created more than 15 months ago
>    (that is 11 proposals, $96k gross)?
>
> *User: Delivered only, measured rates, renewals on, drop them.*
>
> | Month | Earned | Scheduled | Backlog | Pipeline (wtd) | Renewals (wtd) | Total | Pipeline gross |
> |---|---:|---:|---:|---:|---:|---:|---:|
> | May 2026 | $96,000 | $38,200 | $41,000 | $6,500 | — | $181,700 | $14,000 |
> | Jun 2026 | — | $212,400 | $31,900 | $48,600 | $9,100 | $302,000 | $118,000 |
> | Jul 2026 | — | $198,100 | $22,700 | $71,200 | $12,400 | $304,400 | $164,000 |
> | Aug 2026 | — | $171,300 | $18,200 | $64,900 | $12,400 | $266,800 | $151,000 |
> | … | | | | | | | |
>
> Assumptions: 14 recorded, all measured or accepted as proposed; none
> overridden. Review lists: 7 past-due backlog tickets ($41k, in May) need
> rescheduling; 4 proposals
> used the 90-day default date; 2 tickets have revenue posted ahead of today
> ($3.2k, August). Checks: all 7 passed. Data is as of yesterday.
>
> Want the sheet? I'll draft it with the assumptions tab and post it to your
> drive once you approve.

## Team specifics

<!--
  Record the Configuration choices here with dates and reasons, plus the
  branch/division IDs in scope, so each build reads the same model. Re-pull
  this skill after a connector upgrade.
-->
