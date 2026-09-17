---
description: Two-stage review of the active (WIP) job book — scan and rank jobs with capsa_query_job_book (health status or margin erosion, with server-side metric thresholds), shortlist the ones worth a closer look, then pull a compact card and targeted drilldowns per job with capsa_get_job_context / capsa_get_job_context_drilldown and draft a review memo. Use when a manager wants to work a branch or division's WIP job book, not look up one job they already have.
---

# Job book review

Scan the active job book for jobs worth a closer look, then go deep on each
one the way a production manager would: tickets, crew, billing, change
orders, and health history — cited to Capsa's own job-to-date numbers.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Work-in-progress jobs drift — margin erodes, hours run over, issues pile up —
and by the time it shows up in a monthly report the job is already closed
out. This skill turns the active job book into a short shortlist, then
assembles the evidence behind each flagged job in one pass instead of a
manager opening each job one at a time.

The steps are the same whether this runs as an installed skill, is pasted
into another agent, or is run ad-hoc. The "Configuration" section is the
contract; persist those inputs in the Team specifics block below, a system
message, or a wrapper script.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the job-context capability is
  available on this connection.
- The user wants to work through a **set** of active jobs — a branch or
  division's book — not look up one job number they already have.
- The team's shortlist thresholds below are set, or the user is ready to set
  them.

Skip it when the user already has one job identified. If they have a `job_id`
that `capsa_query_job_book` returned earlier in the conversation, go straight
to step 5 below (`capsa_get_job_context`). If all they have is a job number or
a name ("job 55123", "the Maple Ridge irrigation retrofit"), the connector has
no lookup by number or name yet: call `capsa_query_job_book` **without any
`metric_filters`** (narrow only by branch or division if known, and page
through every result), match the row whose `job_number` or property/job name
fits, and use that row's `job_id`. The shortlist threshold from Configuration
is for the review pass, not for finding a job — a perfectly healthy job would
never clear it. If no row matches after the full scan, tell the user the job
wasn't found in the active job book available to this connection — it may be
completed (this capability covers in-production jobs only), out of scope, or
misidentified — rather than concluding which.

## Required connected apps

- **Capsa MCP connector.** Provides the job book, the single-job card, and
  every drilldown this recipe reads. This capability is read-only, so no
  other connector is required. If the user wants the finished memos in a doc
  or message, that destination's connector is also needed and the post is
  approval-gated like any outbound content.

## Configuration

All defaults below are placeholders — the team's numbers are the source of
truth. Never substitute an industry benchmark for an unset value; ask.

- **Scope defaults.** Call `capsa_list_job_filter_options` to see the
  branches, divisions, and Operations Managers available. Record which
  branch/division IDs constitute "the job book" for recurring reviews.
- **Shortlist rule.** The metric threshold that flags a job for the deep-dive
  pass — e.g. `gross_margin_percent` under 20, or `margin_erosion_pct_points`
  over 5. `capsa_list_job_filter_options` also returns the full
  `metric_filter_metrics` / `metric_filter_operators` vocabulary if the team
  wants a different one.
- **Shortlist cap.** How many jobs get the full card-and-drilldown treatment
  in one pass (a common default is 10–15).
- **Default drilldowns.** Which `drilldown_id` values to pull automatically
  per shortlisted job versus only on request. A reasonable default:
  `ticket_breakdown` and `open_issues` always; `crew_breakdown` when the
  ticket breakdown shows a burn problem; `billing_breakdown` when the card's
  billing summary shows outstanding or late balances; `change_orders` when
  the card's `change_order_count` is above zero; `health_history` on request.

## Workflow

### 1. Learn the capability (only if needed)

If you haven't used the job-context capability recently, call
`capsa_describe_capability` for `job_context` once to confirm shape and
filters.

### 2. Resolve the scope

Call `capsa_list_job_filter_options` and resolve the configured branch /
division / Operations Manager names to IDs (see the
[Resolving ambiguous names](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/reference/patterns/resolve-ambiguous-names.md)
pattern). Confirm the shortlist metric and threshold with the user in one
line before pulling.

### 3. Scan the active job book

Call `capsa_query_job_book` with the resolved filters and `metric_filters`,
sorted by `health_status` (the default — most urgent first) or
`margin_erosion_pct_points` descending, whichever the shortlist rule calls
for.

- The response's `book` totals (`job_count_in_scope`,
  `total_current_estimated_revenue`) are computed over the full filtered
  scope on the first page, so the scoreboard is true immediately even before
  every page has loaded.
- While `page.has_more` is true, keep pulling (up to 500 rows per call) using
  `page.next_cursor` until the scope is covered, or until the user has enough
  to work with. Never present a partially paged book as full coverage.
- Every money and progress figure (`revenue_to_date`, `cost_to_date`,
  `current_estimated_revenue`, `current_estimated_cost`, `percent_complete`)
  is cumulative since **that job's own start** — job-to-date, not a rolling
  window like property context uses. Gross margin excludes overtime premium.
  Carry both facts into anything you report.

### 4. Present the shortlist

One line per job: job name, property, branch/division, health status, gross
margin % vs. estimated margin %, margin erosion, open issues, change order
count. The user prunes, reorders, or adds jobs — the scan is a proposal, not
a verdict; accept overrides without arguing.

### 5. Go deep, one job at a time

