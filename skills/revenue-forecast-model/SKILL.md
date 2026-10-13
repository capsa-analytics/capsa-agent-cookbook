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
every build and ask about any that are unset. FRAMEWORK §12 is the same list
with the question to ask for each.

- **Scope.** Branches and divisions in the forecast. Resolve names with the
  connector's filter options, never from memory.
- **Horizon and grain.** Starting point: 12 months monthly, with the next 8
  weeks weekly (earned revenue is monthly only; weekly applies to labor and
  visits).
- **Pipeline statuses.** Which open `OpportunityStatus` values count as
  pipeline. Starting point: Delivered only. Any earlier status included (New,
  Bidding, Approved) gets its own by-status rate or a disclosed discount.
- **Opportunity types and exclusions.** Contract and Work Order; exclude zero
  `EstimatedDollars`, never-sent proposals (`ProposedDate` = `LostDate`), and
  optional service lines if the team's estimate convention excludes them;
  proposals with no `ProposedDate` are excluded or given the last-resort date
  and listed (team's choice).
- **Probability method.** Manual field, flat rate, empirical by segment, or
  adjusted model (FRAMEWORK §6.2). Starting point: empirical by segment,
  dollar-weighted, with the history window in months.
- **Close-rate denominator.** Starting point: Won + Lost + Delivered by
  proposed-date cohort, never-sent excluded.
- **Timing basis.** Whether `AnticipatedCloseDate` is trusted (starting point:
  off until reps maintain it); the default lag for undated proposals
  (starting point: 90 days); where the past-start row sits in the FRAMEWORK
  §6.3 ordering.
- **Staleness.** Created-date lookback (starting point: 12–18 months) and
  past-start cutoff for proposals, neither applied to contracts with a usable
  future end date; months-before-current-month cutoff for past-due backlog;
  undated backlog included (rolled forward from today) or excluded.
- **Contract spread.** Even by month (starting point), service-occurrence
  shape, or the prior year's earned curve. For a term already begun, drop the
  elapsed months and keep the current month's full share (starting point),
  pro-rate the current month by remaining days, or re-spread the elapsed
  share over the remaining months.
  When a term starts before the calculated work-start, keep the contract dates
  and list the conflict (starting point) or begin at the work-start and
  compress the term.
- **Unscheduled work duration.** For work orders and contracts without a
  usable schedule, in order of preference: measured average duration of
  comparable completed tickets, the division's average, or remaining hours ÷
  typical daily production hours. One business day minimum.
- **Expected renewals.** On (starting point) or off; renewal rate from
  measured retention for the scope; planned price increase; late renewals
  (shifted start already passed) dropped and listed (starting point).
- **Delivered treated as Won.** No, unless the business explicitly decides so.
- **Capacity caps.** Off (starting point), or forecast hours per month-of-year
  by branch and division; confirm whether route hours are per day or per week.
- **Today.** The business date and its time zone. Scheduled dates are
  calendar labels and are never shifted.

## Workflow

The FRAMEWORK sections named in each step are the normative rules; the steps
below are the order of operations and the qualifiers most often dropped.

### 1. Learn the resources (once per session)

Call `capsa_describe_aspire_resources` with no arguments, then for
`Opportunities`, `WorkTickets`, `WorkTicketVisits`, `WorkTicketRevenues`,
`WorkTicketTimes`, and (when caps or the route-schedule check apply) `Routes`
with `fields: "dates"` and `"measures"`. Read the `date_basis_map`,
`forecast_layers`, `earned_revenue`, `scheduled_visits`, `labor_acceptance`,
`close_rate_cohort`, `opp_status_canonical`, and `job_status` concepts. Carry
every `guidance` line the responses return into the assumptions sheet.

### 2. Confirm the frame

State the scope, horizon, grain, and today's date in one line and get a
yes. Then walk the Configuration list: for each unset item, propose the
starting point with a one-sentence reason and ask. Batch the questions; do
not ask one at a time across many turns.

### 3. Measure the inputs from history (FRAMEWORK §6.2, §6.3)

Use `capsa_summarize_aspire_records` for every total, never paged rows added
by hand; use `capsa_find_aspire_records` only for per-record lookups such as
the earliest accepted labor date on a job's tickets:

- **Close rates** per segment the team chose: count and sum of
  `EstimatedDollars` on `Opportunities` grouped by `OpportunityStatus`,
  filtered to the denominator statuses with `ProposedDate` in the history
  window, never-sent handled per the configuration. Scope history to the
  forecast's own scope (an excluded division never pools into the global
  anchor); never use `JobStatusName` in historical rates; fall back from a
  thin segment to its parent, then to the global rate, and record which
  segments fell back.
