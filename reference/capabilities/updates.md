# Updates (`updates`)

Read the company's update catalog, the playbooks that reach the connected
person (with the guidance an admin wrote for each one), the recent feed, and
the durable next steps with accountable people and recorded responses. Where
the connection allows it, explain and change update settings after review, and
record a response (creating the task or issue behind a Work assigned when the
person asks) or acknowledge completion after the user confirms.

> This page mirrors `capsa_describe_capability` for `updates`. The connector's
> live output is the source of truth. Update type IDs and playbook IDs are
> connection-specific — call `capsa_describe_updates` at runtime, don't assume
> them. For exact tool inputs/outputs, call `capsa_describe_tool`.

"Updates" is the umbrella: customer updates (what changed at a property — work
finished, a visit moved, a contract won or lost, an issue opened, an appointment
with no follow-up recorded) are the first family; crew and route updates are
planned on the same rails.

## Use when

- The user asks what changed at their properties, or what needs a response.
- The user asks what is expected of them (or their team) and by when.
- The user wants to work through open next steps with you proposing each response.
- An authorized admin wants update rules, a playbook, or its guidance explained or changed.
- The user has done something about an update and wants it recorded, or is the
  accountable person acknowledging a teammate's completion.

## Vocabulary

- **Update type** — one of the catalog's types (for example *Contract marked lost*,
  *Appointment with no follow-up recorded*). IDs come from `capsa_describe_updates`.
- **Playbook** — who hears about which types at which properties, plus what happens
  next for each type. Not to be confused with cookbook recipes.
- **Guidance** — the admin's advice for whoever responds to that type: what good
  looks like, when nothing is needed, when to escalate, who to contact. Returned
  with every open next step as `guidance`, as its playbook line reads today. It
  is the company's advice, not a record of work. Read it before proposing anything.
- **Next step** (a loop) — one update × one playbook, with an accountable person, a
  deadline on the organization's business-day calendar, and a response history.
