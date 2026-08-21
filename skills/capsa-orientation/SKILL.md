---
description: Read first when any request touches the Capsa MCP connector (proposal follow-ups, upcoming visits, property context, renewals). Teaches the agent to discover what's enabled, resolve names to dimensions, keep the user in the approval loop, and record completion only on evidence.
---

# Capsa orientation

You have access to the **Capsa MCP connector**: operational business context
(proposal follow-ups, upcoming visits, property context, renewals) organized along named
dimensions, plus approved writes where enabled — recording follow-up completion, and
saving a confirmed Command Center property note from meeting-note context. Capsa does not
send email or take external actions — those happen through other connectors, after the
user approves. Follow this loop for any request that touches Capsa data.

## 1. Orient — discover, don't assume

At the start of a session, call `capsa_describe_service` and
`capsa_list_capabilities`; call `capsa_describe_capability` for the one you need.
Availability is resolved from the connection, so a capability may be off — check
rather than guess.

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
- For end-to-end workflows and the full list of things to try, consult the public
  cookbook — call `capsa_discover_playbooks`, or see
  https://github.com/capsa-analytics/capsa-agent-cookbook

## A few things users ask for

- "What proposal follow-ups are due this week?"
- "Find this week's chemical-application visits and draft a heads-up to each contact."
- "Pull the context on a property before I call them."
- "Look up <a name>" — resolve whether it's a rep, an owner, or a property first.

## Team specifics

<!--
  Keep saved filter IDs, a term -> dimension synonym map, and standard templates
  here. Keep the loop and safety rules above in sync with the cookbook; re-pull
  when you upgrade the connector.
-->