- **Proposed→won days**, from Won opportunities that have both
  `ProposedDate` and `WonDate`; **won→first-work days**, from `WonDate` to
  the earliest accepted labor date, or the first earned revenue month when
  labor is thin.
- **Typical daily production hours** for a job in each division: accepted
  `WorkTicketTimes` hours per ticket per day actually worked, averaged over
  the history window.
- **Average work duration** by division and opportunity type: business days
  from first to last accepted labor date on completed tickets in the window,
  with a size band (by `Price`) when the team wants comparable-ticket
  durations.
- **Retention rate** for expected renewals, from prior-year contracts that
  did or did not get a Won successor at the same property and division.

Show the measured values and let the user override any of them. An override
is recorded as an assumption with its reason.

### 4. Build the ticket layers (FRAMEWORK §3, §4, §5, §10)

For Open and Scheduled tickets on won opportunities in scope (Complete and
Canceled tickets contribute earned history only):

1. Remaining revenue = `Price − EarnedRevenue`, floored at zero, with no date
   filter on the earned amount. Remaining hours = `HoursEst − accepted hours −
   pending hours`, floored at zero, both from `WorkTicketTimes` (accepted
   entries, and unaccepted entries on the same ticket); pending hours leave
   the pool here because step 4.5 shows them as their own layer. Check
   `HoursAct` against the accepted sum before relying on it; unaccepted labor
   on Complete or Canceled tickets is neither actual nor pending.
2. **Scheduled**: tickets with at least one future visit
   (`WorkTicketVisits.ScheduledDate` ≥ today) that still has uncovered hours
   after netting. Net once per ticket-day: sum the day's visit hours, subtract
   accepted labor dated that day (plus unaccepted labor dated today, for today
   only), floor at zero, allocate the remainder across that day's visits.
   Scheduled hours are the uncovered visit hours themselves, never the
   remaining estimate; allocate remaining revenue across the future visits by
   visit hours (evenly per visit if hours are not maintained). When uncovered
   visit hours and the remaining estimate differ, list the ticket as over- or
   under-scheduled; do not force either to match the other.
3. **Backlog**: every other ticket with remaining revenue or hours, classified
   by plan date (`ScheduledStartDate`, else `AnticStartDate`) against today,
   never against the first of the month: current (plan date today or later,
   spread from it), past due (before today, spread from today, excluded beyond
   the staleness cutoff and listed), or undated (per the configuration).
   Spread over business days using the unscheduled-work duration from the
   configuration, minimum one day.
4. **Earned** revenue by `RevenueMonth` fills closed periods and the current
   period to date. Amounts dated after today are shown in their period
   labelled posted ahead, excluded from "year to date", never hidden or
   reclassified, and the tickets are listed. Through the connector this is
   visible only when `RevenueMonth` is a future month; labor after today is
   visible by day.
