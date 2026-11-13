---
description: Work through a person's open Capsa automation alerts — read each alert and its property context, propose one response per alert (a note, a customer contact, work to assign, or not actionable with a reason), get the user's confirmation of Capsa's review, then record it through the Capsa connector. Use when someone wants to clear their open alerts with help.
---

# Work the updates loop

Clear a person's open alerts: for each alert, read its facts and property context, propose the response, let the user confirm or change it, and
record exactly what they confirmed. Nothing is recorded on intent, and every
record is a review first, then a save.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Capsa notices what changed at a person's properties and routes it to the right
person through the company's automation rules. The person
still has to decide and record what they did. This skill does the reading and
proposing; the person does the deciding; the connector does the recording.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section lists the inputs a run
needs; persist them in the Team specifics block below, a system message, or a
wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa connector is connected and `capsa_list_update_work` returns open work
  (or `capsa_list_updates` returns open alerts) for the person.
- The person wants to work through several alerts in one sitting, not act on one.
- The connection has **Record update responses** when recording is expected;
  without it, run the read-and-propose steps and hand the recording back to the
  Capsa app. Creating the task or issue behind a Work assigned through the
  connector also needs **Create Aspire issues and tasks**; without it, the
  person creates the item in Capsa and you record it by its `action_item_id`.

Skip it for a single update the person has already decided about; record that one
directly.

## Required connected apps

- **Capsa connector.** The alerts, property context, and the response
  recording.
- **An email provider connector (optional).** Only when a proposed response is a
  customer message the person wants sent; send happens there, after approval, and
  Contacted customer is recorded afterwards.

## Configuration

- **Scope.** `mine` (default) or `all`, plus optional `property_ids`.
- **Which alerts.** Open response-required alerts (`capsa_list_update_work`,
  default `status=open`) are the ones this loop works. When the person also wants
  informational alerts, read them with `capsa_list_updates` and show them as a
  read-only summary: they accept no response, so never propose, prepare or record
  a response for one.
- **Batch size.** How many alerts to propose before pausing for review (5–10 keeps
  the review honest).
- **House rules (optional).** Anything the team wants said in every customer
  message, and which Not actionable reasons they prefer.

## Workflow

### 1. Orient (only if needed)

Call `capsa_describe_updates` once: it returns the response kinds the connector
supports and what each needs. Keep it for the session.

### 2. Pull the open alerts

Call `capsa_list_update_work` (open response-required alerts for the person). Each
item carries an `alert_id`, the rule and record context, the headline and body,
the assignee, the response deadline, any current response, linked work, and
`can_respond` / `can_undo`. Page with `cursor` until there is no more or the batch
size is reached. Use the `alert_id` from this read for every response; do not
carry ids over from an earlier session.

### 3. Propose one response per alert

For each alert, read its headline, body and facts. Pull
`capsa_get_property_context` only when the facts call for it (a
lost contract, a complaint, a past-due start). Then propose exactly one of:

- **Noted** — one or two lines of what to record, when the person handled it or
  only needs to acknowledge the alert.
- **Contacted customer** — a short draft message or call script, when the facts
  say the customer should hear from us. Say which channel you suggest.
- **Work assigned** — when someone else must do something or it belongs on a
  later date. Propose the item itself: task or issue, subject, notes, due date
  and who it is for. The connector can create it as it records the response, or
  the person creates it in Capsa and you record that item by its
  `action_item_id`.
- **Not actionable** — with the person's own reason (for example the customer
  already knows, the crew is handling it, or one route move produced many identical
  reschedules).

Say which facts from the alert you relied on.
When the facts are not enough to choose, ask.

### 4. Review

Show the batch as a numbered list: property (by name), update, proposed
response, and the facts behind it. The person confirms, edits, skips, or changes
the kind. For a Work assigned, the yes covers the item itself — task or issue,
subject, notes, due date and assignee — because that is exactly what gets
created. Do not record anything yet.

### 5. Send first, when a message was approved

For a confirmed customer message with an email provider connected, send it there
after the person approves the final text. Capture the send result. A failed send
is not a contact.

### 6. Review, then record exactly what was confirmed

For each alert the person confirmed, first call `capsa_prepare_update_response`
with `user_request`, the `alert_id` and the confirmed `response`. It records
nothing. It returns `saved: false`, a `proposal_token`, `expires_at` and a
`review` (the alert, the normalized response and a plain summary). Show the person
that review. If it differs from what they approved, say so and ask again.

Only after they confirm the review, call `capsa_record_update_response` with
exactly `{"proposal_token": "<from the review>", "confirmed": true}`. Do not send a
`confirmation` object or the response again; Capsa records what the review stored.
The token belongs to the person who made it, works for recording only, expires
after 20 minutes and works once. Do not hold tokens across a long pause or reuse
one for a different response: prepare again. Sending the same record again returns
the first result (`replayed: true`) and never records a second response or creates
a second task.

Some AI apps also ask before the review step. That prompt is routine, not the
person's yes to the record: show the review and wait for an explicit yes.

Response shapes (`response.kind` is one of these):

- **Noted** — optional `note`; optional `append_to_aspire_property_note` only when
  the person asks and the connection has Add notes to Aspire.
- **Contacted customer** — `channel` (email, call, text, in_person), the real
  `contacted_on` day, optional short `summary`. Record it only after the send
  happened or the person says the call or visit happened. It never sends a message.
- **Work assigned** — either `action_item_id` of work already linked to the alert,
  or `work` (below).
- **Not actionable** — the person's `reason`; the connector refuses without one.

