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
(with example prompts to try), the five-beat loop every task follows (orient →
resolve → act → record → log), and the safety contract the recipes assume.

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
- **[meeting-notes-to-command-center](skills/meeting-notes-to-command-center/)** —
  turn AI meeting notes (Granola, Fathom, Otter, or pasted text) into a reviewed
  Command Center property note: resolve the property via the primary contact, have
  the user confirm the exact property and note text, then write it — never to the
  wrong property.
- **[property-site-update](skills/property-site-update/)** — pull a property's
  relationship, health, satisfaction, and outstanding-item context, then draft an
  internal brief and a customer-safe update for the property manager: what
  happened, what's upcoming, and what's needed from them. The agent never sends.
- **[property-plan-builder](skills/property-plan-builder/)** — build or evolve a
  property's forward-looking plan with the user from health, satisfaction,
  planning, and pipeline context plus any existing future-plans notes, then save
  the approved text as a Command Center property note flagged for future plans.
  Internal by default; the agent never sends it to the customer.
- **[job-book-review](skills/job-book-review/)** — scan and rank a branch or
  division's active (WIP) job book by health or margin erosion, shortlist the
  jobs worth a closer look, then pull a compact card and targeted drilldowns
  per job and draft a review memo.
- **[property-book-triage](skills/property-book-triage/)** — start with the
  fixed "what needs my attention today" queue, broaden with a configurable
  metric sweep over the property book, then hand the shortlist to a
  follow-up, note, or renewal recipe.
- **[budget-item-change](skills/budget-item-change/)** — propose a create or
  edit to a property's budget item, review near-duplicate warnings, and save
  only after the user approves that exact proposal. A saved budget item is
  live in Command Center planning immediately, not a draft.
- **[price-recommendation-change](skills/price-recommendation-change/)** —
  propose a create or edit to a property's price increase recommendation and
  save only after explicit approval. Every save stays a draft for a person
  to review in Command Center.
- **[improvement-plan-start](skills/improvement-plan-start/)** — start a Command
  Center improvement plan for one property: agree the goal and target,
  prepare the exact proposal, save only on explicit approval, report the
  baseline Capsa measured.
- **[scorecard-review](skills/scorecard-review/)** — confirm the metric,
  dimension, and date basis with the analytics catalog, run an Ops or Sales
  Scorecard query, drill into a specific cell, and bring in property-level
  penetration/profitability context — always disclosing which definitions
  produced the answer.

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
  property book by dimension, metric, or date range; rank or triage a whole book
  with the property book and attention queue.
- [Job context](reference/capabilities/job-context.md) — the job-grain
  equivalent of property context: rank a branch/division's active (WIP) job
  book, then pull a compact card and ticket/crew/billing/issue/health-history
  drilldowns for one job.
- [Renewal opportunities](reference/capabilities/renewal-opportunities.md) — the
  renewal book for a window: prior contract baseline, pipeline by status,
  retention, change tags, plus per-property service comparisons and prior-year
  performance review.
- [Command Center notes](reference/capabilities/command-center-notes.md) — resolve
  a property from a meeting's primary contact, have the user confirm the exact
  property, then write a Command Center property note with an optional Aspire
  property-note append.
- [Budget planning](reference/capabilities/budget-planning.md) — propose a
  create or edit to a property's budget item, review near-duplicate warnings,
  and save only after explicit approval; a saved item is live immediately.
- [Price recommendations](reference/capabilities/price-recommendations.md) —
  propose a create or edit to a property's price increase recommendation and
  save — always as a draft for a person to review — only after explicit
  approval.
- [Improvement plans](reference/capabilities/improvement-plans.md) — read the
  Command Center improvement plans the connected user can see, and start a
  new one through a prepare-then-save flow; live on save, one open plan per
  property and goal.
- [Product feedback](reference/capabilities/product-feedback.md) — log an unmet
  request (metric, data shape, workflow, or action) for Capsa product review
  when the connector can't satisfy it; loop step 5.
