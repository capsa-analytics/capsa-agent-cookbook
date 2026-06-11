# Capsa Agent Cookbook

A growing collection of recipes and installable skills that show how agents can
use the **Capsa MCP connector** alongside other connected apps — email,
calendars, docs — to complete real work.

## What this cookbook is

The Capsa MCP connector is a capability API. This cookbook is the layer on top:
practical, procedural recipes — packaged as installable skills — that teach an
agent how to combine Capsa's context with the apps your team already uses.

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

## Start here

Just connected Capsa? Read **[start-here.md](start-here.md)** — what you can do
(with example prompts to try), the four-beat loop every task follows (orient →
resolve → act → record), and the safety contract the recipes assume.

To put that guidance *into* your agent, install the
**[capsa-orientation skill](skills/capsa-orientation/)** — or copy its body into a
system prompt, or let an agent fetch it via `capsa_discover_playbooks`. It's
discovery-first, so it keeps working as Capsa ships new capabilities.

## Install the skill pack

The skills ship as a Claude Code plugin (this repo is its own marketplace):

```
/plugin marketplace add capsa-analytics/capsa-agent-cookbook
/plugin install capsa-cookbook@capsa
```

Or copy any skill's `SKILL.md` body into another agent — the steps are
framework-agnostic. Re-pull after a connector upgrade so the discovery-first
guidance stays current.

## Machine-readable index

Agents that reach this cookbook via `capsa_discover_playbooks` can fetch a map
instead of scraping this page:

- [`llms.txt`](llms.txt) — a curated, link-first overview
  ([llmstxt.org](https://llmstxt.org) convention).
- [`index.json`](index.json) — the same map as structured data: capabilities,
  skills, patterns, tools, and install commands, with stable paths.

## Skills — the flagship pack

Installable, self-contained skills. Each is discovery-first and keeps the user in
the approval loop:

- **[capsa-orientation](skills/capsa-orientation/)** — read first. Discover what's
  enabled, resolve names to dimensions, stay in the approval loop, and record
  completion only on evidence.
- **[proposal-followup-batch](skills/proposal-followup-batch/)** — clear a batch of
  outstanding proposal follow-ups: draft per contact from Capsa context, review,
  send through a connected email provider, and mark done only after send evidence.
- **[sensitive-visit-notice](skills/sensitive-visit-notice/)** — surface upcoming
  visits flagged sensitive (e.g. chemical application) by division and service
  type, draft customer pre-notices for review, send only after per-visit approval.
- **[renewal-portfolio-triage](skills/renewal-portfolio-triage/)** — pull the full
  renewal book for a scope, tier it with explainable rules (dollars at risk, time
  pressure, margin flags, payment and satisfaction risk), and present a ranked
  worklist the user prunes before any deep dive.
- **[renewal-deep-dive](skills/renewal-deep-dive/)** — build a renewal
  recommendation for one property from renewal drilldowns and property context:
  price/hours/terms options with cited evidence. The agent proposes; the user
  decides.

## Reference

The comprehensive map of what the connector exposes — capability-led, and kept in
sync with the connector's live `capsa_describe_capability`.

**Capabilities**

- [Follow-up actions](reference/capabilities/followup-actions.md) — outstanding
  proposal follow-ups with contact context; evidence-gated completion.
- [Upcoming visits](reference/capabilities/upcoming-visits.md) — scheduled visits
  with property and customer-contact context for notice workflows.
- [Property context](reference/capabilities/property-context.md) — search
  properties and pull production, satisfaction, sales, and visit signals; filter a
  property book by dimension, metric, or date range.
- [Renewal opportunities](reference/capabilities/renewal-opportunities.md) — the
  renewal book for a window: prior contract baseline, pipeline by status,
  retention, change tags, plus per-property service comparisons and prior-year
  performance review.

**Patterns** — always-on disciplines a skill applies:

- [Resolving ambiguous names](reference/patterns/resolve-ambiguous-names.md) —
  work out which dimension a user's term belongs to (is "Tori Nash" a sales rep,
  an account owner, or a property?) before filtering or reporting.

## Required connectors

Skills name the connectors they expect. The workflow skills need:

- **Capsa MCP connector** — provides follow-up, upcoming-visit, and property
  context, and (for follow-ups) completion recording.
- **An email provider connector** — for sending the approved drafts. Gmail
  and Outlook are common examples; any email connector your agent has
  access to works.

If a connector isn't connected, the agent should ask the user to connect it
rather than working around it.

## Public MCP tools used in recipes

Orientation:

- `capsa_describe_service`, `capsa_list_capabilities`,
  `capsa_describe_capability`, `capsa_describe_tool` — discover what the
  connector exposes before acting.
- `capsa_discover_playbooks` — point the agent at this public cookbook for
  workflow playbooks and the installable skill pack.

Follow-up actions:

- `capsa_find_followup_actions` — list outstanding follow-ups with the
  context needed to act.
- `capsa_mark_followups_done` — record completion after evidence.

Upcoming visits:

- `capsa_list_upcoming_visit_filter_options` — list branches, divisions,
  account owners, service types, and services available to the connection.
- `capsa_find_upcoming_visits` — list upcoming visits with property,
  service, and customer contact context.

Property context & name resolution:

- `capsa_list_followup_filter_options`,
  `capsa_list_property_context_filter_options` — list the dimension values
  (Branch, Sales Rep / Account Owner, Division, property type, tag, industry,
  status) available to the connection. With the upcoming-visit options above,
  these lists double as the dictionary for resolving an ambiguous name to a
  dimension.
- `capsa_search_properties` — fuzzy-match a property, customer, contact,
  owner, tag, or ID and return contact-ready candidates.
- `capsa_get_property_context`, `capsa_get_property_context_drilldown` —
  pull compact context for a property, a filtered property book, or
  one-property detail.

Renewal opportunities:

- `capsa_list_renewal_filter_options` — list the Status, Sales Type, Division,
  Branch, Account Owner, and Property Tag values available to the connection,
  plus the change-tag and performance-flag vocabularies.
- `capsa_find_renewals` — the renewal book, paged with a true book-level
  summary on every page: prior contract baseline, pipeline by status, days to
  start, retention, change tags, and contacts.
- `capsa_get_renewal_drilldown` — one property's service-level price/hours
  comparisons, prior-year performance review, or underlying renewal
  opportunity lists.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Recipes should be procedural, use
fictional examples, and keep the user firmly in the approval loop.
