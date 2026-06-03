# Resolving ambiguous names — which dimension did the user mean?

*Pattern — a cross-cutting discipline the skills invoke, not a standalone
workflow. New to Capsa? Read [start-here.md](../../start-here.md) first.*

When a user names something — "pull sales for Tori Nash," "how's Maple Ridge
doing," "show me Chemical Treatments this quarter" — the agent has to figure out
*what kind of thing* that name is before it can query Capsa. Is "Tori Nash" a
sales rep or a property? Is "Chemical Treatments" a division or a service type? A
traditional app answers this with its UI: you typed into a field labeled "Account
Owner," or you're on the "Properties" tab. An agent has no such label. This
recipe is the procedure for recovering it.

## Purpose

Capsa organizes data along named dimensions — Branch, Account Owner / Sales Rep,
Division, Service Type, Service, property type, tag, industry, status, and
properties themselves. A bare name doesn't say which dimension it belongs to, and
the same word can land in more than one. This recipe teaches an agent to **resolve
a name to a dimension using the connector's own option lists and property search —
and to ask when more than one dimension matches — instead of guessing.**

The connector is explicit about this. Every capability states that *"Capsa does
not parse personal pronouns as filters; use explicit filter options or ask the
user to narrow."* Resolving a name to a dimension is the agent's half of that
contract.

This recipe is framework-agnostic and is a **building block**: other recipes
(follow-up batches, visit notices, property-context pulls) call it the moment a
user names something. Use it ad-hoc, fold it into a skill, or embed it in another
agent. The "Configuration" section is the contract; persistence is your call.

## When to use this recipe

- The user refers to an entity by name or abbreviation and the dimension isn't
  explicit.
- A request could plausibly match more than one dimension (a person who is both a
  Sales Rep and a property contact; a word used as both a Division and a Service
  Type).
- You're about to filter, report, or pull context and need a dimension value (an
  ID) you don't yet have.

Skip it when the user already gave the dimension explicitly ("the **property**
Maple Ridge," "**Division** Chemical Treatments") and the value resolves to
exactly one match — though even then, confirm rather than invent if the value
doesn't resolve.

## Required connected apps

- **Capsa MCP connector.** This recipe is pure Capsa — it uses the connector's
  describe / list / search tools to resolve names. No email or other connector is
  needed; the recipes that *act* on the resolved entity bring their own.

## The dimensions, and how the connector names them

Two things make names ambiguous in Capsa specifically:

1. **The same person wears different dimension labels per capability.** The people
   dimension is called **"Sales Rep"** under follow-up actions, but **"Account
   Owner"** under upcoming visits and property context. Translate the user's word
   ("rep," "owner," "AM") into the term the capability in play actually uses.

   | Capability        | People dimension  | Other filter dimensions                                |
   | ----------------- | ----------------- | ------------------------------------------------------ |
   | Follow-up actions | **Sales Rep**     | Branch                                                 |
   | Upcoming visits   | **Account Owner** | Branch, Division, Service Type, Service                |
   | Property context  | **Account Owner** | Branch, Division, property type, tag, industry, status |

2. **A name can be a property *or* a person *or* a property's contact.**
   `capsa_search_properties` matches fuzzy text against property, customer,
   contact, owner, tag, and ID — so one name can come back as a property *named*
   "Tori Nash," a property *owned by* Tori Nash, or a property whose *contact* is
   Tori Nash. Read the candidate fields to see which role matched; don't assume
   the first one.

## Configuration (optional — gather once if you want persistence)

Disambiguation needs no standing inputs, but two things are worth persisting if a
team hits the same names often:

- **A synonym map.** The team's words → the connector's dimension names (e.g.
  "rep" and "AM" → Sales Rep / Account Owner depending on capability; "site" →
  property). Keeps the agent from re-deriving the mapping every session.
- **Known collisions.** Specific names the team already knows are ambiguous (a rep
  who is also a property contact). Pre-recording these lets the agent jump
  straight to asking.

Persist these in a skill, a system message, or a wrapper script — or skip them and
resolve fresh each time.

## Runtime workflow

### 1. Check for an explicit dimension cue

Read the request for a word that names the dimension: "property," "site,"
"account," "rep," "owner," "division," "service," "branch," "tag," "industry,"
"status." If the user gave one, you already know the dimension — go to step 3 to
resolve the *value* within it.

### 2. If the dimension is implicit, probe the candidate dimensions

Don't guess from the shape of the name. Use the connector's own tools as a
dictionary:

- **Enumerable dimensions** (Account Owner / Sales Rep, Division, Branch, Service
  Type, Service, property type, tag, industry, status) — call the relevant
  `capsa_list_*_filter_options` for the capability in play and match the user's
  term against the returned values. These lists *are* your disambiguation
  dictionary: they return the only valid values and their IDs.
- **Properties, customers, and contacts** — call `capsa_search_properties` with
  the user's plain request and the fuzzy term, then inspect each candidate's
  matched role.

Run both when the name could be either a person or a place. Match
case-insensitively and allow for partials and abbreviations.

### 3. Resolve by how many dimensions matched

- **Exactly one dimension, one value** → proceed, and **state the assumption in
  one line** so the user can cheaply correct it: *"Reading 'Tori Nash' as a Sales
  Rep — say the word if you meant a property."*
- **One dimension, several values** (two reps named Tori Nash; three "Maple"
  properties) → list the candidates with distinguishing context (branch, owner,
  ID) and ask which.
- **More than one dimension** (Tori Nash is both a rep and a property contact) →
  this is the core case: **ask.** Present the candidate readings side by side with
  enough context to choose.
- **Zero matches** → don't fabricate a value or an ID. Report no match, offer the
  closest near-matches the search returned, and ask for a correction or spelling.

### 4. Carry the resolution forward

Once resolved, pin the (dimension → value → ID) for the rest of the session and
pass the ID into the filters of whatever capability you're using. Don't
re-disambiguate the same name every turn. If the conversation later switches
capabilities (follow-ups → property context), remember the people dimension
changes name (Sales Rep → Account Owner) even though it's the same person.

## Stop rules

- **Never silently guess the dimension.** The connector won't parse a name into a
  filter on its own; the agent shouldn't either. One match → state the assumption;
  multiple → ask.
- **Never invent a value or ID.** Use only values returned by the option lists or
  search. No match means no match.
- **Respect capability availability.** If the capability whose dimension you'd
  resolve against isn't enabled for the connection, say so — don't resolve the
  name against a dimension you can't read.
- **Don't over-collapse roles.** A `capsa_search_properties` hit on "Tori Nash"
  might be a property *owned by* Tori Nash, not a property *named* Tori Nash. Check
  the matched role before reporting.
- **Carry freshness through.** Resolved context can be up to 24 hours old; pass
  that warning along the same as any other Capsa read.

## Example user prompt

> "Pull the sales data for Tori Nash."

## Example agent output (fictional)

After calling `capsa_list_property_context_filter_options` (Tori Nash appears as an
Account Owner) and `capsa_search_properties` for "Tori Nash" (a property lists Tori
Nash as its contact):

```
"Tori Nash" matches two different things in Capsa, so I want to confirm before
pulling numbers:

1. Account Owner — Tori Nash (a person who owns a book of properties)
   -> I'd pull sales across every property they own.

2. Property contact — Tori Nash is the listed contact on "Maple Ridge HOA"
   -> I'd pull sales for that one property.

Which did you mean? (Owner -> I summarize the whole book; property -> just
Maple Ridge.)
```

After the user picks, the agent resolves to the matching ID, pulls the context with
the right filter, and notes that Capsa data may be up to 24 hours old.

All names above are fictional.
