# Capsa Agent Cookbook

A growing collection of recipes that show how agents can use the **Capsa MCP
connector** alongside other connected apps — email, calendars, docs — to
complete real work.

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

## Recipes

- [Proposal follow-up email batch](recipes/followup-email-batch.md) — Pull
  outstanding follow-ups from Capsa, draft editable emails per contact,
  send through the connected email provider, and mark complete only after
  send evidence.

- [Sensitive scheduled-visit notice](recipes/sensitive-visit-notice.md) —
  Surface upcoming visits a team flags as sensitive (e.g. chemical
  application) by filtering Capsa upcoming visits on division and service
  type, draft customer pre-notices for user review, and send through the
  connected email provider. Framework-agnostic: persist the filters as a
  skill, embed them in another agent, or run ad-hoc.

## Required connectors

Recipes name the connectors they expect. Both current recipes need:

- **Capsa MCP connector** — provides follow-up and upcoming-visit context,
  and (for follow-ups) completion recording.
- **An email provider connector** — for sending the approved drafts. Gmail
  and Outlook are common examples; any email connector your agent has
  access to works.

If a connector isn't connected, the agent should ask the user to connect it
rather than working around it.

## Public MCP tools used in recipes

Orientation:

- `capsa_describe_service`, `capsa_list_capabilities`,
  `capsa_describe_capability` — discover what the connector exposes before
  acting.

Follow-up actions:

- `capsa_find_followup_actions` — list outstanding follow-ups with the
  context needed to act.
- `capsa_mark_followups_done` — record completion after evidence.

Upcoming visits:

- `capsa_list_upcoming_visit_filter_options` — list branches, divisions,
  account owners, service types, and services available to the connection.
- `capsa_find_upcoming_visits` — list upcoming visits with property,
  service, and customer contact context.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Recipes should be procedural, use
fictional examples, and keep the user firmly in the approval loop.
