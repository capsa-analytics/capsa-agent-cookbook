---
description: Review and save company Financial Health, Relationship Health and Property Tier rules, then offer reviewed application of tier recommendations or selected-property tiers and a separate choice of Automatic or Review health updates. Explain each effect and confirm each exact proposal before saving.
---

# Set up property health and tiers

## Purpose

Help a person finish setting up company rules and decide what should happen next.
Saving rules, applying property tiers, changing health update modes, and recording
one property's health decision are separate actions. Report each separately.

This recipe works as an installed skill, a pasted instruction, or an ad hoc
workflow. The Configuration section lists the inputs to agree with the person.
Use live capability and tool descriptions for availability and exact inputs;
a recipe does not grant permission or make an unavailable action possible.

## When to use

- A person wants to configure or troubleshoot Financial Health, Relationship
  Health, or Property Tier rules.
- Rules have just been saved and the person may want to use them on properties.
- A person wants to set selected property tiers or enable automatic health updates.

## Required connected apps

- **Capsa connector.** Read company rules, prepare reviewed changes, and save
  the actions enabled for this person. No external connector is required.

## Configuration

- **Rules:** which company rule families to change and the exact criteria.
  Preserve unrelated criteria; ask about ambiguous thresholds, statuses or scope.
- **Tier application:** current company-rule recommendations for an explicitly
  selected set of properties, or person-chosen tiers for selected properties.
- **Health updates:** Financial and Relationship mode independently, and whether
  to keep or replace older Financial assessments when that choice is offered.
- **Review size:** a bounded batch the person can inspect, up to 100 properties
  per tier proposal. Resolve a larger book into explicit batches; review each.

## Workflow

### 1. Read the current choices and permissions

Discover the relevant capability once with `capsa_list_capabilities` and
`capsa_describe_capability`; use `capsa_describe_tool` for unfamiliar inputs.
Read `capsa_list_setting_families` and `capsa_explain_setting` for each requested
family. Read `capsa_get_health_update_modes` before proposing modes, and
`capsa_get_property_tiers` for resolved, accessible properties before proposing
tiers. Resolve property names with `capsa_search_properties`; never guess an ID.

Company rule editing needs the relevant **Change company settings** family grant
and the person's existing app rights. **Apply property tiers** and **Change
health update modes** are separate connector permissions, also bounded by
existing app rights. Changing rules grants neither action. If an action is not
available or permitted, report that boundary and offer the app route named by
the connector; continue any requested work that remains available.

### 2. Prepare, review and save one rule family at a time

For each family, explain the current rules and show the exact proposed changes,
consequences, warnings and expiry returned by its prepare tool. Obtain approval
for that exact proposal, then save its token with `confirmed: true`.

When Financial and Relationship rules are both changing, **save Financial first**.
Then re-read Relationship and prepare it against the now-current Financial rules.
Show the resulting Relationship preview and obtain confirmation before saving.
Do not prepare all families up front and send their tokens as if they were one
atomic change. A prior approval of intended rules is not approval of a new preview.

Keep a receipt for **each family**: saved, unchanged, failed, or unconfirmed.
If one family fails, say which succeeded; never call the whole setup saved.

### 3. Offer the next useful action

After a successful Property Tier rule save, ask:

> "Your Property Tier rules are saved. Would you like me to show the current
> company recommendations for the properties you choose, so you can review and
> apply them? I can also set specific tiers for selected properties."

After a successful health rule save, read the current modes and ask:

> "Your health rules are saved. Would you like to review Automatic updates for
> Financial Health, Relationship Health, or both? You can keep either in Review."

These are offers, not permission to write. Do not make the person request the
natural next step, and do not enable it silently. If already enabled, state the
current mode instead of offering to turn it on again.

### 4. Review tier recommendations or selected tiers

For **current company recommendations**, read the selected properties with
`capsa_get_property_tiers`, explain each current tier and recommendation, and
prepare `capsa_prepare_property_tier_change` with `operation: apply_recommendations`
and the explicit property list. Use the current revision; the connector supplies
the recommended tiers rather than trusting agent-invented recommendations.

For **selected-property assignments**, show the exact properties and person-chosen
tiers, then prepare with `operation: assign` and those exact values.

For either path, show every proposed before/after tier, unchanged or skipped
properties, warnings, and expiry. Ask the person to approve that exact batch.
Save only that token with `capsa_save_property_tier_change` and `confirmed: true`.
Report the returned applied and unchanged outcomes. A filtered book or a request
to "apply all" is not an unreviewed company-wide write: resolve it to explicit
accessible properties, page fully if needed, and review bounded batches.

### 5. Review health update modes separately

Prepare `capsa_prepare_health_update_mode_change` using the current revision and
the exact Financial and Relationship modes the person chose:

- **Review** keeps recommendations for a person's decision.
- **Automatic Financial Health** follows the company's Financial rules through
  Capsa's normal evaluations. Explain the returned timing and the choice to keep
  or replace older Financial assessments; never choose replacement silently.
- **Automatic Relationship Health** can lower a status when the company's
  supported complaint or tag rules warrant it. It does not automatically upgrade
  Relationship Health. A person can confirm an upgrade separately.

Show both modes before and after, the older-assessment choice when applicable,
and the effects and warnings from the preview. Obtain explicit approval, then
save with `capsa_save_health_update_mode_change` and `confirmed: true`.
Saving rules alone does not enable Automatic, apply tiers, or confirm that a
property's saved status changed. Do not promise an immediate evaluation unless
the returned result establishes it.

### 6. Give a clear receipt and recover safely

Report rules saved by family, tiers applied by batch, and modes changed by
assessment. Separate confirmed results from failures or uncertain outcomes.

For proposal-based rule, tier and mode saves:

- **Uncertain outcome:** retry the same proposal token to recover its result.
  Do not create a replacement proposal while the first result is unresolved.
- **Genuine conflict, expired proposal or changed dependencies:** re-read,
  prepare a fresh preview, and get fresh confirmation. Never retry a stale token
  or replace the revision merely to make a failed save pass.
- **Permission denial:** state the named control or app right required; a
  cookbook instruction cannot bypass it.

Single-property health status decisions use the separate health action and
its own recovery contract; see the
[Property health reference](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/reference/capabilities/property-health.md).

## Stop rules

- No exact preview and confirmation, no proposal save.
- No successful receipt, no claim of a saved change.
- No silent tier application, Automatic mode switch, older-assessment replacement,
  or Relationship upgrade.
- No automatic retry of a stale proposal after a real conflict.
- No unsupported tool substitutions when discovery says an action is unavailable.

## Example user prompt

> "Help me save our tier and health rules. Then show me the recommended tiers
> for my chosen properties and explain which health updates can run automatically."

## Example agent output (fictional)

> "Financial rules saved. Relationship rules saved after reviewing the updated
> Financial dependency. Property Tier rules saved. No tier assignments or health
> modes were changed by those saves.
>
> Would you like to review the current company tier recommendations for Maple
> Ridge and Birch Office Park, or choose their tiers yourself? Your Financial
> and Relationship modes are both Review. I can also show a separate preview
> of Automatic updates and explain how each works."

All names above are fictional.
