# Updates (`updates`)

Read the automation alerts that appear in My Work, and record or undo a response
to a response-required alert after the user confirms it. Alerts come only from
the automation rules a company has turned on; the rules own what qualifies, who
is told, the instructions and the deadline.

> This page mirrors `capsa_describe_capability` for `updates`. The connector's
> live output is the source of truth. For exact tool inputs and outputs, call
> `capsa_describe_tool`.

The older update feed, update playbooks, update settings tools and the
acknowledgment step are retired. Setting up which alerts a company gets is done
in the company's automation rules, not through the updates tools.

## Use when

- The user asks what alerts are open for them, or what is expected of them and by when.
- The user wants to work through open response-required alerts with you
  proposing each response.
- The user has done something about an alert and wants it recorded, or wants to
  undo a response they recorded.

## Vocabulary

- **Alert** — one automation alert, identified by `alert_id`. It is either
  *informational* (no response is accepted) or *response-required*.
- **Response** — what a person recorded on a response-required alert: **Noted**,
  **Contacted customer**, **Work assigned**, or **Not actionable** (with the
  person's reason). One live response is allowed per alert.
- **Linked work** — a task or issue tied to the alert.

## Tools

Reads (never record anything, never mark Seen):

- `capsa_describe_updates` — the response kinds the backend supports and what
  each needs.
- `capsa_list_updates` — informational and response-required alerts.
- `capsa_list_update_work` — only the response-required alerts.

Each alert carries `alert_id`, the rule and record context, the headline and
body, the assignee, the response deadline, the current response, linked work,
`can_respond` and `can_undo`, plus pagination, warnings and freshness.

Responses (**Record update responses** permission; a Work assigned that creates
its task or issue also needs **Create Aspire issues and tasks**):

- `capsa_prepare_update_response` — review one response on one alert: checks the
  grants the response needs and returns a `proposal_token`, `expires_at` and a
  `review` (the alert, the normalized response and a plain summary). Records
  nothing.
- `capsa_record_update_response` — record exactly the reviewed response after the
  user confirms it. Takes only `proposal_token` and `confirmed: true`.
- `capsa_prepare_update_response_undo` — review undoing the connected author's
  standing response (`alert_id`, `response_id`). Undoes nothing.
- `capsa_undo_update_response` — undo exactly the reviewed response after the
  user confirms it. Takes only `proposal_token` and `confirmed: true`.

When a company requires task or issue types, `capsa_get_work_creation_options`
checks the type and destination first (see Work assigned below).

## Filters and paging

| Input | Where | Values |
| --- | --- | --- |
| `scope` | list tools | `mine` (default) or `all` |
| `status` | list tools | `open` (default) or `all` (adds history) |
| `property_ids` | list tools | property IDs from `capsa_search_properties`; blank means the full allowed scope |
| `cursor` / `limit` | list tools | continue with `pagination.next_cursor` until `has_more` is false |

Every read also takes `user_request`. No recent-date window expires an
outstanding alert. Use the `alert_id` from the current read; ids from an earlier
session are not reliable.

## Recording a response

A response is two steps. `capsa_prepare_update_response` takes `user_request`,
the `alert_id` from the read and one `response`, and returns the review. Show it
to the person. Only after they confirm it, `capsa_record_update_response` takes
`{"proposal_token": "<from the review>", "confirmed": true}` and nothing else,
and records exactly the reviewed response. A review belongs to the person who
made it, works for its own save only (a record review cannot undo), expires
after 20 minutes and is used once: sending it again returns the first result
with `replayed: true` and never records a second response or creates a second
task. Grants are checked again when recording. A caller-written `confirmation`
object is not accepted. Undo works the same way:
`capsa_prepare_update_response_undo` (`alert_id`, `response_id`), then
`capsa_undo_update_response` with the token. Only the author of the standing
response can undo it, only when the alert shows `can_undo`, and undo never
deletes linked tasks or issues. Informational alerts accept no response.

| Kind | Fields | Use it when |
| --- | --- | --- |
| `noted` | `note` (optional, up to 5,000 characters), `append_to_aspire_property_note` (optional; needs *Add notes to Aspire* and a nonempty note) | The person acknowledged the alert and a line or two is the record. Noted does not establish that corrective work happened. |
| `contacted_customer` | `channel` (`email`, `call`, `text`, `in_person`), `contacted_on` (YYYY-MM-DD, today or earlier), `summary` (optional, short) | The customer was actually reached, after a send through a connected email provider or on the user's word that a call happened. It never sends a message. |
| `work_assigned` | Either `action_item_id` (work already linked to the alert) or `work` — `item_type` (`task` or `issue`), `subject`, `assigned_to_contact_id` (a current Aspire employee), and optional `notes`, `due_date`, `priority`, `notify_assignee`; with company work types also `work_type_id`, `work_type_revision`, `subject_detail`, `destination_choice`, `opportunity_id`, `work_ticket_id` | Someone else must do something, or it belongs on a later date. The review names the item being created. Creating it needs **Record update responses** and **Create Aspire issues and tasks** for that item kind together. |
| `not_actionable` | `reason` (required) | Nothing is needed. The reason comes from the person; the connector refuses without one. |

For Work assigned in a company that requires work types, call
`capsa_get_work_creation_options` first, with `resource` (`Task` or `Issue`),
the target, the selected `work_type_id`, `subject_detail` and
`destination_choice`. Use the rendered subject and exact `revision` it returns
in `work.subject` and `work.work_type_revision`. A changed or inactive type, or a
moved destination, needs a new review; never fall back to free text to get
around company policy.

A response can be recorded while its optional Aspire note delivery is queued or
fails; the result reports the two separately. Do not retry the whole response
just to resend the note.

## When the connector refuses

A refused call names one code. Nothing is recorded unless the table says
otherwise; never look for another tool to get around a refusal.

| Code | What happened | What to do next |
| --- | --- | --- |
| `permission_denied` | A grant is off, or the person lacks access to the property; the message names the control. | Stop and tell the person which control in Users & Permissions to turn on (both **Record update responses** and **Create Aspire issues and tasks** for a Work assigned that creates its item), or that the property is outside their access. Do not broaden reads. |
| `not_found` | The alert is not reachable. | Read again; if it is still missing, it is not this connection's to answer. Say so. |
| `conflict` | The alert changed or already has a response. | Read the alert and its linked work again, show the person what stands, and propose afresh; never resend the same call. |
| `invalid_request` | The input is malformed, a reason is missing, the review expired (20 minutes), was already used for a different save, or belongs to another person, or the assignee is not a current Aspire employee. | Fix the call and confirm any changed response again. For a missing, expired or used review, prepare again, show the new review and ask again. |
| `work_created_not_recorded` | The task or issue was created but the response was not recorded. | Keep the created item's evidence; never resend the create. |
| `unavailable` | Nothing was recorded when the failure came before a write was sent. | Tell the person it is not recorded yet and retry a little later. |
| `outcome_unknown` | The connector could not confirm whether the response was recorded; for a Work assigned that creates its item, the task or issue may exist in Aspire. | Read the alert and its linked work again before retrying. Have the person check the property's tasks and issues first; a blind retry can create a duplicate. |

## Boundaries

- Reading, drafting, proposing and reviewing are never responses. Nothing is
  recorded without the user's confirmation of the review Capsa returned.
- A note is proof only when the person actually did the thing it describes.
- The connector never sends email or messages; Contacted customer is recorded after
  the send happened elsewhere, or on the user's word.
- Properties are shown by name, with the id beside it when that helps; never the
  id alone.

## Freshness

Alerts reflect Capsa as of the read. The Aspire facts behind an alert and linked
task completion can be up to 24 hours old. A warning about a missing Aspire
identity is not proof of an empty queue, and an unavailable source is never
reported as zero alerts.

## Related

- Skill: [work-the-updates-loop](../../skills/work-the-updates-loop/)
- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
