# Start here

You've connected the **Capsa MCP connector**. Capsa gives an agent operational
business context — outstanding proposal follow-ups, upcoming scheduled visits,
property context, and renewals — organized along named dimensions, and (where
enabled) records approved writes: follow-up completion, and a confirmed Command
Center property note saved from your meeting notes. Capsa doesn't send email or
take external actions; your agent does that through *other* connected tools, after
you approve.

**If you do one thing:** install the
**[capsa-orientation skill](skills/capsa-orientation/)** (or copy its body into
your agent). It teaches an agent the loop and safety rules below so it behaves well
the moment it touches Capsa. Everything else here is reference.

## What can I actually do? — things to try

Say these in plain language; the agent works out the rest. What's available depends
on what's enabled for your connection — if something isn't, the agent will tell you
(it checks with `capsa_list_capabilities` first).

**Proposal follow-ups**
- "What proposal follow-ups are due this week?"
- "Draft follow-up emails for my outstanding proposals and let me review each
  before anything sends."
- "Show follow-ups for a given sales rep, and mark the ones I've already handled as
  done."

**Upcoming visits**
- "What visits are coming up in the next 7 days?"
- "Find this week's chemical-application visits and draft a heads-up to each
  property contact."

**Property context**
- "Pull the context on Maple Ridge HOA before I call them."
- "Which of my properties are up for renewal with low satisfaction?"
- "Summarize this quarter's sales for a given account owner's book."

**Renewals**
- "Which of my renewals starting next quarter need attention first?"
- "Which prior contracts have no renewal started yet?"
- "How did the Maple Ridge contract actually perform before I re-price it?"

**Meeting notes → Command Center**
- "Summarize my last call and save the recap to that property in Capsa — let me
  confirm the property first."
- "The contact from this meeting manages a few sites; which property should this
  note go on?"

**When a name is ambiguous**
- "Look up Tori Nash." — Capsa data spans people *and* places, so the agent checks
  whether you mean a sales rep, an account owner, or a property, and asks if it's
  unsure rather than guessing.

> Flagship workflows (follow-up email batches, sensitive-visit notices) ship as
> installable skills — see **[skills/](skills/)**. For the full map of every
> capability, see **[reference/](reference/)**.

## The loop every Capsa task follows

1. **Orient** — discover what's enabled now (`capsa_describe_service`,
   `capsa_list_capabilities`); don't assume.
2. **Resolve** — turn names into dimensions/IDs before querying; ask when a name
   matches more than one dimension.
3. **Act** — draft anything outbound for your review; send only after you approve.
4. **Record** — mark work done only on evidence (a real send, your confirmation),
   never on intent.

## The safety contract

- **Approval before send** — nothing external goes out without your approval.
- **Evidence before completion** — record done only after send evidence or your
  confirmation; a draft is not a send.
- **No invented data** — no value, ID, or fact the tools didn't return.
- **Freshness** — Capsa data can be up to 24 hours old; the agent flags that for
  time-sensitive calls.

## Use this in your agent

Three ways, all built on the same orientation skill:

- **Install it** — add the
  **[capsa-orientation skill](skills/capsa-orientation/)** to a framework that
  supports skills (e.g. Claude Code).
- **Copy it** — lift the body of that skill into your agent's system prompt.
- **Fetch it** — point an agent at this repo via the connector's
  `capsa_discover_playbooks` and let it pull what it needs.

The orientation skill is **discovery-first** on purpose: it tells the agent to ask
the connector what's enabled rather than trusting a hardcoded list, so it keeps
working as Capsa ships new capabilities. Re-pull it when you upgrade.
