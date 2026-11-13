# Command Center notes (`command_center_notes`)

Resolve a property from a meeting's primary-contact context, have the user
confirm the exact property, then save a Capsa Command Center property note — with
an optional Aspire property-note append.

> This page mirrors `capsa_describe_capability` for `command_center_notes`. The
> connector's live output is the source of truth; availability and filter
> **values** are connection-specific — call `capsa_describe_capability` and
> `capsa_list_property_context_filter_options` at runtime, don't assume them. For
> exact tool inputs/outputs, call `capsa_describe_tool`.

## Use when

- A meeting-note source (a connected notes app or a pasted transcript/summary)
  gives a primary contact email or name and the user wants a Capsa note saved.
- The primary contact may manage multiple properties and the exact property must
  be selected before writing.
- The user confirms the selected property and the note text for Command Center.

## Tools

- `capsa_find_properties_by_primary_contact` — find every accessible property for
  a primary-contact email or fuzzy name **before** writing. Returns the full
  candidate list and whether user selection is required; it never picks for you.
  (Shared read: it belongs to the `property_context` capability's read
  permission, so read-only workflows can use it without notes access.)
- `capsa_prepare_command_center_note` — review one note: checks the property and
  rights and returns the exact property, note text and options with a
  `proposal_token`. Saves no note.
- `capsa_create_command_center_note` — save exactly the reviewed note after the
  person confirms it. Takes only `proposal_token` and `confirmed: true`.

## Resolving the property

`capsa_find_properties_by_primary_contact` takes a `primary_contact_email` and/or
`primary_contact_name` (at least one), an optional `property_hint`, the same
property-context ID filters (`branch_ids`, `account_owner_ids`, `division_ids`,
`property_type_names`, `property_tags`, `industry_names`), and `max_properties`
(1–250, default 100). It returns a `resolution_status`, a `requires_user_selection`
flag, primary-contact groups, and every accessible candidate property up to the
cap, each with a match reason.

- **Email** is the exact-match key; use it when the source provides one.
- **Name** is a fuzzy fallback or supplement.
- **`property_hint` ranks and annotates only — it never hides or filters out other
  properties for the contact.** Surfacing every property the contact touches is
  the whole point of the resolver; don't collapse the list.
- **A lone hit is not proof of uniqueness.** The resolver matches on each property's
  *primary contact*, so a property owned by the same person but with **no primary
  contact recorded** won't be returned — even when its name matches and it holds the
  active contract. For a name-based (fuzzy) match or a single result, corroborate
  with `capsa_search_properties` on the contact name before writing, and require
  user selection if same-named or same-address properties surface. Treat only an
  exact-email match with no same-named siblings as unambiguous.
- **Request the full set and watch for truncation.** Set `max_properties` to the cap
  (250) for a contact that may manage many properties; if the result returns at the
  cap (`row_count` equals `result_cap`), the list may be truncated — narrow with a
  filter and re-run before confirming a write.

## Writing (review, then save)

A note is saved in two steps, and only against a single property the user has
explicitly confirmed (2026-11-12; before then the write took a `write_confirmation`
object in the same request, which is now refused with a "review first" message).

1. `capsa_prepare_command_center_note` takes `user_request`, `property_id`, the
   `note` body, an optional `append_to_aspire_property_note` and an optional
   `add_to_future_plans` boolean that flags the note as a forward-looking plan (it
   then comes back in `capsa_get_property_context`'s `future_plans` block for that
   property — see [Property context](property-context.md)). It saves nothing and
   returns `saved: false`, a `proposal_token`, `expires_at` and a `review`: the
   property (id, name, customer), the trimmed note and both options.
2. Show that review to the person. Only after they confirm it,
   `capsa_create_command_center_note` takes
   `{"proposal_token": "<from the review>", "confirmed": true}` and nothing else.
   The saved note is exactly the reviewed property, text and options.

The same note-write permission covers `add_to_future_plans`; it is not a separate
write path. The connector refuses when:

- there is no review for the token, or the save carries anything besides the token
  and `confirmed: true` (including a `write_confirmation` object);
- the request changed — prepare again and show the new review;
- the review expired (20 minutes) or belongs to another person;
- the token is for a different save tool.

A review saves once. Sending the same save again returns the first result with
`replayed: true` and never saves a second note. Rights and property access are
checked again when saving. A refusal before saving leaves the review usable; after
an uncertain result, read the property's notes before preparing again.

Never call it from contact identity alone. Confirmed property + confirmed note
text is the evidence gate here, exactly as send evidence gates follow-up
completion.

It returns the created note identity, the selected property identity, the
`created_by` actor, an `aspire_property_note_sync` status, and any warnings. The
optional Aspire append **queues a background sync — it does not write
synchronously**, so the Capsa note saves first and the Aspire append returns as
`queued` when enabled.

## Boundaries

- Never write a note by contact alone — a confirmed `property_id` is required.
- If contact lookup returns multiple properties or contacts, ask the user to
  choose one property before writing.
- V1 writes Capsa Command Center **property** notes — not job notes, comments, or
  direct Aspire visit notes.
- The Aspire append is optional and best-effort; prefer a Capsa-only write when
  the append isn't ready or isn't permitted on the connection.
- Capsa resolves data access from the connection; note writes may be disabled.

## Freshness

Property-resolution data may be up to 24 hours old; don't treat it as live
dispatch status.

## Related

- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md)
- Skill: [meeting-notes-to-command-center](../../skills/meeting-notes-to-command-center/)
- Skill: [property-plan-builder](../../skills/property-plan-builder/) — drafts
  and saves the `add_to_future_plans`-flagged note with the user in the loop.
- Capability: [Property context](property-context.md) — the same properties and
  filter dimensions, read side.
