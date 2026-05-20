# Capsa Agent Cookbook

A growing collection of recipes that show how agents can use the **Capsa MCP
connector** alongside other connected apps — Gmail, Outlook, calendars, docs —
to complete real work.

## What this cookbook is

The Capsa MCP connector is a capability API. This cookbook is the layer on top:
practical, procedural recipes that teach an agent how to combine Capsa's
context with the apps your team already uses.

Every recipe is built around three principles:

1. **Capsa supplies the context.** The connector tells the agent what
   follow-ups are outstanding, who the customer contact candidates are, and
   what evidence would close the loop.
2. **The user approves before anything leaves.** Agents draft; the user
   reviews; the connected email provider (or other tool) sends only after
   explicit approval.
3. **Completion is recorded only after it actually happened.** A draft is not
   a send. An agent never marks a follow-up done without send evidence or an
   explicit user confirmation.

## First recipe

→ [Proposal follow-up email batch](recipes/followup-email-batch.md)

Walks an agent through finding outstanding proposal follow-ups via Capsa,
drafting editable emails per contact, getting user review, sending through
the connected email provider, and only then marking the follow-up complete.

## Required connectors

Recipes will name the connectors they expect. The follow-up email recipe
needs:

- **Capsa MCP connector** — provides follow-up context and completion
  recording.
- **Gmail or Outlook connector** — for sending the approved drafts.

If a connector isn't connected, the agent should ask the user to connect it
rather than working around it.

## Public MCP tools used in recipes

- `capsa_describe_service` — orient the agent to what the connector exposes.
- `capsa_find_followup_actions` — list outstanding follow-ups with the
  context needed to act.
- `capsa_mark_followups_done` — record completion after evidence.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Recipes should be procedural, use
fictional examples, and keep the user firmly in the approval loop.