For each job the user picks, call `capsa_get_job_context` with its `job_id`
**exactly as `capsa_query_job_book` returned it**. A job number is not a
`job_id` — if a number or name is all you have, find the row in the book first
(step 3). This returns the compact
card (health, billing summary, change orders, ticket status counts, open
issue count, links) plus `available_drilldowns`.

Then call `capsa_get_job_context_drilldown` per the Configuration defaults or
whatever the card itself flags — one `drilldown_id` per call:

- `ticket_breakdown` — every ticket on the job, sorted by burn percent, when
  margin or hours look off.
- `crew_breakdown` — alongside `ticket_breakdown`, to see which crew leader
  is driving a burn problem. This is leader-level attribution only; Capsa
  does not track hours below the crew leader.
- `billing_breakdown` — when the card's `billing_summary` shows outstanding
  or late AR.
- `open_issues` / `recent_completed_issues` — when `open_issues_count` is
  above zero or the user wants recent history.
- `change_orders` — when `change_order_count` is above zero. This drilldown
  includes the job's own original Work Order alongside its change orders;
  the compact card's own `change_orders` block does not — don't mix the two
  counts in one sentence.
- `health_history` — the review-action log behind the current status, on
  request.

### 6. Draft a review memo per job

Fixed shape: **Status** (health status and why the job was shortlisted) →
**What's driving it** (ticket/crew/change-order evidence, each cited to the
drilldown it came from) → **Billing** (only when AR is outstanding or late)
→ **Open items** (issue count plus anything notable) → **Suggested next
step** (a question or option for the user, never a directive). Close every
memo with the job-to-date and 24-hour freshness disclosures.

### 7. Review with the user, and stop

The user can ask for another drilldown, adjust the shortlist, or move on.
This capability has no completion-write tool — the run ends at the memos. If
the user wants them in a doc or message, draft it and post only after
explicit approval.

## Stop rules

- **Job-to-date, not rolling.** Every money/progress figure is cumulative
  since the job's own start. State this in every memo; never imply a
  trailing window the way property context uses.
- **Health is the human-reviewed status only.** `health.status`/`summary` is
  the raw status a person set and reviewed (`last_reviewed_at`,
  `review_is_fresh`). Jobs have no live, system-computed "effective health"
  suggestion the way properties do — never present it as a real-time score.
- **WIP-only, and only by the book's own job_id.** `capsa_get_job_context` /
  `capsa_get_job_context_drilldown` accept only a `job_id` exactly as
  `capsa_query_job_book` returned it. A change order's own id, a completed
  job, a nonexistent id, and a job outside the connection's allowed scope all
  return the identical "not available" message — if that happens, say the
  job isn't available through this tool; don't guess which case it was.
- **Never invent a threshold, a figure, or a reason.** A shortlist rule, an
  amount, or an explanation that isn't in the Capsa response or the user's
  own words doesn't go in the memo.
- **Crew detail is leader-level.** `crew_breakdown` attributes hours and cost
  to the crew leader assigned on each ticket. Never imply finer-grained
  detail exists.
- **Freshness.** Every read may be up to 24 hours old — surface that for
  anything schedule- or billing-imminent.
- **Nothing leaves chat without approval** if the memos go anywhere outside
  this conversation.

## Example user prompt

> "Walk the Kansas City WIP job book with me — I want to see anything where
> margin's slipping before we close out the month."

## Example agent output (fictional)

```
Active job book — Kansas City branch (Capsa data may be up to 24 hours old;
every figure below is job-to-date, not a rolling window):

Scoreboard: 42 active jobs · $2.1M current estimated revenue in scope

Shortlisted (gross margin % under 20, worst first):
1. Greenleaf Corporate Campus — WO-2041 · health: yellow · margin 14.2% vs
   28% estimated (13.8 pts eroded) · 2 change orders · 3 open issues
2. Riverbend Office Park — WO-2118 · health: red · margin 9.8% vs 25%
   estimated (15.2 pts eroded) · 0 change orders · 1 open issue

Want the full card and drilldowns on both, or Riverbend first?
```

After the user picks Riverbend:

```
JOB REVIEW — Riverbend Office Park (WO-2118), Kansas City / Enhancement
(Capsa data may be up to 24 hours old; figures are job-to-date since this
job's own start)

STATUS
Health: red — "Labor overruns on irrigation install; crew turnover
mid-project" (reviewed 3 days ago, still fresh). Shortlisted for margin:
9.8% actual vs 25% estimated — 15.2 points eroded.

WHAT'S DRIVING IT
- Ticket breakdown: the irrigation-install ticket is at 134% of estimated
  hours; mowing and edging tickets are on plan.
- Crew breakdown: two crew leaders share the irrigation ticket — Leader A's
  share is running 40% over their allocated hours, Leader B is on plan.

BILLING
No outstanding or late balance on this job.

OPEN ITEMS
1 open issue: "Client asking about install timeline" (open 6 days).

SUGGESTED NEXT STEP
Worth a conversation with Leader A about the irrigation ticket before the
next billing cycle — want me to check the change-order history too, in case
there's unbilled scope here?
```

All names, dollar figures, and dates above are fictional.

## Team specifics

<!--
  Persist your branch/division scope IDs, shortlist metric and threshold,
  shortlist cap, and default drilldown set here. Keep the steps and stop
  rules in sync with the cookbook; re-pull after a connector upgrade.
-->
