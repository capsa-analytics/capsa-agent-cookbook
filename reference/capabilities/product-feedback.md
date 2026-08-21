# Product feedback (`product_feedback`)

Capture an unmet user request for Capsa product review when the current
connector surface cannot fully answer or perform it — a metric question, a
data shape, a workflow, a filter, or a write action.

> This page mirrors `capsa_describe_capability` for `product_feedback`. The
> connector's live output is the source of truth. For exact tool
> inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user asks for an analytics shape the connector cannot directly answer
  today.
- The user asks for a data lookup, workflow, or write action outside current
  Capsa tools.
- A tool call fails because the needed metric, dimension, filter, freshness,
  or action boundary does not exist yet — see the loop step below.
- The user has agreed to record the gap, and you want to capture a concise
  description plus your attempted route for product triage before falling
  back to a generic answer.

## Tools

- `capsa_log_feature_request` — capture the unmet request. Only
  `user_request` is required; everything else (`interpreted_task_type`,
  `attempted_route`, `attempted_tool`, `missing_capability`,
  `requested_metrics`, `requested_dimensions`, `requested_filters`,
  `urgency`, `workflow_category`, `fallback_response`, `related_tool_calls`,
  `agent_context`, `notes`) is optional context that makes the request more
  actionable for product triage. Include as much of it as you have.

## Loop step 5: offer to log, don't give up

Step 5 of the [capsa-orientation](../../skills/capsa-orientation/) loop
exists for exactly this capability: if a request can't be satisfied, OFFER to
record the gap with `capsa_log_feature_request`, and log only after the user
agrees. Recording persists content outside the conversation for Capsa's
product review, so it follows the same rule as any other write: explicit
approval first. When the user agrees, show them what you'll record — a
concise description of the gap in your own words, not their raw message,
with names, dollar figures, and anything else sensitive left out unless they
ask to include it. Offering (then logging with consent) is what you do
instead of:

- silently dropping the ask and answering something adjacent instead;
- improvising a workaround the user didn't ask for;
- guessing at a value, ID, or metric the connector didn't return.

The connector also nudges you toward this tool directly — every
permission-denied error, unknown-capability/tool error, and
unsupported-filter error on the Capsa surface ends with a one-line reminder
to log a feature request if the user still needs it. The nudge tells you the
tool exists; the consent step above still applies before you call it.

## What to include

The more context you give, the more useful the logged request is for product
triage:

- **`attempted_route` / `attempted_tool`** — what you tried first (e.g. an
  Ops Scorecard shape, or `capsa_describe_analytics_catalog`).
- **`fallback_response`** — the safe answer you actually gave the user
  instead. Never include secrets, private email content, or unnecessary
  personal details here or anywhere in the request.
- **`missing_capability`** — your best guess at the gap category (metric,
  dimension, filter/default, source-record lookup, action/writeback,
  role/workflow, freshness, or data quality).
- **`urgency`** — how important this seemed in the user's workflow.
- **`agent_context`** — a short summary of the conversation and the user's
  goal, so a human reviewer doesn't have to reconstruct it.

If a cataloged metric or scorecard shape exists but isn't queryable yet, call
`capsa_describe_analytics_catalog` first so the logged request includes the
closest matching metric and default context.

## Boundaries

- This records product feedback only; it does not create customer-facing
  tasks, tickets, or change customer data.
- Read-only from the agent's perspective — there is no completion or status
  write for a logged request.
- Capsa reviews logged requests asynchronously (see below); logging one does
  not mean the gap is closed in this session.

## Freshness

Feature request capture is immediate, but review is asynchronous — a human
reads a weekly digest, not a live queue.

## Related

- Skill: [capsa-orientation](../../skills/capsa-orientation/) — loop step 5
  is where this capability gets used.
