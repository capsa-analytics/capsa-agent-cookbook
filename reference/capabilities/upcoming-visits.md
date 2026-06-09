# Upcoming visits (`upcoming_visits`)

Find upcoming scheduled visits with property, service, account-owner, and customer
contact context for notice workflows.

> This page mirrors `capsa_describe_capability` for `upcoming_visits`. The live
> output is the source of truth; filter **values** are connection-specific — call
> `capsa_list_upcoming_visit_filter_options` at runtime. For exact tool
> inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user asks for upcoming visits over the next few days.
- The user wants visits filtered by Branch, Account Owner, Division, Service Type,
  or Service.
- The user wants customer contact context for a scheduled visit notice.

## Tools

- `capsa_list_upcoming_visit_filter_options` — list Branch, Account Owner,
  Division, Service Type, and Service values available to the connection.
- `capsa_find_upcoming_visits` — list upcoming visits with property and customer
  contact context.

## Filter dimensions

Enumerable via `capsa_list_upcoming_visit_filter_options`: **Branch**,
**Account Owner**, **Division**, **Service Type**, **Service**.

`capsa_find_upcoming_visits` accepts — resolve names to IDs first (see the
[Resolving ambiguous names](../patterns/resolve-ambiguous-names.md) pattern):

| Dimension | Field | Type |
| --- | --- | --- |
| Branch | `branch_ids` | int[] |
| Account Owner | `account_owner_ids` | int[] |
| Division | `division_ids` | int[] |
| Service Type | `service_type_ids` | int[] |
| Service | `service_ids` | int[] |
| Property | `property_ids` | int[] |

Window & scope: `lookahead_days`, `max_rows`.

## Boundaries

- Capsa does not send customer notices; drafting and email-provider handoff happen
  outside Capsa.
- No completion-write tool — do not record completion for visits.
- Capsa resolves data access from the connection.
- Same-day dispatch decisions should verify freshness.

## Freshness

Data may be up to 24 hours old; don't treat it as live dispatch status.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Skill: [sensitive-visit-notice](../../skills/sensitive-visit-notice/)