- **Response** — what a person recorded: **Noted**, **Contacted customer**,
  **Work assigned**, or **Not actionable** (with the person's reason). The
  Updates page's button for the third reads **Assign work**; the recorded
  response, and the connector's `response.kind` `work_assigned`, is Work assigned.
- **Candidate properties** — on an *Appointment with no follow-up recorded*
  update, the properties the appointment may belong to:
  `candidate_properties: [{property_id, name, in_your_view}]`. Show each by
  name with its id beside it; a property outside the person's view comes back
  with no name — say that rather than showing its id alone.
- **Seen** — a viewing mark. Never a response.

## Tools

Reads (never mark Seen, never record):

- `capsa_describe_updates` — the catalog of update types with their qualification
  rules, and the playbooks that reach the connected person, each with its guidance.
- `capsa_list_updates` — the recent feed (`recent_window_days` 1–60, default 7) with
  Seen marks and next-step context.
- `capsa_list_update_work` — durable next steps (`work_status` `open` or `all`) that
  stay until resolved regardless of feed age, with accountable person, guidance,
  recorded response and acknowledgment.

Settings (company settings access; preparing and saving need **Manage updates**):

- `capsa_explain_update_settings` — company rules, playbooks, choices, the current
  person's view, and the revision.
- `capsa_prepare_update_settings_change` — preview one targeted change (company rule,
  playbook, next-step line with guidance, starting date, or personal view) against
  the current revision; writes nothing.
- `capsa_save_update_settings_change` — save exactly the reviewed proposal after the
  user confirms it.

Responses (**Record update responses** permission; a Work assigned that creates
its task or issue also needs **Create Aspire issues and tasks**):

- `capsa_record_update_response` — record one response on one next step after the
  user confirms the exact response; for Work assigned it can create the task or
  issue in the same call.
- `capsa_acknowledge_update_response` — the accountable person acknowledges a
  teammate's recorded completion.

## Filters and paging

| Input | Where | Values |
| --- | --- | --- |
| `scope` | list tools | `mine` (the person's playbooks' viewpoint, default) or `all` (the full allowed property book) |
| `families` | list tools | update type IDs from `capsa_describe_updates` |
| `playbook_id` | list tools | a reachable playbook ID from `capsa_describe_updates` |
| `property_ids` | all reads | property IDs from `capsa_search_properties`; blank means the full allowed scope |
| `status` | `capsa_list_updates` | `not_seen_by_me` (default), `not_seen_by_anyone`, `seen_by_me`, `all` |
| `recent_window_days` | `capsa_list_updates` | 1–60; never expires outstanding work |
| `work_status` | `capsa_list_update_work` | `open` (default) or `all` |
| `cursor` / `limit` | list tools | continue with `pagination.next_cursor` until `has_more` is false; `limit` 1–100 |

## Recording a response

Every call to `capsa_record_update_response` names the next step (`property_id`,
`item_key`, `fingerprint`, `playbook_id` from the read) and carries
`confirmation: {confirmed_by_user: true, summary}` — the user's explicit yes to
the exact response you show them. One `response`:

| Kind | Fields | Use it when |
| --- | --- | --- |
| `noted` | `note` (optional unless the line asks for an outcome), `append_to_aspire_property_note` (optional; needs *Add notes to Aspire*) | The person handled it, or learned something, and a line or two is the record. The default. |
| `contacted_customer` | `channel` (`email`, `call`, `text`, `in_person`), `contacted_on` (YYYY-MM-DD, not in the future), `summary` (optional) | The customer was actually reached — after a send through a connected email provider, or the user says a call happened. |
| `work_assigned` | Either `action_item_id` (the task or issue the Updates page already created for this next step) or `work` — `item_type` (`task` or `issue`), `subject` (up to 200 characters), `assigned_to_contact_id` (a current Aspire employee, required), `notes` (up to 4,000 characters, or null), `due_date` (YYYY-MM-DD, or null), `priority` (Low, Normal, High or Urgent; Normal when omitted), `notify_assignee` (true when omitted: the assignee is told the way Assign work tells them) — which makes the connector create that task or issue in Aspire and record the response in one confirmed call; the result carries `recorded.action_item_id`, `recorded.item_type` and `recorded.work_item_created` | Someone else must do something, or it belongs on a later date. The confirmation `summary` names the item the person agreed to: task or issue, subject, due date, assignee. Creating it needs **Record update responses** and **Create Aspire issues and tasks** together; with the second off the connector refuses with `permission_denied` and names both controls in Users & Permissions. |
| `not_actionable` | `reason` (required, ≤ 300) | Nothing is needed. The reason comes from the person; the connector refuses without one. Prefer the pack: Customer already knows · Crew already handling it · Not customer-facing · Too dated · Already resolved in Aspire · Part of a bulk schedule change · Duplicate — or their own words. |

A line that asks for an outcome ("Respond with an outcome") refuses an empty
Noted. A Create-tasks line takes no response at all; it closes when its Aspire
tasks are completed. A next step that already has a response returns `conflict`;
read again before trying anything else.

## When the connector refuses

A refused call names one code. Nothing is recorded unless the table says
otherwise; never look for another tool to get around a refusal.

| Code | What happened | What to do next |
| --- | --- | --- |
| `permission_denied` | A grant is off, or the person lacks access to the property; the message names the control. | Stop and tell the person which control in Users & Permissions to turn on (both **Record update responses** and **Create Aspire issues and tasks** for a Work assigned that creates its item), or that the property is outside their access. Hand that step back to the Updates page. |
| `not_found` | The update or next step is not reachable. | Read the loops again; if it is still missing, it is not this connection's to answer — say so. |
| `conflict` | The next step changed, already has a response, or takes another kind of response; or another request is creating work for it; or it already has a task or issue from someone else. | Read the next step again before doing anything else, show the person what stands, and propose afresh; never resend the same call. When a Work assigned created its item but a teammate's response settled the step first, the refusal carries `work_item` with the created `action_item_id`: the item stays linked to the step; once the standing response is undone (only its author can), record Work assigned with that id. |
| `invalid_request` | The input is malformed, a reason or confirmation is missing, the assignee is not a current Aspire employee, or Aspire refused the item (the message says why). | Fix the call: a Not actionable carries the person's reason, every record carries their confirmation, a Work assigned names a current employee. Nothing was recorded or created. |
| `unavailable` | Nothing was recorded, and no item was created. | Tell the person it is not recorded yet and retry the same response a little later. |
| `outcome_unknown` | The connector could not confirm whether the app recorded it; for a Work assigned that creates its item, the task or issue may exist in Aspire. | Read the next step again before retrying: if the response now shows, report it as recorded. For a Work assigned that creates its item, have the person check the property's tasks and issues first and record the existing one by `action_item_id`; a blind retry can create a duplicate in Aspire. Otherwise send the same response again. |

## Boundaries

- Reading, drafting and proposing are never responses. Nothing is recorded
  without the user's confirmation of the exact response.
- A note is proof only when the person actually did the thing it describes.
- The connector never sends email or messages; Contacted customer is recorded after
  the send happened elsewhere, or on the user's word.
- Guidance is advice, not a template: combine it with property context and the
  update's facts, and say which parts you used.
- Properties are shown by name, with the id beside it when that helps; never the
  id alone. A candidate property outside the person's view has no name to show —
  say it is outside their view.
- Health open loops are a separate workspace today; their responses join this
  vocabulary later.

## Freshness

Settings, Seen and recorded responses reflect Capsa as of the read. The Aspire
facts behind an update can be up to 24 hours old; delayed update types are
listed explicitly and are never a silent zero.

## Related

- Skill: [work-the-updates-loop](../../skills/work-the-updates-loop/)
- Example playbook guidance: [reference/playbooks](../playbooks/README.md)
- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
