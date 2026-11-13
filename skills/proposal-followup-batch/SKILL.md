---
description: Work through a batch of outstanding Capsa proposal follow-ups — pull them, draft an email per contact from Capsa context, get user review, send via a connected email provider, and mark done only after the send. Use when clearing several follow-ups in one pass.
---

# Proposal follow-up email batch

Work through a batch of outstanding proposal follow-ups: draft emails from Capsa
context, get user review, send through a connected email provider, and record
completion only after the email actually went out.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

After a proposal goes out, follow-ups slip. This skill takes a pile of outstanding
follow-ups and walks the user through them in one short session: one draft per
follow-up, one review pass, one approved send, and a clean completion record.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section lists the inputs a run
needs; persist them in the Team specifics block below, a system message, or a
wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and reports outstanding follow-up actions.
- The user wants to clear several follow-ups in a single pass, not write one
  bespoke email.
- An email provider connector is connected (Gmail, Outlook, or any other) and the
  user intends to send from it.

Skip it when the user wants a single high-touch reply, or when no email provider is
connected — ask the user to connect one first.

## Required connected apps

- **Capsa MCP connector.** Provides the follow-up list, the context behind each
  one, and the call to record completion.
- **An email provider connector.** Sends the approved drafts. Send only through a
  connected provider — never via raw SMTP or an unconnected channel.

## Configuration

The inputs a run needs. Most vary session-to-session, so leaving them runtime-only
is fine.

- **Filter scope.** Call `capsa_list_followup_filter_options` to see the branches
  and sales reps available to the connection; the user picks the subset to clear.
- **Lookback / lookahead window.** `lookback_weeks` (1–52) and `lookahead_weeks`
  (0–52).
- **Statuses.** Any subset of `past_due`, `overdue`, `upcoming`, `complete`. Most
  clearance passes use `past_due` and `overdue`.
- **Max rows.** A cap so the review step stays manageable.
- **Standard intro / signature (optional).** A baseline opener or closer to reuse;
  the agent fills specifics from Capsa context.

## Workflow

### 1. Orient (only if needed)

If you haven't used Capsa recently this session, call `capsa_describe_service` once
to confirm available tools and their shape.

### 2. Pull outstanding follow-ups

Call `capsa_find_followup_actions`. Expect items each with a short description, one
or more customer contact candidates, and drafting context (proposal reference, date
sent, prior touchpoints).

### 3. Show a concise review list

Summarize what came back — one line per follow-up. The user decides which to act on
and which to skip. Don't draft or send yet.

### 4. Draft editable emails

For each follow-up the user picks, draft a short email using only Capsa's context:
three to five sentences, specific to the follow-up, addressed to the selected
contact, free of invented facts. If multiple contacts exist and the user hasn't
chosen, ask.

### 5. Review and approve

Present each draft with recipient(s) and subject. The user can approve as-is, edit
then approve, skip (optionally mark not needed), or defer. Don't send until the user
approves the specific draft.

### 6. Send through the connected email provider

Send each approved draft through the connected provider. Capture the result —
message ID, sent timestamp, or an error. If a send fails, surface the error and do
not mark that follow-up done.

### 7. Mark complete only after evidence — review, then save

For each follow-up with send evidence (or explicit user confirmation it was handled
out-of-band), have Capsa review the completion first. Call
`capsa_prepare_followups_done` with the user's request, `follow_up_actions` (each
item is `opportunity_id` plus `follow_up_key`, or `action_id` for automation
follow-ups) and `completion_evidence` (`type: email_sent` with `provider`,
`message_id`, `recipient_email` and `sent_at`, or `type: user_confirmed` with the
user's own `confirmation` text). This records nothing. It returns a
`proposal_token`, `expires_at` and a `review` of exactly which follow-ups will be
marked done and on what evidence.

Show the user that review. Only after they confirm it, call
`capsa_mark_followups_done` with exactly
`{"proposal_token": "<from the review>", "confirmed": true}`. If the selection or
evidence changes, prepare again. A token expires after 20 minutes and works once;
sending the same save again returns the first result. Do not hold a token across a
long pause — prepare again.

Capsa records `email_sent` details as you give them. It does not read the mailbox
or check that the message was sent, so give only the real provider result from
step 6. Never mark done because a draft was created, edited, or approved.

## Stop rules

- **No user approval.** Never send without explicit approval on the specific draft.
- **Draft is not completion.** Never call `capsa_prepare_followups_done` or
  `capsa_mark_followups_done` because a draft exists — the trigger is send evidence or user confirmation.
- **No invented contact info.** Missing email, no usable recipient, or low contact
  confidence → ask, don't guess.
- **No invented context.** A fact not in the Capsa context gets omitted or asked
  about, never invented.
- **Send error.** If the provider errors, don't mark that follow-up done.

## Example user prompt

> "I have a bunch of proposals sitting out there with no follow-up. Can you work
> through them with me? I want to look at each one before anything goes out."

## Example agent output (fictional)

```
I found 3 outstanding proposal follow-ups via Capsa:

1. Greenleaf Landscaping — proposal sent 12 days ago, no reply.
   Contact: Jamie Doe <jamie@example.com>

2. Cedar Creek Lawn Care — proposal sent 6 days ago, last touch was a question
   about pricing tiers.
   Contact: Pat Roe <pat@example.com>

3. Stoneridge Grounds — proposal sent 9 days ago, contact asked for a follow-up
   "next week."
   Contact candidates: Sam Lee <sam@example.com>, Alex Park <alex@example.com>

Which would you like me to draft? For Stoneridge, which contact should I use?
```

After the user replies, the agent drafts the chosen emails, presents them for
approval, sends only after approval, and — only after each send — reviews the
completion with `capsa_prepare_followups_done` and records it with
`capsa_mark_followups_done` once the user confirms the review.

All names, emails, and timing above are fictional.

## Team specifics

<!--
  Persist your filter scope (branches, sales reps, statuses, lookback/lookahead
  window) and a standard intro/signature here. Keep the steps and stop rules in
  sync with the cookbook; re-pull after a connector upgrade.
-->
