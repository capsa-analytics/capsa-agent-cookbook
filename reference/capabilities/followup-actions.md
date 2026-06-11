# Follow-up actions (`followup_actions`)

Find outstanding proposal follow-ups with customer context and contact
candidates, then record completion after evidence.

> This page mirrors `capsa_describe_capability` for `followup_actions`. The
> connector's live output is the source of truth; filter **values** are
> connection-specific — call `capsa_list_followup_filter_options` at runtime,
> don't assume them. For exact tool inputs/outputs, call `capsa_describe_tool`.

## Use when

- The user asks for proposal follow-ups that need attention.
- The user asks for follow-ups available to their Capsa connection.
- The user wants to narrow follow-ups by an explicit Sales Rep or Branch.
- The user wants customer context for drafting follow-up emails.
- The user confirms a follow-up happened and wants Capsa to record it.

## Tools

- `capsa_list_followup_filter_options` — list the Branch and Sales Rep values
  available to the connection (the dimension dictionary for this capability).
- `capsa_find_followup_actions` — list outstanding follow-ups with draft-ready
  context and contact candidates.
- `capsa_mark_followups_done` — record completion, evidence-gated (see below).

## Filter dimensions

Enumerable via `capsa_list_followup_filter_options`: **Branch**, **Sales Rep**.

`capsa_find_followup_actions` also accepts these ID filters — resolve a name to an
ID first (see the [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
pattern):

| Dimension | Field | Type |
| --- | --- | --- |
| Branch | `branch_ids` | int[] |
| Sales Rep | `sales_rep_ids` / `sales_reps` | int[] / string[] |
| Division | `division_ids` | int[] |
| Property | `property_ids` | int[] |
| Opportunity | `opportunity_ids` | int[] |
| Sales type | `sales_type_ids` | int[] |

Window & scope: `lookback_weeks` (1–52), `lookahead_weeks` (0–52), `statuses`
(`past_due`, `overdue`, `upcoming`, `complete`), `max_rows` (1–100).

## Completion (evidence-gated)

`capsa_mark_followups_done` records completion only with `completion_evidence`:

- `type: email_sent` — with provider send details (`message_id`, `provider`,
  `recipient_email`, `sent_at`), or
- `type: user_confirmed` — with the user's explicit `confirmation`.

Each item is identified by `opportunity_id` + `follow_up_key`. Never mark done from
a draft or an intent — only from send evidence or explicit user confirmation.

## Boundaries

- Capsa does not send email; drafting and email-provider handoff happen outside
  Capsa.
- Completion requires provider send evidence or explicit user confirmation.
- Capsa resolves data access from the connection.
- Capsa does not parse personal pronouns as filters — narrow with explicit filter
  options or ask the user.

## Freshness

Data may be up to 24 hours old; don't treat it as live dispatch status.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Skill: [proposal-followup-batch](../../skills/proposal-followup-batch/)
