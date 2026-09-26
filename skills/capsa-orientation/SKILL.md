---
description: Read once when first using Capsa or when approval and completion rules are unclear. For routine requests, use the relevant tool or one cookbook recipe without reloading orientation.
---

# Capsa orientation

You have access to the **Capsa MCP connector**: operational business context —
proposal follow-ups, upcoming visits, property context (one property, a ranked
property book, or the daily attention queue), active-job context (the WIP job book
and per-job cards), renewals, Ops/Sales Scorecard questions, and property
penetration/profitability analytics — organized along named dimensions, plus
approved writes where enabled: recording follow-up completion, saving a confirmed
Command Center property note from meeting-note context, adding or editing a
property's Command Center budget item, creating or editing a *draft* price
increase recommendation, starting a Command Center improvement plan, and
reviewed teammate-permission changes for authorized super admins. The
planning writes (budget items, price recommendations, improvement plans) go
through a prepare step that shows the exact values before a
separate save the user has approved; follow-up completion is recorded only on
send evidence or the user's confirmation, and a Command Center note is saved only
after the user confirms the exact property and text. Capsa does not send
email or take external actions — those happen through other connectors, after the
user approves. Use this guidance when first learning Capsa, then reuse it for
the current task. The [cookbook index](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/INDEX.md)
routes specific workflows to one recipe.

Reflects the connector contract as of 2026-09-26 — re-pull this skill after a connector
upgrade.

## 1. Orient — discover, don't assume

When you need a broad overview, call `capsa_list_capabilities`. For an unfamiliar
capability, call `capsa_describe_capability` for that one capability; for unclear
inputs, call `capsa_describe_tool` for that tool. Call `capsa_describe_service`
only when you need connector-wide boundaries or freshness. Availability is
resolved from the connection; do not assume a capability is enabled.

## 2. Resolve names to dimensions

Capsa data is organized along dimensions: Branch, Account Owner / Sales Rep,
Division, Service Type, Service, property type, tag, industry, status, and
properties. A bare name doesn't say which one it is — "Tori Nash" could be a sales
rep, an account owner, or a property/contact, and the people dimension is called
"Sales Rep" for follow-ups but "Account Owner" elsewhere. Before filtering or
reporting, resolve the term against the relevant `capsa_list_*_filter_options` and
`capsa_search_properties`:

- exactly one match → proceed, and state the assumption in one line;
- more than one → ask which;
- no match → don't invent one.

## 3. Act with approval

Anything that leaves your context — email, messages, docs — is drafted for the user
and sent through another connector only after explicit approval. Writes back into
Capsa follow the same rule: before saving a Command Center property note, resolve
the property from the contact and have the user confirm the exact property and the
note text — never write by contact alone.
For teammate permissions, show the exact before/after access and any access
lost, then apply only the proposal the super admin explicitly approves.

## 4. Record only on evidence

Mark a follow-up done only after send evidence or explicit user confirmation, never
from a draft or an intent. If a capability has no completion write, don't fabricate
one.

## 5. Offer to log what's missing

If a request can't be satisfied, don't silently drop the ask, improvise a
workaround, or guess at data the connector didn't return. Instead, OFFER to
record the gap for the Capsa team with `capsa_log_feature_request` — and log
only after the user says yes. Recording persists content outside this
conversation for Capsa's product review, so it follows the same rule as every
other write: explicit approval first.

When the user agrees, show them what you'll record before calling the tool: a
concise description of the gap in your own words — not their raw message —
with names, dollar figures, and anything else sensitive left out unless the
user asks to include it. Add the capability or tool you tried first and the
fallback you gave, when you have them. If the user declines, respect that and
move on.

## Always

- Never invent a dimension value, ID, or fact the tools didn't return.
- Capsa data can be up to 24 hours old; flag that for time-sensitive decisions.
- For end-to-end workflows, use the [cookbook index](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/INDEX.md)
  to select one recipe. Do not read every recipe or reload this orientation
  before each Capsa call.

## A few things users ask for

- "What proposal follow-ups are due this week?"
- "Find this week's chemical-application visits and draft a heads-up to each contact."
- "Pull the context on a property before I call them."
- "What needs my attention today?" / "Which jobs in my branch are losing margin?"
- "How did close rate trend by branch last quarter?" — a Scorecard question.
- "Add this to next year's budget for the property" / "Draft a price increase
  recommendation" — prepare, show the exact values, save only on approval.
- "Explain this teammate's access and suggest the narrowest role" — super
  admin only; show any proposed change before applying it.
- "Look up <a name>" — resolve whether it's a rep, an owner, or a property first.

## Team specifics

<!--
  Keep saved filter IDs, a term -> dimension synonym map, and standard templates
  here. Keep the loop and safety rules above in sync with the cookbook; re-pull
  when you upgrade the connector.
-->
