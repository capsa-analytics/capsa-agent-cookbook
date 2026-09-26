---
description: Help a Capsa super admin review a teammate's effective access, choose the narrowest role or direct grant, preview the exact before/after change, apply only after explicit approval, and verify the live result.
---

# Teammate permission management

Understand the access a teammate has today, agree on the access their job
requires, and make only a reviewed change. The same steps work as an installed
skill, a pasted recipe, or an ad-hoc workflow. The Configuration section names
the inputs; a team may keep conventions in a system message or wrapper, but
must still resolve current permissions from Capsa.

## When to use

Use this for a super admin who wants to understand or change teammate access,
role templates, role assignments, or connector capabilities. For a read-only
question, stop after the explanation; do not prepare a proposal merely to
answer it.

## Required connected apps

- **Capsa MCP connector** with `permission_management` available on the
  active connection. No email or other connector is required.

If the capability is absent, say that it requires super-admin access, an
active connector, and the super admin's own **Manage teammate permissions**
grant in AI Connectors. Ask the user to configure it in the app. Do not try a
hidden tool, another tenant, or a different account to get around the gate.

## Configuration

- **Organization:** the intended Capsa organization when the user belongs to
  more than one. Never infer the tenant from a teammate's name alone.
- **Target:** an exact teammate reference returned by Capsa, or the email of
  an existing pending invitation. Confirm an ambiguous name.
- **Desired job and access:** the work the person should do; required pages,
  settings rights, report limits, and connector capabilities. Ask for missing
  business choices rather than inventing them.
- **Team conventions (optional):** approved role names or least-access rules.
  Treat these as recommendations, never as proof of the user's current access.

## Workflow

### 1. Confirm the connection and inventory access

Check `capsa_list_capabilities` for `permission_management`; use
`capsa_describe_capability` or `capsa_describe_tool` when a field is unclear.
Confirm the organization with the user if more than one is available. Call
`capsa_list_teammate_permissions` to resolve the exact person and current
effective access. If the target is ambiguous, ask which person before
continuing. Do not act on an unknown invitation email.

### 2. Explain the current state

Call `capsa_explain_teammate_permissions` for the selected target. For role
work, call `capsa_list_role_templates` and
`capsa_describe_role_template` for plausible existing roles. Explain direct
grants, role-derived access, report restrictions, and connector status in
plain language. Label a pending invitation as pending.

### 3. Interview for the smallest appropriate change

Ask what the teammate must accomplish and which access is unnecessary.
Compare an existing role with a narrow direct grant; prefer the smallest
change that covers the job. Tell the user when a role assignment would copy
its permissions **once**, so later edits to the template will not update
that teammate. If creating or editing a role, review its *complete* access
definition. For a direct change, name every section being changed and leave
unmentioned sections alone. An empty restriction list means no restriction
on that dimension; never use it casually.

### 4. Prepare and show the exact proposal

Use the matching prepare tool for a role template, role assignment, or
teammate change. Preparation stores a temporary proposal, not a permission
change. Present the target, before/after effective access, every grant and
removal, connector capability changes, access lost, warnings, and expiry.
For a bulk assignment, show each person's proposal separately. If the
result conflicts with the user's intent, stop and prepare a corrected one.

### 5. Ask for explicit approval, then apply

Ask the user to approve the **specific prepared proposal**. A request to
"manage permissions" or agreement with a general plan is not approval to
apply it. After approval, use the matching save/apply tool with the original
`proposal_token` and `write_confirmation` containing `confirmed: true`, the
same token, and a nonempty summary of what the user confirmed. Never pass
editable permission fields to an apply tool. For a batch, apply only the
items the user approved; each item has its own token and confirmation.

### 6. Verify and report

Read the teammate or role again and compare effective access with the
approved proposal. State which changes are live, which individual batch
items failed, and any access still needing action. If an apply times out or
the result is unclear, retry the original token before proposing anything
new. If the proposal is stale or expired, explain the conflict, obtain a
fresh preview, and ask for approval again.

## Stop rules

- Never apply a permission change without explicit approval of the exact
  before/after proposal and target. These changes take effect immediately.
- Never change the caller's own access, another super admin's access, the
  super-admin roster, suspended status, or the management toggle through
  this connector. Direct the user to the app for protected changes.
- Never create a new invitation here. A pending email must already exist.
- Never treat a role template edit as an update to people who previously
  received that role. Verify each affected person's live access after an
  approved assignment or direct change.
- On denial, stale review, or ambiguous identity, stop and explain the
  visible reason; do not route around it with another connection or tool.

## Example user prompt

> "In my Capsa organization, explain Avery Stone's current access. Avery
> needs to review property work but should not manage organization settings.
> Recommend the smallest change and show me what it would do. Don't apply
> anything until I approve the exact preview."

## Example agent output (fictional)

> "I found one Avery Stone. Their current access includes the Property
> Command Center and organization-settings changes. I recommend removing
> only the settings-change right; their page access stays as it is. The
> preview shows that Avery would lose the ability to change shared settings
> and no other access would change. This takes effect immediately if saved.
> Do you approve this exact change for Avery Stone?"

After explicit approval, apply the original reviewed token, read Avery's
access again, and report the actual saved result. All names above are
fictional.

## Team specifics

<!-- Keep local role conventions here. Re-pull after a connector upgrade. -->
