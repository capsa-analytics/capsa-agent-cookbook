---
description: Surface upcoming Capsa visits a team flags as sensitive (e.g. chemical application) by division and service type, draft per-visit customer pre-notices for user review, and send via a connected email provider. Use for recurring sensitive-visit notice runs.
---

# Sensitive scheduled-visit notice

Surface upcoming Capsa visits a team flags as sensitive (e.g. chemical application,
pest treatments) and draft per-visit customer pre-notices the user reviews and
sends through a connected email provider.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Teams usually define "sensitive" visits by **division name** and **service type
name** in Capsa — divisions like "Chemical Treatments" or "Pest Control," service
types like "Herbicide Application" or "Fungicide Application." This skill uses
Capsa's upcoming-visits capability to find those scheduled visits with property and
contact context, then walks the user through drafting and sending pre-notices.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section is the contract;
persist those inputs in the Team specifics block below, a system message, or a
wrapper script.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the upcoming-visits capability is
  available on this connection.
- The team has a recurring class of upcoming visits that needs both internal
  awareness and customer pre-notice.
- An email provider connector is connected and the user intends to send notices
  from it.

Skip it for one-off questions about upcoming visits, or when no email provider is
connected — ask the user to connect one first.

## Required connected apps

- **Capsa MCP connector.** Provides the visit list with property, service,
  account-owner, and customer contact context.
- **An email provider connector.** Sends the approved notices (Gmail, Outlook, or
  any other the agent has access to).

## Configuration

- **Filter scope.** Call `capsa_list_upcoming_visit_filter_options` to see the
  branches, divisions, account owners, service types, and services available.
  Identify with the user which **division IDs** and **service type IDs** count as
  sensitive — matching is by name, and the user is the source of truth.
- **Lookahead window.** A common default is 5–7 days; the user picks.
- **Max rows.** A cap so the review step stays manageable.
- **Customer notice body template.** The user's standard wording — what to expect
  during the visit, any reentry interval, contact info, any regulatory disclaimer
  required in their jurisdiction. Do **not** invent regulatory language;
  requirements for chemical and pesticide work vary by jurisdiction.
- **Internal flag destination (optional).** Where the heads-up list goes — chat,
  Slack, a working doc, a calendar event. Skip if a chat summary is enough.

## Workflow

### 1. Learn the capability (only if needed)

If you haven't used the upcoming-visits capability recently, call
`capsa_describe_capability` with `upcoming_visits` once to confirm shape and
freshness. Skip on later runs in the same session.

### 2. Pull upcoming sensitive visits

Call `capsa_find_upcoming_visits` with the configured `division_ids`,
`service_type_ids`, and `lookahead_days`. Expect visits each with date/time window,
property and work-ticket context, service and route context, primary and fallback
customer contact candidates, and freshness notes.

If Capsa flags that data may be up to 24 hours old, **surface that warning** when
the visit is same-day or imminent.

### 3. Show the internal flag list

Summarize what came back — one line per visit. The user decides which to act on,
which to skip, and (where more than one is offered) which contact candidate to use.

If the user configured an internal flag destination outside chat, prepare that
summary but **do not post it** until the user approves it like any other outbound.

### 4. Draft customer notices

For each visit the user wants to act on, draft a short notice using only the Capsa
context and the user's configured body template. Keep drafts short (three to five
sentences), specific to the visit date and service type, addressed to the chosen
contact, and free of invented facts (no addresses, names, dates, or regulatory text
not in the context or template).

### 5. Review and approve

Present each draft with recipient, subject, and visit reference. The user can
approve, edit-and-approve, skip, or defer per visit. Don't send until the user
approves the specific draft.

### 6. Send through the connected email provider

Send each approved notice through the connected provider. Capture the result —
message ID, sent timestamp, or an error. If a send fails, surface it and move on to
the next visit.

### 7. Do not record completion in Capsa

The upcoming-visits capability has no completion-write tool. Do not invent one. The
run ends after the user-approved sends. If the user wants an external "notice sent"
record (a doc, a Slack thread, a calendar event), produce it from the captured send
results — never from intent, drafts, or approvals alone.

## Stop rules

- **No user approval.** Never send a notice without explicit per-visit approval.
- **Invented regulatory text.** Never add a reentry interval, hazard line, or
  disclaimer that isn't in the user's template. If asked for one not provided, ask.
- **No usable contact.** If a visit has no primary or fallback contact, surface
  that and skip unless the user supplies a recipient.
- **No invented context.** A fact not in the Capsa context or template gets omitted
  or asked about.
- **Stale-data risk for same-day decisions.** If Capsa flags data up to 24 hours
  old and the visit is same-day, surface the warning and let the user decide.
- **No fabricated completion record.** Upcoming visits has no mark-done tool; don't
  pretend otherwise.

## Example user prompt

> "We just brought you online for our chemical-application visits. Can you find the
> ones coming up in the next week and walk me through drafting a heads-up email to
> each property contact?"

## Example agent output (fictional)

After running `capsa_find_upcoming_visits` with the configured filters:

```
I found 4 upcoming sensitive visits in the next 7 days (Capsa data may be up to
24 hours old):

1. Mon 2026-05-25, morning window — Greenleaf Landscaping
   Service: Herbicide Application
   Contact: Jamie Doe <jamie@example.com>

2. Tue 2026-05-26, afternoon window — Cedar Creek Lawn Care
   Service: Fungicide Application
   Contact: Pat Roe <pat@example.com>

3. Wed 2026-05-27, morning window — Stoneridge Grounds
   Service: Herbicide Application
   Contact candidates: Sam Lee <sam@example.com>, Alex Park <alex@example.com>

4. Thu 2026-05-28, afternoon window — Maple Ridge HOA
   Service: Pesticide Application
   Contact: Riley Tran <riley@example.com>

Which should I draft notices for? For Stoneridge, which contact should I use?
```

After the user replies, the agent drafts the chosen notices using the configured
template, presents them for approval, and sends only after explicit per-visit
approval.

All names, emails, and dates above are fictional.

## Team specifics

<!--
  Persist your sensitive division IDs / service type IDs, lookahead window, and
  notice body template here. Keep the steps and stop rules in sync with the
  cookbook; re-pull after a connector upgrade.
-->
