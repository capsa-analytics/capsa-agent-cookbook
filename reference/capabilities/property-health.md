# Property health (`property_health`)

Read a property's separate Financial and Relationship assessments, evidence and
history, then record an allowed single-property decision.

> The live `capsa_describe_capability` and `capsa_describe_tool` outputs determine
> availability, exact inputs and current permissions. Relationship is called
> `customer` in tool fields; present it as Relationship Health to the person.

## Tools

- `capsa_get_property_health` — read a resolved `property_id`, its Financial
  and Relationship statuses, current Relationship recommendation and histories.
- `capsa_update_property_health` — save a person-confirmed Financial or
  Relationship status, or a current rule-backed Relationship downgrade.

Manual decisions require confirmation of the exact property and status change,
including the actual property name. Read first and use the expected previous
status when supported, so another person's intervening decision is not overwritten.
Show the returned outcome; no write goes to Aspire.

## Permissions and limits

Property Context access and the person's Command Center property scope apply.
Writes additionally require **Update Financial health** or **Update Relationship
health**, respectively, and connector write access. A person can confirm a
Relationship upgrade or downgrade; an agent never upgrades Relationship Health
on its own. An agent downgrade requires Automatic Relationship mode plus current,
pending rule-backed complaint or tag evidence and its current fingerprint.

Company rules and update modes belong to
[company settings](configuration-settings.md). **Change health update modes**
does not grant either individual health-status write, and the individual write
grants do not enable mode changes. Use the
[setup recipe](../../skills/property-health-and-tier-setup/SKILL.md) for a reviewed
choice of Automatic or Review after saving health rules.

## Recovery and freshness

A conflict means read the property's current health again before proposing
another decision. A stale recommendation must be re-read; never rewrite its
fingerprint to force a save. A single-property health write with an uncertain
outcome must be checked by reading the property's health and history before
trying again; do not apply the proposal-token retry rule to this separate action.

Statuses and histories reflect saved Capsa decisions. Complaint and tag evidence
comes from the latest Command Center refresh; state the freshness returned by
Capsa when it matters to the decision.
