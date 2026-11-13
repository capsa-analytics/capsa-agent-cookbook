---
description: Turn AI meeting notes (Granola, Fathom, Otter, or a pasted transcript/summary) into a reviewed Capsa Command Center property note. Extract the primary contact and a proposed note, resolve the exact property via the primary contact, require the user to confirm the property and note text, then write it — never to the wrong property. Use after a customer call when you want the recap saved back to Capsa.
---

# Meeting notes to Command Center property note

Take the notes from a customer call — captured in a meeting-notes app or pasted
in — summarize them, resolve which property they belong to via the primary
contact, and, after the user confirms the exact property and the note text, save a
Capsa Command Center property note. The guarantee: a note never lands on the wrong
property.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

After a call, the recap lives in a notes tool and rarely makes it back into the
system of record. This skill closes that loop: it turns a meeting summary into a
Command Center property note without ever guessing the property. A primary contact
can manage several properties, so the skill resolves the full candidate list and
makes the user pick before anything is written.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section lists the inputs a run
needs; persist them in the Team specifics block below, a system message, or a
wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the `command_center_notes` capability
  is available (check `capsa_describe_capability`; note writes can be disabled for
  a connection).
- You have meeting notes to work from — from a connected notes app, or pasted as
  text — that name or imply a customer contact.
- The user wants the recap saved to Capsa and is available to confirm the property
  and note.

Skip it when the capability isn't enabled (ask the user to enable note writes), or
when there's no contact context at all to resolve a property from.

## Required connected apps

- **Capsa MCP connector.** Resolves the property from the primary contact
  (`capsa_find_properties_by_primary_contact`), corroborates it with a property
  search (`capsa_search_properties`), and writes the Command Center note.
- **A meeting-notes source (optional).** A connected notes app (Granola, Fathom,
  Otter, and similar) supplies the transcript or summary. If none is connected, the
  user can paste the notes directly — the workflow is identical from step 2 on.

## Configuration

The inputs a run needs. Most vary session-to-session, so leaving them runtime-only
is fine.

- **Meeting source.** Which meeting to use — the latest call, a named meeting, or
  pasted text.
- **Note style (optional).** A house format for the note body (e.g. lead with next
  steps, keep to a few sentences). The agent fills specifics only from the notes.
- **Aspire append.** Whether to also append to the Aspire property Note
  (`append_to_aspire_property_note`). Off unless the connection allows it and the
  user asks — prefer a Capsa-only write otherwise.

## Workflow

### 1. Orient (only if needed)

If you haven't used Capsa recently this session, call `capsa_describe_capability`
for `command_center_notes` to confirm the write is enabled and check the Aspire
append readiness before promising it.

### 2. Extract from the meeting notes

From the transcript, title, and summary, pull:

- **primary contact email** — if available (the exact-match key);
- **primary contact name** — as a fuzzy fallback or supplement;
- **property hint** — any property/site name mentioned, for ranking only;
- **proposed note body** — a short recap drafted **only** from the notes: what was
  discussed, decisions, and next steps. Invent nothing.

### 3. Resolve the property — then corroborate before trusting it

Call `capsa_find_properties_by_primary_contact` with the email (when present), the
name, and the `property_hint`. Pass ID filters only if the user has already scoped
to a branch/division/owner.

- Use the email for the exact match; use the name as fallback or supplement.
- The `property_hint` **only ranks and annotates** — it never hides other
  properties for the contact. Present the full candidate list.
- **Ask for the full set and watch for truncation.** Set `max_properties` to the
  cap (250) so a many-property contact isn't silently trimmed below the list the
  user must choose from. If the result comes back at the cap (`row_count` equals
  `result_cap`), the candidates may be incomplete — narrow with a branch or
  account-owner filter (or ask the user to) and re-run before presenting anything
  for confirmation. Never confirm a write off a truncated list.

**Don't treat a lone primary-contact hit as ground truth.** The resolver keys on
each property's *primary contact*, so a property that belongs to the same person
but has **no primary contact recorded** won't come back — and it may be the more
relevant one (for example, the property that actually holds the active contract,
while a duplicate record carries the contact). So whenever the match is name-based
(fuzzy) or the resolver returns a single property, **corroborate**: also call
`capsa_search_properties` on the contact name (and any property hint) and reconcile.
If that search surfaces same-named or same-address properties the resolver didn't
return, fold them into the candidate list and treat resolution as ambiguous —
noting which candidates have an active contract.

### 4. Review candidate properties

- **No match** → stop and ask for more context (a different email, a property
  name); don't invent a property.
- **One high-confidence match** — an exact-email hit with no same-named siblings
  from the corroboration search → still show property, customer, branch, and account
  owner for confirmation before writing.
