# Company settings (`configuration_settings`)

Explain company report groups, Command Center rules and health update modes,
then prepare and save exact changes after review.

> Availability and current inputs come from `capsa_describe_capability` and
> `capsa_describe_tool`. Discover the live connection first; a documented action
> may not yet be available on every connector deployment.

## Rules: discover, explain, prepare, save

Start with `capsa_list_setting_families`, then `capsa_explain_setting` for the
requested family. Explain returns its current definition, revision, choices,
meaning and dependencies. Use stable choices returned by Capsa; preserve
unrelated rules and surface missing or ambiguous choices for correction.

This workflow uses these family-specific pairs:

| Family | Prepare | Save |
| --- | --- | --- |
| Financial Health rules | `capsa_prepare_property_financial_health_rules_change` | `capsa_save_property_financial_health_rules_change` |
| Relationship Health rules | `capsa_prepare_property_relationship_health_rules_change` | `capsa_save_property_relationship_health_rules_change` |
| Property Tier rules | `capsa_prepare_property_tier_rules_change` | `capsa_save_property_tier_rules_change` |

Prepare uses the revision from explain and the complete proposed definition.
Show the returned before/after, consequences, warnings and expiry. Save only
that `proposal_token` with `confirmed: true` after explicit approval.

When changing Financial and Relationship rules together, save Financial first,
then re-read and prepare Relationship. Its preview must reflect the Financial
rules now saved. Show and confirm that preview before saving it. These are
separate family saves; report success or failure for each.

## Health update modes

- `capsa_get_health_update_modes` — read current Financial and Relationship
  modes and the current revision.
- `capsa_prepare_health_update_mode_change` — preview both selected modes with
  `expected_revision`, `modes` (`financial_mode`, `customer_mode`, each `review`
  or `automatic`), and `older_assessments` (`keep` or `replace`) when applicable.
- `capsa_save_health_update_mode_change` — save only the reviewed `proposal_token`
  with `confirmed: true` after explicit approval.

Review keeps recommendations for a person's decision. Automatic Financial
Health follows company Financial rules through normal Capsa evaluation; show
the preview's effects and whether older Financial assessments will be kept or
replaced. That choice needs explicit consent. Automatic Relationship Health
can lower a status under the company's supported complaint or tag rules; it
never automatically upgrades the relationship. Read the returned timing rather
than promise immediate recalculation.

## Permission and effect boundaries

Rule saves need the relevant **Change company settings** family grant. Mode
saves need the separate **Change health update modes** grant. Existing app
rights remain the ceiling. These tools cannot grant permissions.

Saving rules changes the company definition. It does not apply Property Tier
recommendations, change health update modes, or record a single-property health
decision. Existing Automatic evaluations may use new rules; in Review, new rules
change recommendations. Explain that effect before a rule save.

After saving tier rules, offer reviewed tier application through
[property tiers](property-tiers.md). After saving health rules, read modes and
offer a separate review of Automatic or Review for each assessment. Follow the
[setup recipe](../../skills/property-health-and-tier-setup/SKILL.md).

## Recovery

An uncertain proposal-save result is recovered by retrying the same token.
A genuine conflict, expired token, changed definition or dependency requires a
fresh read, preview and user confirmation. Do not manufacture a new revision or
repeatedly retry the stale proposal. Keep a receipt for each family and action.
