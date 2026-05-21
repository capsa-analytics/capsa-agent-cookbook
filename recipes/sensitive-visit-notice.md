# Sensitive scheduled-visit notice

Help an agent surface upcoming Capsa visits that a team flags as sensitive
(e.g. chemical application, pest treatments) and draft per-visit customer
pre-notices the user reviews and sends through a connected email provider.

## Purpose

Teams usually define "sensitive" visits by **division name** and **service
type name** in Capsa — for example, divisions like "Chemical Treatments" or
"Pest Control," service types like "Herbicide Application" or "Fungicide
Application." This recipe uses Capsa's upcoming-visits capability to find
those scheduled visits with property and contact context, then walks the
user through drafting and sending pre-notices.

The recipe is intentionally framework-agnostic. Use it ad-hoc, fold it into
a Claude Code skill, embed it in another agent framework, or wrap it in a
small script that calls the MCP — the workflow and safety rules are the
same. The "Configuration" section below is the contract; how you persist
those inputs is up to you.

## When to use this recipe

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the upcoming-visits capability
  is available on this connection.
- The team has a recurring class of upcoming visits that needs both
  internal awareness and customer pre-notice.
- An email provider connector is connected and the user intends to send
  notices from it.

Skip it for one-off ad-hoc questions about upcoming visits, or when no
email provider is connected — ask the user to connect one first.

## Required connected apps

- **Capsa MCP connector.** Provides the visit list with property, service,
  account-owner, and customer contact context.
- **An email provider connector.** Sends the approved notices. Gmail and
  Outlook are common examples; any email connector the agent has access to
  works.

## Configuration (gather once, persist however suits the user)

Before the first run, gather the inputs below. They're the same no matter
how you store them.

- **Filter scope.** Call `capsa_list_upcoming_visit_filter_options` to see
  the branches, divisions, account owners, service types, and services
  available to the connection. Work with the user to identify which
  **division IDs** and **service type IDs** count as sensitive for their
  team. Matching is by name — the user is the source of truth on what
  counts.
- **Lookahead window.** A common default is 5–7 days; the user picks.
- **Max rows.** A sensible cap so the user-review step stays manageable.
- **Customer notice body template.** The user's standard wording — what to
  expect during the visit, any reentry interval, contact info, any
  regulatory disclaimer required in their jurisdiction. The agent should
  **not** invent regulatory language; pre-notice requirements for
  chemical and pesticide work vary by jurisdiction.
- **Internal flag destination (optional).** Where the heads-up list goes —
  chat output, a Slack message, a working doc, a calendar event. Skip
  this input if a chat summary is enough.

Where these inputs live is the user's call. Common options, none required:

- A reusable Claude Code skill at `.claude/skills/<name>/SKILL.md` (shared
  via git) or `~/.claude/skills/<name>/SKILL.md` (private to one user).
- A system message or prompt template in another agent framework.
- A small wrapper script that calls the MCP with the filters preset.

Treat the inputs above as the contract; pick the persistence that fits.

## Runtime workflow

### 1. Learn the capability (only if needed)

If the agent has not used the upcoming-visits capability recently, call
`capsa_describe_capability` with `upcoming_visits` once to confirm shape
and freshness. Skip on subsequent runs in the same session.

### 2. Pull upcoming sensitive visits

Call `capsa_find_upcoming_visits` with the configured `division_ids`,
`service_type_ids`, and `lookahead_days`. Expect a list of visits, each
with:

- visit date / time window,
- property and work-ticket context,
- service and route context,
- primary and fallback customer contact candidates,
- freshness notes.

If Capsa flags that data may be up to 24 hours old, **surface that
warning to the user** when the visit is same-day or imminent.

### 3. Show the user the internal flag list

Summarize what came back. One line per visit. The user decides which
visits to act on, which to skip, and (if any) which contact candidate to
use when more than one is offered.

If the user configured an internal flag destination outside chat (Slack,
doc, calendar), prepare that summary but **do not post it** until the
user approves it like any other outbound.

### 4. Draft customer notices

For each visit the user wants to act on, draft a short notice using only
the Capsa context and the user's configured body template. Keep drafts:

- short — three to five sentences,
- specific to the visit date and service type,
- addressed to the chosen contact candidate,
- free of invented facts (no addresses, names, dates, or regulatory text
  that isn't in the Capsa context or the configured template).

### 5. Ask the user to review and approve

Present each draft with recipient, subject, and visit reference. The user
should be able to approve, edit-and-approve, skip, or defer per visit.
Do not move to sending until the user approves the specific draft.

### 6. Send through the connected email provider

Send each approved notice through the agent's connected email provider.
Capture the send result — message ID, sent timestamp, or an error. If a
send fails, surface the error and move on to the next visit.

### 7. Do not record completion in Capsa

The upcoming-visits capability does not have a completion-write tool. Do
not invent one. The recipe ends after the user-approved sends.

If the user wants an external "notice sent" record (a shared doc, a
Slack thread, a calendar event), produce it from the captured send
results — never from intent, drafts, or approvals alone.

## Stop rules

The agent must stop and ask rather than push through when any of these
come up:

- **No user approval.** Never send a notice without explicit per-visit
  approval.
- **Invented regulatory text.** Never add a reentry interval, hazard
  line, or disclaimer that isn't in the user's configured template. If
  the user asks for one and didn't provide it, ask.
- **No usable contact.** If the visit has no primary or fallback contact,
  surface that and skip the visit unless the user supplies a recipient.
- **No invented context.** If a fact would make the notice stronger but
  isn't in the Capsa context or the configured template, omit it or ask.
- **Stale-data risk for same-day decisions.** If Capsa flags data as up
  to 24 hours old and the visit is same-day, surface the warning and let
  the user decide.
- **No fabricated completion record.** Capsa has no mark-done tool for
  upcoming visits; do not pretend otherwise.

## Example user prompt

> "We just brought you online for our chemical-application visits. Can
> you find the ones coming up in the next week and walk me through
> drafting a heads-up email to each property contact?"

## Example agent output (fictional)

After running `capsa_find_upcoming_visits` with the configured filters:

```
I found 4 upcoming sensitive visits in the next 7 days (Capsa data may
be up to 24 hours old):

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

Which should I draft notices for? For Stoneridge, which contact should
I use?
```

After the user replies, the agent drafts the chosen notices using the
configured body template, presents them for approval, and sends only
after explicit per-visit approval.

All names, emails, and dates above are fictional.