- [Scorecard queries](reference/capabilities/scorecard-queries.md) — run
  supported Ops or Sales Scorecard analytics with explicit dates, metrics,
  dimensions, and filters, and drill into the rows behind one cell.
- [Property analytics](reference/capabilities/property-analytics.md) — run
  Property Penetrations or Property Profitability by-property reports with
  explicit dates, filters, and defaults.

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
- `capsa_query_property_book` — a lean, sortable, paginated summary row per
  property across a filtered book, plus book-level totals, for ranking or
  reviewing a whole book (see property-book-triage).
- `capsa_get_attention_queue` — a fixed-order "what needs my attention
  today" triage queue over a property book (see property-book-triage).

Job context:

- `capsa_list_job_filter_options` — list the Branch, Division, and
  Operations Manager filters available to the connection for the job book,
  plus the job-grain metric-filter vocabulary.
- `capsa_query_job_book` — a lean, sortable, paginated summary row per
  active (WIP) job across a filtered book, plus book-level totals.
- `capsa_get_job_context` — a compact single-job card: identity, health,
  job-to-date financials, budget, progress, schedule, billing summary,
  change orders, ticket status counts, and open issue count.
- `capsa_get_job_context_drilldown` — one focused block of detail behind a
  single job: ticket breakdown, change orders, open issues, recently
  completed issues, crew-leader breakdown, billing breakdown, or health
  history.

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

Command Center notes:

- `capsa_find_properties_by_primary_contact` — find every accessible property
  for a primary-contact email or fuzzy name before writing a note; returns the
  full candidate list and whether user selection is required.
- `capsa_create_command_center_note` — write a Command Center property note
  against a single, user-confirmed property, with an optional Aspire
  property-note append and an optional future-plans flag
  (`add_to_future_plans`) that surfaces the note back in
  `capsa_get_property_context`'s `future_plans` block.

Budget planning:

- `capsa_prepare_budget_item_change` — propose a create or edit to a
  property's budget item and return near-duplicate warnings; writes
  nothing.
- `capsa_save_budget_item_change` — save exactly one reviewed budget item
  proposal after explicit user confirmation. A confirmed save is live in
  Command Center planning immediately — there is no draft state.

Price recommendations:

- `capsa_prepare_price_recommendation_change` — propose a create or edit to
  a property's draft price increase recommendation and return
  near-duplicate warnings; writes nothing.
- `capsa_save_price_recommendation_change` — save exactly one reviewed
  price recommendation proposal, always as a draft, after explicit user
  confirmation.

Improvement plans:
- `capsa_list_improvement_plans` — the Command Center improvement plans the
  connected user can see, optionally for specific properties.
- `capsa_get_improvement_plan` — one plan with its live measurement, why it is
  surfacing, and recent events.
- `capsa_prepare_improvement_plan` — propose a new plan (no write) and get a
  proposal token.
- `capsa_save_improvement_plan` — create exactly one reviewed plan after the
  user's explicit approval; live in Command Center immediately.

Product feedback:

- `capsa_log_feature_request` — capture an unmet user request (metric, data
  shape, workflow, or action) for Capsa product review; loop step 5.
- `capsa_describe_analytics_catalog` — check for a cataloged metric or
  scorecard shape before logging a metric-gap feature request, so the logged
  request includes the closest match.

Scorecard queries:

- `capsa_describe_analytics_catalog` — describe available Capsa metrics,
  scorecard dimensions, filters, time grains, and defaults; call this
  before a query when the shape is uncertain.
- `capsa_query_scorecard` — run supported Ops or Sales Scorecard analytics
  with explicit dates, metrics, dimensions, filters, and guidance.
- `capsa_get_scorecard_drilldown` — return the visit/work-ticket or
  opportunity rows behind one selected scorecard cell.

Property analytics:

- `capsa_query_property_analytics` — run Property Penetrations or Property
  Profitability by-property report analytics with explicit dates, filters,
  defaults, and guidance.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Recipes should be procedural, use
fictional examples, and keep the user firmly in the approval loop.
