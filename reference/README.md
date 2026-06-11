# Reference

The comprehensive, capability-led map of the Capsa connector. The connector's live
`capsa_describe_capability` is the source of truth; these pages mirror it and
document each capability's tools, dimensions, filters, and boundaries. Filter
**values** are connection-specific — call the `capsa_list_*_filter_options` tools
at runtime rather than assuming them.

## Capabilities

- [Follow-up actions](capabilities/followup-actions.md) — outstanding proposal
  follow-ups with contact context; evidence-gated completion.
- [Upcoming visits](capabilities/upcoming-visits.md) — scheduled visits with
  property and customer-contact context for notice workflows.
- [Property context](capabilities/property-context.md) — search properties and
  pull production, satisfaction, sales, and visit signals; filter a property book
  by dimension, metric, or date range.

## Patterns

- [Resolving ambiguous names](patterns/resolve-ambiguous-names.md) — work out which
  dimension a user's term belongs to before filtering or reporting.
