# Proposal follow-up email batch

Help an agent work through a batch of outstanding proposal follow-ups by
drafting emails from Capsa context, getting user review, sending through a
connected email provider, and recording completion only after the email
actually went out.

## Purpose

After a proposal goes out, follow-ups slip. This recipe lets an agent take a
pile of outstanding follow-ups and walk the user through them in one short
session: one draft per follow-up, one review pass, one approved send, and a
clean completion record.

The recipe is intentionally framework-agnostic. Use it ad-hoc, fold it into
a Claude Code skill, embed it in another agent framework, or wrap it in a
small script that calls the MCP — the workflow and safety rules are the
same. The "Configuration" section below lists the inputs that go into a
run; how you persist them is up to you.

## When to use this recipe

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and reports outstanding follow-up
  actions.
- The user wants to clear several follow-ups in a single pass, not write one
  bespoke email.
- An email provider connector is connected — Gmail, Outlook, or any other
  email connector available to the agent — and the user intends to send
  from it.

Skip it when the user wants to write a single, high-touch reply, or when no
email provider is connected — ask the user to connect one first.

## Required connected apps

- **Capsa MCP connector.** Provides the follow-up list, the context behind
  each one, and the call to record completion.
- **An email provider connector.** Sends the approved drafts. Gmail and
  Outlook are common examples; any email connector the agent has access to
  works. The agent should send only through a connected provider — not via
  raw SMTP or any unconnected channel.

## Configuration (gather once, persist however suits the user)

These are the inputs a run needs. They're the same no matter how you
store them — and unlike a sensitivity recipe, most of these vary
session-to-session, so leaving them runtime-only is a perfectly good
choice.

- **Filter scope.** Call `capsa_list_followup_filter_options` to see the
  branches and sales reps available to the connection. The user picks
  whichever subset narrows the follow-ups to what they want to clear
  this session.
- **Lookback / lookahead window.** `lookback_weeks` (1–52) and
  `lookahead_weeks` (0–52). Pick whatever cadence the user runs this
  on.
- **Statuses.** Any subset of `past_due`, `overdue`, `upcoming`,
  `complete`. Most clearance passes use `past_due` and `overdue`.
- **Max rows.** A sensible cap so the user-review step stays
  manageable.
- **Standard intro / signature (optional).** A baseline opener or
  closer the team wants reused across drafts — the agent fills in the
  specifics from Capsa context.

Where these inputs live is the user's call. Common options, none
required:

- A reusable Claude Code skill at `.claude/skills/<name>/SKILL.md`
  (shared via git) or `~/.claude/skills/<name>/SKILL.md` (private to
  one user).
- A system message or prompt template in another agent framework.
- A small wrapper script that calls the MCP with the inputs preset.

Persisting tends to fit a team-policy case (e.g. "always show this
sales rep's past-due follow-ups, lookback six weeks"); leave them
runtime-only if the user wants to vary scope each session.

## Workflow

### 1. Learn the connector (only if needed)

If the agent has not used the Capsa connector recently, call
`capsa_describe_service` once to discover the available tools and their
shape. Skip this on subsequent runs in the same session.

### 2. Pull outstanding follow-ups

Call `capsa_find_followup_actions`. Expect a list of follow-up items, each
with:

- a short description of what's outstanding,
- one or more customer contact candidates,
- any context the agent needs to draft a useful email (e.g., proposal
  reference, date sent, prior touchpoints).

### 3. Show the user a concise review list

Before drafting anything, summarize what was returned. One line per
follow-up. The user decides which to act on and which to skip. Do not draft
or send anything yet.

### 4. Draft editable emails

For each follow-up the user wants to act on, draft a short email using only
Capsa's context. Keep drafts:

- short — three to five sentences,
- specific to what the follow-up is about,
- addressed to the contact candidate the user selected,
- free of invented facts (dates, numbers, names not present in the
  context).

If multiple contact candidates exist and the user hasn't chosen, ask.

### 5. Ask the user to review and approve

Present the drafts together with the recipient(s) and subject line. The user
should be able to:

- approve a draft as-is,
- edit a draft, then approve,
- skip a draft (and optionally mark the follow-up as not needed),
- defer a draft to handle later.

Do not move to sending until the user approves a specific draft.

### 6. Send through the connected email provider

Send each approved draft through the agent's connected email provider.
Capture the send result — message ID, sent timestamp, or an error.

If a send fails, surface the error to the user and do not proceed to mark
that follow-up done.

### 7. Mark complete only after evidence

For each follow-up where the agent has send evidence (or explicit user
confirmation that the follow-up was handled out-of-band), call
`capsa_mark_followups_done` with that follow-up's identifier.

Do not mark a follow-up done because a draft was created, edited, or
approved — only because it was actually sent (or the user explicitly
confirmed it's handled).

## Stop rules

The agent must stop and ask rather than push through when any of these come
up:

- **No user approval.** Never send without explicit user approval on the
  specific draft.
- **Draft is not completion.** Never call `capsa_mark_followups_done`
  because a draft exists. The trigger is send evidence or user
  confirmation.
- **No invented contact info.** If the contact email is missing, the
  follow-up has no usable recipient, or contact confidence is low, ask the
  user — do not guess.
- **No invented context.** If a fact would make the draft stronger but
  isn't in the Capsa context, omit it or ask the user. Do not invent.
- **Send error.** If the email provider returns an error, do not mark that
  follow-up done.

## Example user prompt

> "I have a bunch of proposals sitting out there with no follow-up. Can you
> work through them with me? I want to look at each one before anything
> goes out."

## Example agent output format

The fictional example below shows the shape of the agent's review step
before any draft is sent.

```
I found 3 outstanding proposal follow-ups via Capsa:

1. Greenleaf Landscaping — proposal sent 12 days ago, no reply.
   Contact: Jamie Doe <jamie@example.com>

2. Cedar Creek Lawn Care — proposal sent 6 days ago, last touch was a
   question about pricing tiers.
   Contact: Pat Roe <pat@example.com>

3. Stoneridge Grounds — proposal sent 9 days ago, contact asked for a
   follow-up "next week."
   Contact candidates: Sam Lee <sam@example.com>, Alex Park <alex@example.com>

Which would you like me to draft? For Stoneridge, which contact should I
use?
```

After the user replies, the agent drafts the chosen emails and presents
them for approval before sending. After each approved send, the agent
records completion via `capsa_mark_followups_done`.

All names, emails, and timing in the example are fictional.