For a Work assigned with `work`, the review shows the exact item that will be
created:

```json
{
  "alert_id": "<from capsa_list_update_work>",
  "response": {
    "kind": "work_assigned",
    "work": {
      "item_type": "task",
      "subject": "Quote north-entrance drainage",
      "notes": "Walked the north entrance with the board on Oct 9; quote due Oct 24.",
      "assigned_to_contact_id": 4312,
      "due_date": "2026-10-24",
      "priority": "Normal",
      "notify_assignee": true
    }
  }
}
```

`item_type` is `task` or `issue`; `subject` (up to 200 characters) and
`assigned_to_contact_id` (a current Aspire employee; 4312 is Dana Ruiz) are
required; `notes` (up to 4,000 characters) and `due_date` may be null; `priority`
is Low, Normal, High or Urgent (Normal when omitted); `notify_assignee` is true
unless the person asks otherwise. When the company requires work types, check
`capsa_get_work_creation_options` first and use the rendered subject and exact
revision it returns. Creating the item needs **Record update responses** and
**Create Aspire issues and tasks** together; with the second off the connector
refuses with `permission_denied` and names both controls.

A refusal comes back as a code. `conflict` and `outcome_unknown` both mean read
the alert and its linked work again before doing anything else; after an
`outcome_unknown` on a Work assigned that creates its item, have the person check
the property's tasks and issues before any retry, because a blind retry can
duplicate the item in Aspire; `work_created_not_recorded` means keep the created
item's evidence and never resend the create; `unavailable` before a write was sent
means nothing was recorded, try again shortly; `permission_denied` and `not_found`
go back to the person with the control or alert the message names; `invalid_request`
means repair the input and confirm any changed response again. A refusal that
starts with "Reviewed change:" (expired, used, or another person's review) means
prepare again and ask again. The
[Updates reference](https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/reference/capabilities/updates.md#when-the-connector-refuses)
lists each one.

### 7. Undo a response when asked

Only the person who recorded a standing response can undo it, and only when the
alert shows `can_undo`. Call `capsa_prepare_update_response_undo` with
`user_request`, the `alert_id` and the `response_id`; show the review; after the
person confirms it, call `capsa_undo_update_response` with exactly
`{"proposal_token": "<from the review>", "confirmed": true}`. An undo review works
only for undo, expires after 20 minutes and works once. Undo never deletes tasks or
issues the response linked.

### 8. Close the session

Summarize what was recorded, what was skipped, and anything that needs the Capsa
app (a task or issue the connector could not create, a response it refused). If
the connector could not do something the person needed, offer
`capsa_log_feature_request`.

## Stop rules

- **No confirmation, no record.** Every `capsa_record_update_response` and
  `capsa_undo_update_response` follows `capsa_prepare_update_response` /
  `capsa_prepare_update_response_undo` and an explicit yes to the review shown. The
  save carries only the token and `confirmed: true`; never a hand-built
  `confirmation` object.
- **One review, one save.** Do not reuse a token, hold it across a long pause, or
  change the response under an old one. An expired or used token is refused:
  prepare again and ask again.
- **A draft is not a contact.** Contacted customer needs a real send or the
  person's word that it happened.
- **Noted is a record of something done.** Never propose Noted to make an alert go
  away.
- **Not actionable needs the person's reason.** The connector refuses without one.
  Use their own words.
- **Work assigned names the item.** Either the `action_item_id` of the task or
  issue linked to the alert, or the `work` details they confirmed so the connector
  creates it. Neither, no record.
- **A refusal is shown, not retried blindly.** `conflict` (the alert changed,
  already has a response, or takes another kind of response) and
  `outcome_unknown` (the connector could not confirm the record) both mean read
  the alert again before anything else; a Work assigned that creates its item is
  never resent blindly, because a retry can duplicate it in Aspire; `unavailable`
  means nothing was recorded, try again shortly; `permission_denied` names the
  control to turn on.
- **Facts, not guesses.** Never invent a fact the tools did not return; when the
  facts are not enough to choose, ask. The person decides.

## Example user prompt

> "Help me clear my open alerts. Show me what each one needs, suggest what you'd
> record, and let me say yes or no before you write anything."

## Example agent output (fictional)

```
You have 4 open alerts. Proposals, with the facts behind them:

1. Hillcrest Townhomes — service visit rescheduled (fall fertilizer, Oct 13 →
   Oct 17). 11 properties on this route moved the same day. Proposed: Not
   actionable — Part of a bulk schedule change.

2. Birch Office Park — contract marked lost ($18,400). Proposed: Contacted
   customer by call. Script: ask what drove the decision, whether price or
   service, and whether a revised scope would help. Record after the call.

3. Maple Ridge HOA (property 4821) — appointment with no follow-up recorded
   (site walk Oct 9 with the board president). Proposed: Work assigned — task
   "Quote north-entrance drainage" for Dana Ruiz, due Oct 24, with the note
   "Walked the north entrance with the board; agreed to quote drainage by
   Oct 24." I will create the task as I record it, once you confirm.

4. Cedar Lane — work order start date passed, no hours (patio install).
   Proposed: ask ops first; nothing to record yet.

Confirm, edit, or skip each one. I will record only what you approve.
```

All names, figures and dates above are fictional.

## Team specifics

<!--
  Persist your scope (scope, property set), batch size, preferred
  Not actionable reasons, and house rules for customer messages here. Keep the
  steps and stop rules in sync with the cookbook; re-pull after a connector upgrade.
-->