5. **Pending acceptance**: every unaccepted `WorkTicketTimes` entry on an Open
   or Scheduled ticket, shown in the period it is dated as its own layer in
   the hours view (its revenue stays inside the ticket's remaining value), so
   every hour step 4.1 removed from the pool appears somewhere. Entries older
   than the prior month are also listed for cleanup.
6. Closed periods show only earned revenue, accepted hours, and pending hours
   dated in them.

### 5. Build the pipeline layer (FRAMEWORK §6)

For open opportunities matching the configured statuses, types, exclusions,
and staleness rules (a stale date means the work slipped, not that it is
underway):

1. Resolve probability to the most specific segment with enough history, per
   the chosen method. Won is 100% and never in this layer; Delivered is not
   Won; any earlier status gets its by-status rate or disclosed discount.
2. Resolve the estimated win date with the FRAMEWORK §6.3 table in the
   configured order, then the work-start date (§6.4): add won→first-work
   days, floor at a future `StartDate`, floor at today.
3. A contract has a usable schedule when `StartDate` and `EndDate` are both
   present, end ≥ start, end ≥ today: spread across the term regardless of a
   stale close date; drop, pro-rate, or re-spread the elapsed share per
   the configuration so nothing lands before the current period; list terms that
   start before the calculated work-start (or compress them, if that was the
   choice). Everything else spreads from work-start over the unscheduled-work
   duration measured in step 3.
4. Weighted revenue and hours = gross × probability, same spread. Keep gross
   and weighted side by side. Count the rows that used the last-resort date,
   the rows with no `ProposedDate`, and the rows excluded as stale; all three
   go in the report.

### 6. Build expected renewals, if on (FRAMEWORK §7)

Candidates: Contract opportunities whose job is active or complete, with
`StartDate` before today and valid dates, whose one-year-shifted term overlaps
the horizon. Suppress a candidate when a Contract opportunity at the same
property and division that is not Lost or cancelled overlaps the shifted term;
a Lost renewal attempt does not suppress, and is listed as a signal. Shift
start and end one year, keep the source contract's shape and hours, multiply
revenue by (1 + price increase), multiply revenue and hours by the measured
retention rate. A candidate whose shifted start is already behind today with
no future contract is treated as not renewed: $0 forecast, listed.

### 7. Assemble, cap, and reconcile (FRAMEWORK §9, §10, §11)

Sum the layers per period, branch, and division. If capacity caps are on,
push expected renewals, then pipeline, then backlog later in that order until
each period fits; never move earned, pending, or scheduled work. Verify that
no scheduled, backlog, pipeline, or renewal amount lands before the current
period. Then run every check in FRAMEWORK §11 and report any that fail. A
failed check stops the build until the user decides; layers are never
adjusted to make a check pass, and only capacity pushes move layers.

### 8. Present

Lead with the period table (earned to date, scheduled, backlog, weighted
pipeline, expected renewals, total, and gross pipeline for context), then:

- the assumptions sheet: every Configuration value with measured vs.
  overridden and the reason;
- the review lists, each with counts: past-due backlog, stale exclusions,
  last-resort-dated and no-`ProposedDate` proposals, future-dated actuals,
  over-scheduled tickets, contract-date vs work-start conflicts, late
  renewals, and Lost renewal attempts;
- the reconciliation results;
- a note when per-division totals differ between layers, because tickets and
  visits carry the operations division from the service line while pipeline
  and renewals carry the opportunity's sales division;
- one line on freshness (connector data may be up to 24 hours old).

**Sales (bookings) view, on request** (FRAMEWORK §8): bucket Won rows by
`WonDate`, never clamped; bucket open rows by estimated win date, clamped to
the current month when past; same probabilities; present it as a second
output and never add it to the revenue forecast.

If the user wants the model in a sheet or doc, draft it and post only after
approval. Offer a sensitivity line ("counting Bidding proposals adds $X to
Q3 weighted") when the user asks what-if, using the by-status or discounted
rate the configuration names, not the delivered-proposal rate.

## Stop rules

- Aspire records are not enabled on the connection: say so, offer the
  scorecard-only pipeline view, and offer to log a feature request.
- A Configuration value is unset and the readings differ materially: ask
  before building; never pick silently.
- A reconciliation check fails: report it and stop; do not adjust layers to
  make it pass.
- A segment's close-rate history is too thin and no fallback is agreed: ask.
- Never fill missing dates, prices, or hours with invented values; the only
  fallbacks are the configured, disclosed ones (last-resort proposal date,
  undated backlog rolled forward), and those rows are counted and listed.
- Never hide or reclassify future-dated actuals; never cap scheduled hours at
  the estimate; never shift `ScheduledDate` by time zone; never roll Won work
  forward; never treat Delivered as Won without an explicit decision.
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
> | Aug 2026 | $3,200 (posted ahead) | $171,300 | $18,200 | $64,900 | $12,400 | $270,000 | $151,000 |
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
