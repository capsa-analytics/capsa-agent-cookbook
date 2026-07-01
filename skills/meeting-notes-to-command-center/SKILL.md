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

- **Capsa MCP connector.** Resolves the property from the primary contact and
  writes the Command Center note.
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

### 3. Resolve the property by primary contact

Call `capsa_find_properties_by_primary_contact` with the email (when present), the
name, and the `property_hint`. Pass ID filters only if the user has already scoped
to a branch/division/owner.

- Use the email for the exact match; use the name as fallback or supplement.
- The `property_hint` **only ranks and annotates** — it never hides other
  properties for the contact. Present the full candidate list.

### 4. Review candidate properties

- **No match** → stop and ask for more context (a different email, a property
  name); don't invent a property.
- **One property** → still show property, customer, branch, and account owner for
  confirmation before writing.
- **Multiple properties or contacts** (`requires_user_selection`) → present the
  full list and have the user pick exactly one. Never hide extras or pick for them.

### 5. Confirm property and note with the user

The user confirms the selected property (id and name) and approves or edits the
note body. This is the approval gate — nothing is written until the user confirms
both.

### 6. Write the Command Center note

Call `capsa_create_command_center_note` with:

- `property_id` = the confirmed property's id;
- `note` = the approved body;
- `write_confirmation.confirmed_by_user = true`, plus `summary`,
  `selected_property_id`, and `selected_property_name` matching the confirmed
  property. The connector rejects the write if the selected id/name don't match, so
  carry the exact values from the property the user confirmed.
- `append_to_aspire_property_note = true` **only** when the append is ready on the
  connection and the user asked for it. Otherwise leave it off — the Capsa note
  saves first and the Aspire append, when enabled, returns as `queued`.

### 7. Record the result

Report back the created note reference and identity, the property id and name, and
the Aspire sync status. Keep a short record — property, reviewer, timestamp, and
the source meeting link — so the write is traceable.

## Stop rules

- **Never write by contact alone.** A confirmed `property_id` is required — resolve
  and confirm the property first.
- **Never hide extra properties for the same contact.** Present the full candidate
  list; the user selects.
- **`property_hint` only ranks.** It must never filter the candidates.
- **Approval before write.** No note is written until the user confirms the exact
  property and the note text.
- **Match the confirmation.** `selected_property_id` / `selected_property_name`
  must match the confirmed property, or the write is rejected — don't retry with
  mismatched values.
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

After the user picks a property and approves the text, the agent calls
`capsa_create_command_center_note` with `confirmed_by_user: true` and the selected
property's id and name, then reports the created note reference and Aspire sync
status.

All names, emails, and details above are fictional.

## Team specifics

<!--
  Persist your default meeting source, house note format, and whether the Aspire
  property-note append is allowed on your connection here. Keep the steps and stop
  rules in sync with the cookbook; re-pull after a connector upgrade.
-->
