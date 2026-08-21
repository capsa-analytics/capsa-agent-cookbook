---
description: Pull a property's relationship, health, satisfaction, and outstanding-item context from Capsa's property_context capability, then draft an internal brief and a customer-safe update for the property manager covering what happened, what's upcoming, and what's needed from them. Use when preparing a property manager check-in or status update.
---

# Property site update

Tell a property manager what happened at their property recently and what's
needed from them — decisions on proposals, feedback, scheduling — using Capsa's
property context as the evidence. Produces two artifacts: an internal brief with
everything, and a customer-safe draft the user reviews before it goes anywhere.

New to the Capsa connector? Start with the **capsa-orientation** skill (or
https://github.com/capsa-analytics/capsa-agent-cookbook).

## Purpose

Property managers don't get a periodic check-in by default, even though the
connector already holds everything a manager would look at first: relationship
and health status, recent satisfaction signals, what happened, what's scheduled,
and what's still open. This skill turns that context into two things — an
internal brief covering everything, including loose ends the account manager
still needs to chase, and a customer-safe draft the user can review, edit, and
send however they choose.

The steps are the same whether this runs as an installed skill, is pasted into
another agent, or is run ad-hoc. The "Configuration" section lists the inputs a
run needs; persist them in the Team specifics block below, a system message, or a
wrapper script — or leave them runtime-only.

## When to use

Use it when **all** of the following are true:

- The Capsa MCP connector is connected and the `property_context` capability is
  available (check `capsa_describe_capability` if unsure).
- The user wants a status update for one property's manager or primary
  contact — not a single ad-hoc data question.
- A property is named, or there's enough contact context (an email or name) to
  resolve one.

Skip it for a one-off question ("what's this property's gross margin?") — just
call `capsa_get_property_context` directly. Skip it too if `property_context`
isn't enabled for the connection; ask the user to enable it first.

## Required connected apps

- **Capsa MCP connector.** Supplies property resolution, single-property
  context, and every drilldown this recipe uses.

This recipe has no send step, so no email or messaging connector is required.
Property context is read-only, and this recipe stops at handing the user a
draft — if they want it sent, that happens on their own initiative through
whatever channel they choose, outside this recipe's boundary.

## Configuration

The inputs a run needs. Most vary session-to-session, so leaving them
runtime-only is fine.

- **Property.** A property ID, a name/query for `capsa_search_properties`, or a
  contact (email or name) for `capsa_find_properties_by_primary_contact` when
  there's no property named yet.
- **Update audience.** Which contact the customer-safe draft addresses —
  default to the property's primary contact; ask if more than one candidate
  exists or the user names someone else.
- **Dollar/margin visibility (optional).** Default: leave revenue, cost,
  margin, and AR figures out of the customer draft. Include them only if the
  user asks.
- **Internal brief destination (optional).** Where the internal brief goes if
  not just chat — a doc, a ticket, a Slack message. Skip if a chat summary is
  enough.

## Workflow

### 1. Resolve the property

If a property is named, call `capsa_search_properties` to find the exact match —
see [Resolving ambiguous names](../../reference/patterns/resolve-ambiguous-names.md)
if more than one candidate comes back. If starting from a contact instead (a
property manager's name or email, no property named), call
`capsa_find_properties_by_primary_contact` and apply the same
corroborate-before-trusting discipline the
[meeting-notes-to-command-center](../meeting-notes-to-command-center/) recipe
uses: a lone match isn't proof of uniqueness, and a property hint only ranks
candidates — it never filters them. (This contact lookup is part of the
`property_context` read permission this recipe already requires; if it is ever
unavailable on a connection, `capsa_search_properties` also matches contact
names as a fallback.) Present every candidate and let the user choose; never
guess a property for a customer-facing draft.

### 2. Pull single-property context

Call `capsa_get_property_context` with the resolved `property_ids: [id]`. One
call returns everything a status check starts from: `relationship_status`
(active contract, construction, or renewal timing), `satisfaction` (open and
recent complaint/issue counts, `last_touch`), `production.upcoming_visit_count`
and `next_visit`, `sales` (delivered proposals, days since last proposal), the
`health` block (`status`, `summary`, `last_reviewed_at`, and — when present — a
standing recommendation with a plain-English `explanation`), a compact
`property_card` (`brief` and `whats_changed` sections only), and the
`available_drilldowns` list. Skim this before deciding which drilldowns are
worth a follow-up call — don't pull every drilldown by default.

### 3. Pull drilldowns for what the compact context doesn't cover

`capsa_get_property_context_drilldown` takes exactly one `property_id` and one
`drilldown_id` per call — pull only what the update needs, one call at a time:

- **What happened** — `property_card` for the full narrative (adds
  `activity_digest`, `emerging_risks`, `open_opportunities`, and
  `client_priorities` beyond the compact `brief`/`whats_changed` from step 2),
  `recent_completed_issues`, `last_touch_activity`.
- **What's upcoming** — `upcoming_visits`. Renewal/contract timing already came
  back in `relationship_status`; no separate call needed for that.
- **What's outstanding** — `delivered_proposals`, `proposed_opportunities`,
  `open_issues`, `open_complaints`.

Each block and drilldown carries its own freshness: property data generally may
be up to 24 hours old, and `property_card` sections are nightly-generated
narrative with a per-section `as_of` date, not a live read. Carry the actual
date forward into both artifacts rather than implying "as of right now."

<!--
  Coming soon: Phase B3's property_story evidence pack (roadmap working name)
  is expected to collapse steps 2 and 3 above into one composed read with
  per-block freshness, plus add delivered-opportunity and visit-note AI
  summaries this recipe can't reach today. Until it ships, keep stitching
  capsa_get_property_context with sequential capsa_get_property_context_drilldown
  calls as described above.
-->

### 4. Compose two artifacts

Write two distinct documents from the same pulled context — never one document
with the internal parts merely hidden in the customer copy:

- **Internal brief.** Everything relevant: the full health picture and its
  recommendation, satisfaction counts, dollar/margin figures where useful
  internally, every open item, and anything the account manager still needs to
  chase (a stale recommendation, a proposal with no activity, a visit needing
  internal follow-up) — flagged explicitly, not buried in prose.
- **Customer-safe draft for the property manager.** Plain language only: no
  property IDs, connector field names, or raw status codes — use the
  customer-facing names and descriptions the context already returns. Activity
  references are subjects/types only — `last_touch_activity` doesn't expose
  message bodies; that's a deliberate Capsa boundary, not a gap to fill in.
  Leave dollar and margin figures out unless the user asked for them in this
  draft. State nothing the pulled context doesn't support, and carry the real
  as-of date for narrative sections instead of implying it's live.

### 5. Build the asks section

Both artifacts should include a clear "what we need from you" section, drawn
only from what the reads returned:

- **Proposals awaiting decision** — from `delivered_proposals`, whichever
  aren't yet won or lost.
- **Feedback requests** — recently completed work (`recent_completed_issues`)
  worth asking the property manager to confirm or react to.
- **Upcoming-visit confirmations** — from `upcoming_visits`, anything that
  needs site access, scheduling confirmation, or a heads-up acknowledged.

### 6. Hand both to the user — never send

Present the internal brief and the customer-safe draft together and stop.
Property context is read-only and this recipe has no send step at all — unlike
[sensitive-visit-notice](../sensitive-visit-notice/), which drafts and then
sends through a connected email provider after per-item approval, this recipe's
job ends at the draft. If the user wants it sent, that's their call, through
whatever channel they choose, outside this recipe.

## Stop rules

- **No sending.** This recipe never sends anything through any channel. Hand
  off both artifacts and stop.
- **No fabricated events.** Every fact in either artifact must trace to a
  specific property-context field or drilldown; if a read doesn't show it, it
  doesn't appear.
- **Respect each block's as-of date.** Carry the real freshness/as-of markers
  per block forward — property data can be up to 24 hours old, and
  `property_card` narrative sections are nightly-generated, not live. Never
  present either as "as of right now."
- **No internal IDs or raw statuses in the customer draft.** Use plain-language
  property/customer names and status descriptions only.
- **No email bodies.** Only activity subjects/types are available from
  `last_touch_activity`; the connector doesn't expose message content by
  design. Never invent or infer body content.
- **No dollar or margin internals unless asked.** Leave revenue, cost, margin,
  and AR figures out of the customer draft by default.
- **Missing data surfaces, never gets smoothed over.** If a section, drilldown,
  or expected signal is unavailable, absent, or comes back with a customer-safe
  "not evaluated" note, say so plainly in the internal brief — don't silently
  drop it or improvise a workaround.
- **Log what the connector can't answer — with consent.** If the user needs
  something the `property_context` capability doesn't provide, offer to record
  the gap with `capsa_log_feature_request`; log a concise, redacted
  description only after the user agrees, per
  [capsa-orientation](../capsa-orientation/) loop step 5.

## Example user prompt

> "Can you put together an update for the property manager at Maple Ridge HOA —
> what's happened lately, what's coming up, and what we need from them? I want
> to review it before anything goes out."

## Example agent output (fictional)

```
Pulled context for Maple Ridge HOA (active contract, Northgate branch).

INTERNAL BRIEF

- Health: yellow — "Irrigation complaints trending up; renewal at risk"
  (reviewed 2026-08-01). Standing recommendation: red — Days Since Last
  Activity 42 days (threshold 30), Gross Margin % 18% (threshold 25%). No
  internal follow-up logged against this yet — flag before sending.
- Satisfaction: 1 open complaint, 3 open issues (1 quality-flagged).
- Sales: 1 delivered proposal (irrigation repair, delivered 12 days ago, no
  decision yet); 0 proposed opportunities.
- Upcoming: 1 visit scheduled 2026-08-22 (mulch refresh).
- Last touch: a call logged 2026-08-14 (subject only — no body available).

CUSTOMER-SAFE DRAFT — for Jordan Lee, Maple Ridge HOA

  Hi Jordan,

  A quick update on Maple Ridge HOA. Since our last check-in, our team
  wrapped up two service items, with one still in progress that we're staying
  on top of. We also have a proposal out for irrigation repair that's still
  awaiting your decision, and a visit scheduled for 8/22 (mulch refresh) —
  let us know if the site will be accessible that day.

  We'd also love your take on the recent work — anything we should adjust?

  (As of last activity 2026-08-14; context pulled 2026-08-19.)

Want me to adjust either before you send it?
```

All names, emails, dates, and figures above are fictional.

## Team specifics

<!--
  Persist your default customer-draft tone/signature, whether dollar/margin
  figures are ever included by default, and any standing property manager
  contact preferences here. Keep the steps and stop rules in sync with the
  cookbook; re-pull after a connector upgrade.
-->
