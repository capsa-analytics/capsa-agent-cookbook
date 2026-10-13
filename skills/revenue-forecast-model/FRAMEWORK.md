# Revenue forecast framework for Aspire data

This is the thinking behind a production revenue forecast built from Aspire
records: what the forecast answers, how to layer work by certainty, when
revenue should be recognized, how to time and weight open pipeline, and which
decisions a team has to make for the numbers to mean anything. The companion
[SKILL.md](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/revenue-forecast-model/SKILL.md)
is the procedure an agent follows; this page is the why.

It is a framework, not a fixed model. Every choice below is marked as a
**starting point** the team can change. Where the Capsa app's own forecast
makes one of these choices, it is one reasonable implementation of this
framework, not the only one. Nothing here is a statement of how any
particular product computes it; the checks in section 11 are how you hold any
implementation, including your own, to account. Aspire field names appear so the model can be
rebuilt from the Capsa connector's Aspire records tools or from Aspire's own
reports; the [field appendix](#appendix-aspire-fields-the-model-uses) lists
them in one place.

## 1. What the forecast answers

A production revenue forecast answers: **how much revenue will we recognize in
each future period, by branch and division, and how sure are we?**

That is a different question from three neighbours, and mixing them is a
common forecasting error in Aspire data:

| Question | Date basis | Aspire source |
| --- | --- | --- |
| What will we **recognize** (production revenue)? | The month work is earned: `WorkTicketRevenues.RevenueMonth` | Work tickets, visits, earned revenue |
| What will we **book** (sales)? | Won date or estimated close date: `Opportunities.WonDate`, `AnticipatedCloseDate` | Opportunities |
| What will we **invoice**? | `Invoices.InvoiceDate` | Invoices, invoice revenue lines |
| What **cash** arrives? | `Payments.PaymentDate` | Payments |

One forecast uses one date basis. A contract sold in January, worked
April–October, and invoiced monthly is a January booking, April–October
revenue, and twelve invoices. The framework below is the revenue forecast;
section 8 covers the sales (bookings) view that shares its inputs.

Aspire recognizes earned revenue **per work ticket per month**. The work
ticket is therefore the unit of recognition, and the opportunity is the unit
of selling. Every rule below is stated at the grain where Aspire keeps the
fact.

## 2. The layering principle

Future revenue is not one number. It is a stack of layers ordered by how
certain the work is, and each layer has its own timing rule and its own
probability:

| Layer | What it is | Certainty | Timing comes from |
| --- | --- | --- | --- |
| **Earned** | Revenue Aspire has already recognized | Fact | `RevenueMonth` |
| **Pending acceptance** | Labor worked but not yet accepted by a manager | Near-fact | The labor date |
| **Scheduled** | Tickets with a future visit on the calendar | High | `WorkTicketVisits.ScheduledDate` |
| **Backlog** | Sold tickets with remaining value and no future visit | Medium | Ticket plan date, or today |
| **Open pipeline** | Proposals not yet won or lost | Weighted | Estimated win date + lag to first work |
| **Expected renewals** | Prior-year contracts whose term, shifted one year, falls in the horizon, with no renewal proposed yet | Weighted | Prior term shifted one year |

Two rules make the stack sound:

1. **Each layer draws from one pool.** A work ticket's remaining value is
   `Price − earned revenue to date`, floored at zero. Pending acceptance,
   scheduled, and backlog all draw from that pool, so a ticket's revenue lives
   in exactly one of scheduled or backlog and the layers can never sum to
   more than `Price − earned`. (Pending acceptance is mostly an hours layer;
   show it in the hours view and fold its revenue into the ticket's remaining
   value.) Opportunities that are won are already represented by their
   tickets and must not also appear in pipeline.
2. **Precedence runs from certain to uncertain.** When anything has to give
   (a capacity cap, a reconciliation difference), move the lower-certainty
   layer, never the work that has already been done or scheduled.

Showing gross and weighted side by side for the two weighted layers lets a
reader see what the probabilities are doing.

## 3. The remaining-value pool (work tickets)

For every work ticket on a won opportunity whose status is Open or Scheduled:

- **Remaining revenue** = `WorkTickets.Price − WorkTickets.EarnedRevenue`,
  floored at zero. The subtraction is date-agnostic: if Aspire has dated an
  earned amount after today, it has still been earned against this ticket, so
  it is already out of the pool. Do not add a date filter to the netting; it
  double counts.
- **Remaining hours** = `WorkTickets.HoursEst − accepted hours`, floored at
  zero, where accepted hours are the sum of `WorkTicketTimes.Hours` with
  `AcceptedDateTime` set. `WorkTickets.HoursAct` is Aspire's lifetime roll-up;
  check it against the accepted sum before relying on it. Unaccepted labor on
  an Open or Scheduled ticket is the pending-acceptance layer; unaccepted
  labor on a Complete or Canceled ticket is neither.
- Complete and Canceled tickets contribute earned history and nothing forward.

**Future-dated actuals.** Aspire lets a ticket post earned revenue or labor
against a date after today. Show those amounts in the period they are dated,
label them as posted ahead of today, and keep "year to date" literal by
excluding them from it. Never hide or reclassify them; some companies post
ahead deliberately. Starting point: list the affected tickets so a manager
can review them. Through the connector, earned revenue is monthly only, so
revenue posted ahead is visible only when `RevenueMonth` is a future month;
labor dated after today (`WorkTicketTimes.StartTime`) is visible by day.

**Why the ticket, not the opportunity header.** `Opportunities.WonDollars`
and `ActualEarnedRevenue` are job totals. They are a useful sanity check
(ticket prices on a job should roughly sum to the job; change orders, optional
lines, and time-and-materials work explain most gaps), but recognition timing
only exists at the ticket and visit level.

## 4. Scheduled work

A ticket is **scheduled** while it has at least one visit on or after today
with uncovered hours. Visits live in `WorkTicketVisits` with `ScheduledDate`,
`RouteID`, and `Hours`.

- Allocate the ticket's remaining revenue across its future visits in
  proportion to visit hours (starting point) or evenly per visit if hours are
  not maintained. The remaining hours follow the same shape.
- **Net same-day labor.** A visit on day D contributes `visit hours − accepted
  labor dated D on the same ticket`, floored at zero, so a visit that has
  already been worked today does not also appear as scheduled. For today
  only, also net unaccepted (pending) labor dated today, so labor already
  counted as pending is not scheduled a second time.
- Scheduled hours are the schedule. Do not cap them at the remaining estimate;
  the comparison between the two is a signal (over-scheduled ticket), not a
  correction.
- `ScheduledDate` is a calendar-date label. Never shift it by time zone; the
  only time-zone decision in the model is which calendar date is "today".
- Recurring maintenance contracts often show up here rather than in backlog
  when their occurrence tickets and routed visits exist in Aspire; check how
  far ahead your company creates them.

## 5. Backlog

**Backlog** is every Open or Scheduled ticket with remaining revenue or hours
and no uncovered future visit. It is sold work that is not on the calendar.
Classify each ticket by its plan date (`ScheduledStartDate`, falling back to
`AnticStartDate`) compared to **today**, never to the first of the month:

| Bucket | Plan date | Spread from | Note |
| --- | --- | --- | --- |
| Backlog, current | today or later | the plan date | Work that is planned but not routed |
| Backlog, past due | before today, including earlier this month | today | Slipped work that needs rescheduling. It must stay in the forecast: if you spread it from its past date, a short duration ends before today and the revenue disappears. |
| No date | — | today | Or exclude under a stricter "future only" setting |

Decisions to make:

- **Staleness cutoff.** A ticket planned fourteen months ago with remaining
  value is probably a close-out problem, not future revenue. Starting point:
  exclude past-due tickets older than a configurable number of months before
  the current month, and list them separately for cleanup.
- **Duration.** Spread remaining value over business days using the ticket's
  remaining hours divided by a typical daily production hours figure for the
  division (derived from accepted labor history), or over an average ticket
  duration measured from completed tickets. One day is the minimum.

## 6. Open pipeline

Open pipeline is every opportunity that is not Won and not Lost. It is the
only layer where both **whether** and **when** are uncertain, so it needs a
probability and a timing rule.

### 6.1 Population

Start from `Opportunities` with `OpportunityStatus` not in Won or Lost, and
decide:

- **Which open statuses count.** Aspire's usual progression is New, Bidding,
  Approved, Delivered, then Won or Lost. Delivered means the proposal reached
  the customer. A conservative revenue forecast counts Delivered only; a sales
  manager's view may include everything open. Ask the team, and remember
  that a close rate measured on delivered proposals overstates earlier
  statuses (New, Bidding, Approved); discount them or measure the rate by
  status, and say which.
- **Opportunity types.** Contract and Work Order both count; they spread
  differently (section 6.4).
- **Exclusions.** Zero `EstimatedDollars`; never-sent proposals (Aspire stamps
  `ProposedDate` equal to `LostDate` on auto-closed proposals, so these are
  Lost anyway); optional service lines if the team's estimate convention
  excludes them. Proposals with no `ProposedDate` are a decision: exclude
  them as never really proposed, or keep them on the last-resort date in
  section 6.3 and list them.
- **Staleness.** Open proposals created or planned to start long ago are
  often abandoned, not pending. Starting point: a created-date lookback
  (for example 12–18 months) and a past-start-date cutoff, both tunable, with
  the excluded rows listed so sales can clean them up. Do not apply the
  past-start cutoff or the created-date lookback to contracts with a usable
  future end date (section 6.4).

### 6.2 Probability

Four approaches, in increasing sophistication. Most teams start at the
second and move to the third once they trust the data.

1. **Manual.** Use `Opportunities.Probability` when the sales team maintains
   it. Honest when it is kept current; usually optimistic when it is not.
2. **Flat rate.** One close rate for all open work (for example the trailing
   twelve-month dollar close rate). Simple, auditable, and wrong in the same
   direction for everyone.
3. **Empirical by segment.** Measure historical close rates by the dimensions
   the team believes matter: division, sales type (New vs Renewal), opportunity
   type, branch, sales rep. Resolve each open opportunity to the most specific
   segment with enough history; fall back to the parent segment, then the
   global rate, when a segment is thin.
4. **Adjusted model.** Start from the scoped global rate and nudge it for a
   few traits you believe matter (for example division, sales type, deal
   size, and how long the proposal has been open), skipping any trait where
   history is thin or the opportunity lacks it.

Rules that apply to every empirical approach:

- **Measure close rate as a cohort.** Numerator: Won. Denominator: Won + Lost
  (+ Delivered, if still-open delivered proposals should count as not yet
  won). Follow the proposals from a period to their outcome; never divide this
  period's wins by this period's proposals.
- **Dollar-weight when forecasting dollars.** Count-based rates and
  dollar-based rates differ whenever big deals close differently from small
  ones. Use the one that matches the forecast's unit.
- **Only train on what existed at the outcome.** `JobStatusName` is filled
  in after a win, so it carries no information about whether an open proposal
  will close. Use it to filter forward candidates if the team wants, never to
  compute historical rates.
- **Measure age from the same date you forecast from.** Proposal date is the
  usual anchor; creation date is defensible when proposals sit unproposed for
  weeks.
- **Scope history to the forecast's own scope.** If the forecast excludes a
  division, its history should not pool into the global anchor.
- **Won is 100%. Delivered is not Won.** If the business wants delivered
  proposals treated as won, that is an explicit decision, not a default.

### 6.3 Timing: estimated win date

Aspire dates on open opportunities drift. A proposed work start in the past
on a still-open deal means the start slipped, not that the work is underway.
The timing rule has to say what a stale date means.

One defensible ordering, which teams commonly adjust. The principle: a
stale date means the work slipped, not that it is underway, so treat the deal
as if it were proposed yesterday and let the average lags place it. A
"usable" date is a `ProposedDate`, an `AnticipatedCloseDate` the team trusts,
or a `StartDate`. Variations: trust the rep's close date more, or less.

| Opportunity | Estimated win date | Note |
| --- | --- | --- |
| Won | `WonDate`, then the best remaining historical date (anticipated close, proposed + average lag, start) | History. Never roll won work forward, even when the fallback lands in the past. |
| Open, `StartDate` in the past | `yesterday + avg proposed→won days` | The proposed start slipped |
| Open, `AnticipatedCloseDate` in the past and the team uses close dates | `yesterday + avg proposed→won days` | The expected close slipped |
| Open, `AnticipatedCloseDate` in the future and the team uses close dates | `AnticipatedCloseDate` | The rep's estimate wins when fresh |
| Open, `ProposedDate + avg proposed→won` is in the future | that date | The average lag places it |
| Open, `ProposedDate + avg proposed→won` is in the past | `yesterday + avg proposed→won days` | Still active, so still in the horizon |
| Open, no usable dates | `today + default lag` (for example 90 days) | Last resort; count these and show them |

Two averages drive this, both measured from the team's own history over a
configurable window:

- **Proposed→won days**, from Won opportunities with both `ProposedDate` and
  `WonDate`.
- **Won→first-work days**, from `WonDate` to the first accepted labor date
  (or the first earned revenue month when labor is thin).

Whether to use `AnticipatedCloseDate` at all is a team decision: it is
accurate where reps maintain it and noise where they do not.

### 6.4 Timing: when revenue is recognized

Revenue work-start = estimated win date + won→first-work days, then:

- floor at `StartDate` when it is in the future (a future proposed start is a
  real constraint: the customer does not want the work before then);
- floor at today (unwon work cannot be recognized in a closed or current-day
  historical bucket).

Then spread:

- **Contracts with a usable schedule** (`StartDate` and `EndDate` both
  present, end ≥ start, end ≥ today): spread across the contract term and
  ignore the estimated win date entirely; a stale close date must not move a
  contract away from its contract dates. Starting point is an even spread by
  month; a better one follows the service occurrences or the prior year's
  earned curve for the same property and division. For a term that began
  before today, nothing may land before the current period: drop the elapsed
  share (starting point) or re-spread it over the remaining months, and state
  which you chose.
- **Work orders, and contracts without a usable schedule**: spread from the
  work-start date over a duration taken from (in order) the average duration
  of comparable completed tickets, the average work duration for the division,
  or remaining hours divided by typical daily production hours.

Weighted revenue and hours = gross × probability, spread with the same shape.

## 7. Expected renewals

Open pipeline misses the most predictable revenue in a maintenance business:
the contract that ends in October and will almost certainly renew, but whose
renewal proposal has not been created yet. Model it as a separate layer so it
can be tuned (or switched off) on its own.

- **Candidates.** Contract opportunities whose job is active or complete,
  with `StartDate` before today and valid dates, whose term shifted forward
  one year overlaps the forecast horizon.
- **Suppression.** Skip a candidate when another Contract opportunity for the
  same property and division (not Lost or cancelled) overlaps the shifted
  term. The real proposal, in pipeline, represents that renewal now. Match at
  property + division so a snow renewal does not suppress a maintenance ghost.
- **Already late.** If the shifted start is already behind today and no
  future contract exists, the renewal window passed. Starting point: treat it
  as not renewed and list it, rather than forecasting it.
- **Math.** Shift start and end one year; keep the source contract's shape and
  hours; multiply revenue by (1 + expected price increase); multiply revenue
  and hours by the expected renewal rate. The renewal rate should come from
  measured retention for the scope, not an industry number.

## 8. The sales (bookings) view

The same opportunities answer "what will we **sell** by month?" with a
different bucket:

- Won rows bucket by `WonDate` and are never clamped.
- Open rows bucket by estimated win date (section 6.3) and are clamped to the
  current month when that date is in the past. An open deal cannot be booked
  into a closed month.
- Probabilities follow section 6.2. Including Won rows gives a
  bookings-to-date plus weighted-remaining picture against a sales goal.

Keep the revenue forecast and the sales forecast as two outputs over shared
inputs; do not add them.

## 9. Capacity reality check

A forecast can promise more hours than the crews can deliver. Compare
forecast hours per period, branch, and division against capacity (route
hours from `Routes`, confirming whether the figure is per day or per week, or
headcount × hours per week × working days). Starting point: when a period is
over its cap, push the lowest-certainty layer later first, expected renewals,
then open pipeline, then backlog, and never move earned, pending, or
scheduled work. Caps that recur by month of year (an April cap applies to
every April) capture seasonality once.

Hours and staffing views show actual and pending hours for context in closed
periods and only forecast layers from the current period forward.

## 10. Closed periods

A period before the current one shows actuals only: earned revenue, accepted
hours, and pending-acceptance hours dated in it. No scheduled, backlog,
pipeline, or renewal layer may appear in a closed period. If the model puts
one there, the timing rule is wrong.

## 11. Reconciliation checks

Run these before trusting a build:

- For every ticket, scheduled + backlog ≤ `Price − EarnedRevenue`.
- No ticket appears in both scheduled and backlog; no Won opportunity appears
  in open pipeline.
- Year-to-date earned revenue equals Aspire's earned revenue report for the
  same scope and months.
- Scheduled hours for next week equal the route schedule for next week.
- Open pipeline gross plus the listed stale and excluded rows equals the open
  pipeline total on the Sales Scorecard for the same statuses and scope.
- Nothing forecast lands in a closed period.
- Pipeline rows with a last-resort date, past-due backlog, stale exclusions,
  and future-dated actuals are each listed, with counts, next to the chart.

## 12. Decisions the team must make

Every one of these changes the number. Record the choice, the reason, and the
date; the agent should read them back before each build.

| Decision | Starting point | Ask |
| --- | --- | --- |
| Horizon and grain | 12 months, monthly; weekly for the next 8 weeks | "How far out do you plan labor?" |
| Which open statuses are pipeline | Delivered only | "Is a proposal in Bidding real pipeline for you?" (earlier statuses need their own, lower rate) |
| Probability method | Empirical by segment, dollar-weighted | "Do your reps keep the probability field current?" |
| Close-rate denominator | Won + Lost + Delivered by proposed-date cohort | "Should a delivered proposal still waiting count as not-yet-won?" |
| Use `AnticipatedCloseDate` | Off until reps maintain it | "Who updates expected close dates, and how often?" |
| Proposal staleness | 12–18 month created-date lookback | "When is an open proposal really dead?" |
| Backlog staleness | Exclude past-due tickets older than N months | "How old can a slipped ticket be and still be real?" |
| Undated backlog | Roll forward from today | "Do you want undated tickets in or out?" |
| Contract spread shape | Even by month | "Does your maintenance revenue follow a seasonal curve?" |
| Expected renewals | On, measured retention rate, planned price increase | "What renewal rate and price increase are you planning on?" |
| Capacity caps | Off until crews are modeled | "What is a crew-week worth in hours by division?" |
| Delivered treated as Won | No | Only if the business explicitly says so |

## 13. Worked example (fictional)

Fieldstone Grounds, Maintenance division, forecasting June. Today is May 20.

| Item | Facts | Layer | June amount |
| --- | --- | --- | --- |
| Ticket 4411, Oak Plaza mowing | Price $6,000; earned $3,000; 6 equal-length visits left, 2 in June | Scheduled | $1,000 (2 of 6 remaining visits) |
| Ticket 4520, Elm Court mulch refresh | Price $8,500; earned $0; planned start May 6, no visits | Backlog, past due | $8,500 spread from today over 5 business days, so all lands in May; **$0** in June |
| Ticket 4590, Birch Lane cleanup | Price $2,400; earned $2,400 | — | $0 (fully earned) |
| Opp 7021, Cedar Park seasonal color changeouts | Work Order, Delivered, $12,000, proposed Apr 28, no proposed start date; segment close rate 45%; proposed→won 30 days; won→first work 14 days; duration 10 business days | Pipeline | Win ≈ May 28, start ≈ Jun 11; weighted $5,400 all in June |
| Opp 7044, Maple Ridge maintenance | Contract, Delivered, $36,000, Jul 1–Dec 31; segment rate 60% | Pipeline | Usable contract schedule: spread Jul–Dec ($3,600/month weighted); **$0** in June |
| Opp 6210, Willow Office Park irrigation-and-turf contract | Contract, Complete, Jun 1–Nov 30 last year, $45,000; no renewal proposal; retention 85%, price increase 4% | Expected renewal | Shifted Jun 1–Nov 30 (start is after today, so it qualifies); June share $45,000 × 1.04 ÷ 6 × 0.85 = $6,630 |
| Opp 6188, Pine Hollow maintenance contract | Contract, Complete, Mar 1–Nov 30 last year, $30,000; no renewal proposal | Already late | Shifted start (Mar 1) is behind today: listed as not renewed, **$0** forecast |

June, Maintenance: scheduled $1,000 + backlog $0 + weighted pipeline $5,400
+ expected renewals $6,630 = **$13,030** forecast, with $0 earned (June has
not started). The report also lists Ticket 4520 as past-due backlog for
rescheduling, Opp 6188 as a renewal whose window passed, and shows pipeline
gross of $12,000 next to the weighted $5,400.

Change one decision (count Bidding proposals as pipeline, or turn expected
renewals off) and the June number moves; that is the point of recording the
decisions.

## Appendix: Aspire fields the model uses

Discover live fields with `capsa_describe_aspire_resources` (resource +
`fields: "dates"` or `"measures"`) and the `date_basis_map`,
`forecast_layers`, `earned_revenue`, `scheduled_visits`, `labor_acceptance`,
`close_rate_cohort`, `opp_status_canonical`, and `job_status` concepts. For
teams exporting from Aspire reports instead, the same fields by name:

| Resource | Fields | Used for |
| --- | --- | --- |
| `Opportunities` | `OpportunityStatus`, `OpportunityType`, `SalesTypeName`, `EstimatedDollars`, `WonDollars`, `Probability`, `CreatedDateTime`, `ProposedDate`, `WonDate`, `LostDate`, `AnticipatedCloseDate`, `StartDate`, `EndDate`, `JobStatusName`, `BranchID`, `DivisionName`, `SalesRepContactID`, `PropertyID` | Pipeline population, probability, timing, renewals, sales view |
| `WorkTickets` | `WorkTicketStatusName`, `Price`, `EarnedRevenue`, `HoursEst`, `HoursAct`, `ScheduledStartDate`, `AnticStartDate`, `CompleteDate`, `OpportunityID`, `BranchID` | Remaining-value pool, backlog classification |
| `WorkTicketVisits` | `ScheduledDate`, `Hours`, `RouteID`, `WorkTicketID` | Scheduled layer |
| `WorkTicketRevenues` | `RevenueMonth`, `RevenueAmount`, `WorkTicketID` | Earned layer, closed periods, reconciliation |
| `WorkTicketTimes` | `StartTime` (or `WorkTicketTimeDate`), `Hours`, `AcceptedDateTime`, `WorkTicketID` | Actual vs pending hours, same-day netting, won→first-work lag |
| `Routes` | `Hours`, `BranchID`, `DivisionID`, `Active` | Capacity caps |

Division for a ticket or visit comes through its opportunity service line
(the operations division); pipeline and renewals use the opportunity header's
sales division. Per-division totals can therefore differ between layers; say
so when they disagree. Branch is on the ticket. Work removed in Aspire is not returned by the
connector, so the model never has to handle deleted records itself.
