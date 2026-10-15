# Updates (`updates`)

Read the company's update catalog, the playbooks that reach the connected
person (with the guidance an admin wrote for each one), the recent feed, and
the durable next steps with accountable people and recorded responses. Where
the connection allows it, explain and change update settings after review, and
record a response or acknowledge completion after the user confirms.

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
  with every next step as `guidance`. Read it before proposing anything.
- **Next step** (a loop) — one update × one playbook, with an accountable person, a
  deadline on the organization's business-day calendar, and a response history.
- **Response** — what a person recorded: **Noted**, **Contacted customer**,
  **Work assigned**, or **Not actionable** (with a reason).
- **Seen** — a viewing mark. Never a response.

## Tools

Reads (never mark Seen, never record):

- `capsa_describe_updates` — the catalog of update types with their qualification
  rules, and the playbooks that reach the connected person, each with its guidance.
- `capsa_list_updates` — the recent feed (`recent_window_days` 1–60, default 7) with
  Seen state and next-step context.
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

Responses (**Record update responses** permission):

- `capsa_record_update_response` — record one response on one next step after the
  user confirms the exact response.
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
| `work_assigned` | `action_item_id` | A Capsa task or issue was created for this next step from the Updates page. The connector cannot create that item yet; send the user to the row's **Assign work**. |
| `not_actionable` | `reason` (optional, ≤ 300) | Nothing is needed. Prefer a reason from the pack: Customer already knows · Crew already handling it · Not customer-facing · Too dated · Already resolved in Aspire · Part of a bulk schedule change · Duplicate. |

A line that asks for an outcome ("Respond with an outcome") refuses an empty
Noted. A Create-tasks line takes no response at all; it closes when its Aspire
tasks are completed. A next step that already has a response returns a conflict;
read again before trying anything else.

## Boundaries

- Reading, drafting and proposing are never responses. Nothing is recorded
  without the user's confirmation of the exact response.
- A note is proof only when the person actually did the thing it describes.
- The connector never sends email or messages; Contacted customer is recorded after
  the send happened elsewhere, or on the user's word.
- Guidance is advice, not a template: combine it with property context and the
  update's facts, and say which parts you used.
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