- **A single fuzzy / medium-confidence match, or same-named siblings exist** → do
  **not** auto-select. Present every candidate — resolver hits plus anything the
  corroboration search surfaced — with active-contract status, and have the user
  pick exactly one.
- **Multiple properties or contacts** (`requires_user_selection`) → present the
  full list and have the user pick exactly one. Never hide extras or pick for them.

### 5. Review the note with Capsa

Call `capsa_prepare_command_center_note` with the user's request, the selected
`property_id`, the draft `note`, and — only when the user asked for them —
`append_to_aspire_property_note` and `add_to_future_plans` (both default to off).
This saves nothing. It checks the property and the connection's rights and
returns `saved: false`, a `proposal_token`, `expires_at`, and a `review`: the
property (id, name, customer), the exact note text, and both options.

### 6. Confirm with the user, then save

Show the user the review exactly as returned: the property (id and name), the
note body, and the options. The user confirms the property and approves or edits
the note. This is the approval gate — nothing is saved until they confirm the
review they were shown. If they edit anything (property, text or options), go back
to step 5 for a new review; never edit under an old token.

Only after the user confirms, call `capsa_create_command_center_note` with exactly:

```json
{"proposal_token": "<from the review>", "confirmed": true}
```

Capsa saves what the review stored. Do not send the note, the property or a
`write_confirmation` / `confirmation` object with the token; a request written
that way is refused with a "review first" message.

- The token belongs to the person who made the review, works for this save only,
  expires after 20 minutes and saves once. If the user pauses longer than that,
  prepare again and show the new review; never reuse an old token.
- Sending the same save again returns the first result (`replayed: true`) and
  never saves a second note. If the result is uncertain, read the property's
  notes before preparing again.
- The Capsa note saves first; an Aspire append, when requested and enabled,
  returns as `queued`.

### 7. Record the result

Report back the created note reference and identity, the property id and name, and
the Aspire sync status. Keep a short record — property, reviewer, timestamp, and
the source meeting link — so the write is traceable.

## Stop rules

- **Never write by contact alone.** A confirmed `property_id` is required — resolve
  and confirm the property first.
- **Never hide extra properties for the same contact.** Present the full candidate
  list; the user selects.
- **Corroborate before a single write.** A lone primary-contact hit is not proof the
  property is unique — a same-named property with no primary contact recorded is
  invisible to the resolver. Cross-check with `capsa_search_properties` and require
  selection when siblings surface.
- **Medium confidence → confirm, never auto-select.** Only an exact-email match with
  no same-named siblings may be treated as unambiguous; a fuzzy name match always
  goes to the user.
- **Never confirm off a truncated candidate list.** If the resolver hit its result
  cap (`row_count` equals `result_cap`), narrow with a filter and re-run before
  selection — a hidden property is a wrong-property risk.
- **`property_hint` only ranks.** It must never filter the candidates.
- **Approval before write.** No note is saved until the user confirms the review
  Capsa returned (the exact property and note text).
- **Review, then save, with the token only.** Never build a confirmation object.
  A changed request needs a new review; an expired (20 minutes) or used token is
  refused — prepare again and ask again.
- **A review prompt is not the user's yes.** Some AI apps ask before the review
  step too. Treat that as routine; wait for an explicit yes to the shown review
  before the save.
- **No invented content.** A fact not in the meeting notes gets omitted or asked
  about, never invented.
- **Aspire append is optional.** If the append isn't ready or isn't permitted,
  write the Capsa note only — don't block the save on it.

## Example user prompt

> "I just wrapped a call with Jordan at Maple Ridge — can you summarize my notes
> and save a recap to that property in Capsa? Let me confirm the property first."

## Example agent output (fictional)

```
Here's a recap drafted from your meeting notes:

  "Reviewed spring cleanup scope and irrigation start date. Jordan wants a
  revised quote for added mulch beds by Friday; renewal decision expected end of
  month. Next step: send updated proposal, follow up Monday."

To save this to the right property, I looked up jordan@example.com — that contact
is the primary on two properties:

  1. Maple Ridge HOA — Northgate branch, account owner Sam Lee (id 4812)
  2. Maple Ridge Commons — Northgate branch, account owner Sam Lee (id 5190)

Your notes mention "spring cleanup" but not which site. Which property should this
note go on — 1 or 2 — and does the recap read right, or want any edits?
```

After the user picks a property, the agent calls
`capsa_prepare_command_center_note` and shows the returned review (property, note
text, options). When the user approves it, the agent calls
`capsa_create_command_center_note` with only the `proposal_token` and
`confirmed: true`, then reports the created note reference and Aspire sync status.

All names, emails, and details above are fictional.

## Team specifics

<!--
  Persist your default meeting source, house note format, and whether the Aspire
  property-note append is allowed on your connection here. Keep the steps and stop
  rules in sync with the cookbook; re-pull after a connector upgrade.
-->
