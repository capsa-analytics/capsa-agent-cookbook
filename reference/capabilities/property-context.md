# Property context (`property_context`)

Search properties and retrieve operational context — contacts, relationship
status, production, satisfaction, sales, and upcoming-visit signals — for one
property, a selected set, or a filtered property book.

> This page mirrors `capsa_describe_capability` for `property_context`. The live
> output is the source of truth; filter **values** are connection-specific — call
> `capsa_list_property_context_filter_options` at runtime. For exact tool
> inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user gives a fuzzy or abbreviated property name and needs the right property
  identified.
- The user needs contact-ready property context before drafting customer
  communication.
- The user asks for one property's production, satisfaction, sales, or
  upcoming-visit context.
- The user asks to review a filtered property book for renewal, contact, or
  prioritization work.
- The user needs a focused drilldown behind one property.

## Tools

- `capsa_list_property_context_filter_options` — list the filter values available
  to the connection.
- `capsa_search_properties` — fuzzy-match a property, customer, contact, owner,
  tag, or ID and return contact-ready candidates (default 25 rows, up to 100).
- `capsa_find_properties_by_primary_contact` — resolve a primary-contact email
  or fuzzy name to accessible property candidates. Gated by this capability's
  read permission (it also appears in the Command Center notes workflow, but a
  connection needs only `property_context` to call it).
- `capsa_get_property_context` — compact context for one property, selected
  properties, or a capped, filtered property book.
- `capsa_get_property_context_drilldown` — one focused drilldown behind a single
  property.

## Filter dimensions

Enumerable via `capsa_list_property_context_filter_options` — resolve names to
values first (see the
[Resolving ambiguous names](../patterns/resolve-ambiguous-names.md) pattern):

| Dimension | Field | Type |
| --- | --- | --- |
| Branch | `branch_ids` | int[] |
| Account Owner | `account_owner_ids` | int[] |
| Division | `division_ids` | int[] |
| Property type | `property_type_names` | string[] |
| Tag | `property_tags` | string[] |
| Industry | `industry_names` | string[] |
| Work-ticket status | `work_ticket_statuses` | string[] |
| Property | `property_ids` | int[] |

**Metric filters** (on `capsa_get_property_context`): threshold conditions on
`total_revenue`, `contract_value`, `gross_margin_percent`, `gross_margin_dollars`,
and `total_cost` (operators `eq`/`neq`/`gt`/`gte`/`lt`/`lte`/`between`; ANDed within
a group, ORed across groups).

**Date range:** a `preset` (`last_365_days`, `last_90_days`, `current_year`) or an
explicit `start_date`/`end_date`.

**Drilldowns** (`capsa_get_property_context_drilldown`, one property at a time):
gross margin by division / service type / service / opportunity / work ticket; open
and recent complaints; open and recent-completed issues; delivered proposals;
proposed opportunities; active contracts; upcoming visits; last-touch activity.

## Boundaries

- Property context is read-only — no completion-write tool.
- Broad property-book pulls are capped; use filters or property IDs for exhaustive
  detail.
- Drilldowns are one-property detail pulls, not default portfolio payloads.
- Capsa resolves data access from the connection.
- Capsa does not parse personal pronouns as filters — use explicit filter options
  or ask the user to narrow.

## Freshness

Data may be up to 24 hours old; don't treat it as live dispatch status.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Skills: property context supplies the drafting context used across the pack.
