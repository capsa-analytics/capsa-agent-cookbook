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
- `capsa_create_command_center_note` — create a confirmed Command Center property
  note against a single, user-confirmed `property_id`.

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

## Writing (confirmation-gated)

`capsa_create_command_center_note` writes only against a single property the user
has explicitly confirmed. It takes `property_id`, the `note` body, an optional
`append_to_aspire_property_note`, and a `write_confirmation` object carrying
`confirmed_by_user`, a `summary`, `selected_property_id`, and
`selected_property_name`. The connector rejects the write when:

- `confirmed_by_user` is not true,
- `selected_property_id` does not match `property_id`, or
- `selected_property_name` does not match the selected property.

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
- Capability: [Property context](property-context.md) — the same properties and
  filter dimensions, read side.
