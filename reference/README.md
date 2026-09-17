# Reference

The comprehensive, capability-led map of the Capsa connector. The connector's live
`capsa_describe_capability` is the source of truth; these pages mirror it and
document each capability's tools, dimensions, filters, and boundaries. Filter
**values** are connection-specific — call the `capsa_list_*_filter_options` tools
at runtime rather than assuming them.

## Capabilities

- [followup_actions](capabilities/followup-actions.md) — Outstanding proposal follow-ups with customer context and contact candidates; evidence-gated completion.
- [upcoming_visits](capabilities/upcoming-visits.md) — Scheduled visits with property, service, account-owner, and customer-contact context for notice workflows.
- [property_context](capabilities/property-context.md) — Search properties and pull production, satisfaction, sales, and upcoming-visit signals; filter, rank, or triage a property book by dimension, metric, or date range.
- [job_context](capabilities/job-context.md) — The job-grain equivalent of property context: rank a branch/division's active (WIP) job book, then pull a compact card and ticket/crew/billing/issue/health-history drilldowns for one job.
- [renewal_opportunities](capabilities/renewal-opportunities.md) — The renewal book for a window — prior contract baseline, pipeline by status, retention, price/scope change tags — plus per-property service comparisons and prior-year performance review.
- [command_center_notes](capabilities/command-center-notes.md) — Resolve a property from a meeting's primary-contact context, have the user confirm the exact property, then save a Command Center property note with an optional Aspire property-note append.
- [budget_planning](capabilities/budget-planning.md) — Propose a create or edit to a property's Command Center budget item, review near-duplicate warnings, and save only after explicit approval. A saved item is live in Command Center planning immediately.
- [price_recommendations](capabilities/price-recommendations.md) — Propose a create or edit to a property's draft Command Center price increase recommendation, review near-duplicate warnings, and save — always as a draft for a person to review — only after explicit approval.
- [product_feedback](capabilities/product-feedback.md) — Log an unmet user request (metric, data shape, workflow, or action) for Capsa product review when the connector can't satisfy it. Loop step 5.
- [scorecard_queries](capabilities/scorecard-queries.md) — Run supported Ops or Sales Scorecard analytics with explicit dates, metrics, dimensions, and filters, and drill into the rows behind one selected cell.
- [property_analytics](capabilities/property-analytics.md) — Run Property Penetrations or Property Profitability by-property report analytics with explicit dates, filters, defaults, and guidance.

## Patterns

- [Resolving ambiguous names](patterns/resolve-ambiguous-names.md) — work out which
  dimension a user's term belongs to before filtering or reporting.
