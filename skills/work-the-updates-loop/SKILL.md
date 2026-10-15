---
description: Work through a person's open Capsa updates and next steps — read each loop's guidance and property context, propose one response per loop (a note, a customer contact, work to assign, or not actionable with a reason), get the user's confirmation, then record it through the Capsa connector. Use when someone wants to clear their Updates queue with help.
---

# Work the updates loop

Clear a person's open next steps: for each loop, read the admin's guidance and the
update's facts, propose the response, let the user confirm or change it, and
record exactly what they confirmed. Nothing is recorded on intent.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Capsa notices what changed at a person's properties and routes it through update
playbooks, each with guidance an admin wrote for that kind of update. The person
still has to decide and record what they did. This skill does the reading and
proposing; the person does the deciding; the connector does the recording.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section lists the inputs a run
needs; persist them in the Team specifics block below, a system message, or a
wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa connector is connected and `capsa_list_update_work` returns open work
  (or `capsa_list_updates` returns unseen updates) for the person.
- The person wants to work through several loops in one sitting, not act on one.
- The connection has **Record update responses** when recording is expected;
  without it, run the read-and-propose steps and hand the recording back to the
  Updates page.

Skip it for a single update the person has already decided about; record that one
directly.

## Required connected apps

- **Capsa connector.** The loops, their guidance, property context, and the response
  recording.
- **An email provider connector (optional).** Only when a proposed response is a
  customer message the person wants sent; send happens there, after approval, and
  Contacted customer is recorded afterwards.

## Configuration

- **Scope.** `mine` (default) or `all`, plus optional `property_ids`, `families`
  or one `playbook_id` from `capsa_describe_updates`.
- **Which loops.** Open work first (`capsa_list_update_work`, `work_status: open`);
  add the recent feed (`capsa_list_updates`, a window of 7–14 days) when the person
  also wants awareness-only updates.
- **Batch size.** How many loops to propose before pausing for review (5–10 keeps
  the review honest).
- **House rules (optional).** Anything the team wants said in every customer
  message, and which Not actionable reasons they prefer.

## Workflow

### 1. Orient (only if needed)

Call `capsa_describe_updates` once: it returns the update types, the playbooks
that reach this person, and each playbook's guidance per type. Keep it for the
session.

### 2. Pull the open loops

Call `capsa_list_update_work` with `work_status: open`. Each item carries the
update's facts (title, dates, service, the issue or appointment block when there
is one), its next steps (one per playbook) with `guidance`, the accountable
person, the deadline, and whether a response already exists. Page with
`next_cursor` until `has_more` is false or the batch size is reached.

### 3. Propose one response per loop

For each loop, read the guidance and the update's facts. Pull
`capsa_get_property_context` only when the guidance or the facts call for it (a
lost contract, a complaint, a past-due start). Then propose exactly one of:

- **Noted** — one or two lines of what to record, when the person handled it or
  the guidance says a note is enough.
- **Contacted customer** — a short draft message or call script, when the guidance
  says the customer should hear from us. Say which channel you suggest.
- **Assign work** — when someone else must do something or it belongs on a later
  date. Say who and what; the item itself is created from the row's **Assign work**
  in Capsa (task or issue), then recorded.
- **Not actionable** — with a reason from the pack (Customer already knows · Crew
  already handling it · Not customer-facing · Too dated · Already resolved in Aspire
  · Part of a bulk schedule change · Duplicate), for example when one route move
  produced many identical reschedules.

Quote the guidance line you relied on. Never invent a fact the tools did not
return; when the facts are not enough to choose, ask.

### 4. Review

Show the batch as a numbered list: property, update, proposed response, the
guidance it follows. The person confirms, edits, skips, or changes the kind. Do
not record anything yet.

### 5. Send first, when a message was approved

For a confirmed customer message with an email provider connected, send it there
after the person approves the final text. Capture the send result. A failed send
is not a contact.

### 6. Record exactly what was confirmed

For each confirmed loop call `capsa_record_update_response` with the loop's
`property_id`, `item_key`, `fingerprint`, `playbook_id`, the confirmed `response`,
and `confirmation: {confirmed_by_user: true, summary: "<what the person approved>"}`.
Record Contacted customer only after the send happened or the person says the
call or visit happened, with the real `contacted_on` day. Record Work assigned
only with the `action_item_id` of the task or issue created from the row. Offer
`append_to_aspire_property_note` on a Noted only when the person asks for it and
the connection has Add notes to Aspire.

### 7. Acknowledge when asked

When the person is the accountable one and a teammate's completion is awaiting
acknowledgment, show it and call `capsa_acknowledge_update_response` only when
they say so.

### 8. Close the session

Summarize what was recorded, what was skipped, and anything that needs the Updates
page (assigning work, a response the connector refused). If the connector could
not do something the person needed, offer `capsa_log_feature_request`.

## Stop rules

- **No confirmation, no record.** Every `capsa_record_update_response` follows an
  explicit yes to that exact response.
- **A draft is not a contact.** Contacted customer needs a real send or the
  person's word that it happened.
- **Noted is a record of something done.** Never propose Noted to make a loop go
  away.
- **Not actionable needs a reason.** Prefer the pack; free text when none fits.
- **Work assigned needs the item.** No `action_item_id` from the row, no record.
- **Conflict means re-read.** A refused record (changed update, already recorded,
  outcome required, tasks line) is shown to the person; read the loop again before
  anything else.
- **Guidance is advice.** Follow it, cite it, and say when the facts argue against
  it; the person decides.

## Example user prompt

> "Help me clear my updates. Show me what each one needs, suggest what you'd
> record, and let me say yes or no before you write anything."

## Example agent output (fictional)

```
You have 4 open next steps. Proposals, with the guidance they follow:

1. Hillcrest Townhomes — Contract service visit rescheduled (fall fertilizer,
   Oct 13 → Oct 17). Guidance: "Tell the customer when a visit moves 3+ days;
   skip when the whole route moved." 11 properties on this route moved the same
   day. Proposed: Not actionable — Part of a bulk schedule change.

2. Birch Office Park — Contract marked lost ($18,400). Guidance: "Call the
   contact within 2 business days and learn why." Proposed: Contacted customer
   by call. Script: ask what drove the decision, whether price or service, and
   whether a revised scope would help. Record after the call.

3. Maple Ridge HOA — Appointment with no follow-up recorded (site walk Oct 9
   with the board president). Guidance: "Record what was agreed and create tasks
   for commitments." Proposed: Noted — "Walked the north entrance with the
   board; agreed to quote drainage by Oct 24." Then Assign work from the row for
   the quote.

4. Cedar Lane — Work order start date passed, no hours (patio install).
   Guidance: "Confirm the new start with ops, then tell the customer." Proposed:
   ask ops first; nothing to record yet.

Confirm, edit, or skip each one. I will record only what you approve.
```

All names, figures and dates above are fictional.

## Team specifics

<!--
  Persist your scope (playbook, families, property set), batch size, preferred
  Not actionable reasons, and house rules for customer messages here. Keep the
  steps and stop rules in sync with the cookbook; re-pull after a connector upgrade.
-->
