# Property tiers (`property_tiers`)

Read selected properties' saved tiers and current company-rule recommendations,
then apply recommendations or person-chosen tiers through a reviewed batch.

> Discover availability through `capsa_describe_capability`; use
> `capsa_describe_tool` for exact live inputs and returned review details.
> Documentation alone does not establish a connection's access or deployment.

## Tools

- `capsa_get_property_tiers` — read 1–100 explicit `property_ids` with their
  saved tiers, recommendations and current revision.
- `capsa_prepare_property_tier_change` — preview an explicit batch using
  `expected_revision`, `operation`, and `items` containing `property_id`.
  `operation: apply_recommendations` uses current company recommendations;
  `operation: assign` also supplies the person-chosen `tier` for each item.
  The supported tiers are A, B and C; confirm the live schema before use.
- `capsa_save_property_tier_change` — save the reviewed `proposal_token` with
  `confirmed: true` after the person approves the exact batch.

Resolve property names first. Show each property's current and proposed tier,
unchanged or skipped items, warnings and expiry from prepare. Review at most
100 properties in one proposal. A larger requested book must be resolved into
explicit accessible properties and reviewed in bounded batches; there is no
implicit company-wide apply action. Explain the full scope and any incomplete
paging before claiming coverage.

## Permissions and boundaries

Reads use the connection's Property Context access and property limits. Applying
tiers also needs **Apply property tiers** and the person's existing company-settings editing rights.
This grant is separate from company Property Tier rule editing and from health
status or health update mode changes. The connector cannot expand app rights.

Saving tier rules does not assign tiers. Offer to show current company-rule
recommendations after a successful rule save, then prepare, review and save the
selected batch only after explicit approval. A person may instead choose an
explicit tier for selected properties. No action changes Aspire.

## Recovery

After an uncertain proposal save, retry the same token to recover its outcome.
For a genuine conflict or expired proposal, read current tiers and recommendations,
prepare a fresh preview, and obtain fresh consent. Never use an old recommendation
as though it were current or call an uncertain save failed.

See the [health and tier setup recipe](../../skills/property-health-and-tier-setup/SKILL.md)
for the full sequence and post-save offers.
