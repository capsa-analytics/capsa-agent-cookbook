# Permission management

Help a super admin understand a teammate's effective access, reusable role
templates, and connector grants, then propose a narrowly scoped change for
review. Capsa is the authority for effective permissions and every save.

Capability id: `permission_management`. Check `capsa_list_capabilities` on the
active connection before relying on it. These tools appear only when the
connected person is a super admin with an active Capsa connector and **Manage
teammate permissions** enabled for that person in AI Connectors. The app can
enable that grant; the connector cannot enable itself. Use
`capsa_describe_capability` and `capsa_describe_tool` for current inputs.

## Read tools

- `capsa_list_teammate_permissions` — teammates, their current effective
  access, available pages, and report restriction dimensions.
- `capsa_explain_teammate_permissions` — one teammate or an existing pending
  invitation, including where effective access comes from.
- `capsa_list_role_templates` — reusable role templates. Assignment copies a
  template's access once; later template edits do not update prior assignees.
- `capsa_describe_role_template` — one template's access and revision.

Use an exact teammate reference returned by Capsa, or the email of an existing
pending invitation. Resolve duplicate names before discussing a change. Reads
and writes stay within the active connection's tenant.

## Review and save tools

| Job | Prepare a proposal | Apply that reviewed proposal |
| --- | --- | --- |
| Create or edit a reusable role | `capsa_prepare_role_template_change` | `capsa_save_role_template_change` |
| Assign a role to selected teammates or existing pending invitations | `capsa_prepare_role_assignment` | `capsa_apply_role_assignment` |
| Change a teammate's direct page, settings, report-limit, or connector permissions | `capsa_prepare_teammate_permission_change` | `capsa_apply_teammate_permission_change` |

Preparing stores an expiring proposal but does **not** change effective access.
It returns a `proposal_token`, before/after effective access, changes, access
lost, warnings, and expiry. Show these to the user for the exact target before
applying anything. A save takes only that token and `write_confirmation` with
`confirmed: true`, the identical token, and the user's nonempty confirmation
text. It does not take editable permission fields. If the request changes,
prepare a new proposal and obtain fresh approval.

Role definitions replace the complete reviewed role. Direct teammate changes
preserve omitted sections; an explicit empty restriction list clears that
restriction. A role assignment copies access at assignment time. A bulk role
assignment can contain up to 20 independent proposals: review and confirm each
person, then report each success or failure separately. One failure does not
undo successful items.

## Boundaries

- A connector grant can narrow authority, never elevate app rights. Capsa
  rechecks tenant membership, super-admin status, the management grant, and
  current revisions when a proposal is applied.
- The connector refuses changes to the caller's own access, another super
  admin, the super-admin roster, suspended-access restoration, unknown
  invitation emails, and granting the management toggle to others. Use the
  app for protected operations; do not look for another tool to bypass them.
- A stale or expired proposal needs a new preview and review. If an apply
  result is uncertain, retry the **same** token to learn the outcome; do not
  create a new proposal and risk a duplicate change.
- A confirmed save changes live access and produces an audit record. Verify
  the result with a fresh list/explain read; never report success from the
  prepare response alone.

For the interview, recommendation, review, and verification sequence, use
the [teammate-permission-management skill](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/skills/teammate-permission-management/SKILL.md).
