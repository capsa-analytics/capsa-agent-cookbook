# Contributing

This cookbook collects recipes that show how agents can use the Capsa MCP
connector with other connected apps to complete useful work. New recipes are
welcome.

## What a good recipe looks like

A recipe should:

- **Explain how an agent uses the Capsa connector to complete work.** The
  reader should be able to follow the recipe end-to-end without needing
  internal product knowledge.
- **Use fictional, generic examples.** Names, emails, companies, and dates
  in examples must not refer to real customers, prospects, or accounts.
- **Keep the user in the approval loop.** Any action that sends mail, edits
  external data, or otherwise leaves the agent's context should require
  explicit user approval first.
- **Treat completion recording carefully.** Record completion only after
  evidence the work actually happened — a draft, a plan, or an intent is
  not completion.

A recipe should not:

- Include secrets, tokens, internal URLs, or anything that wouldn't belong
  in customer-facing product documentation.
- Reference real customer data, real account names, or anything pulled
  from a private system.
- Describe Capsa's internal implementation, infrastructure, or storage —
  this cookbook is about how to *use* the connector, not how it's built.

## Recipe structure

Use the existing recipes as a template:

- Purpose (include a short note that the recipe is framework-agnostic and
  point readers at the Configuration section)
- When to use
- Required connected apps
- Configuration (the inputs a run needs, with optional persistence
  pointers — skill, system message, wrapper script). Include this even
  when most inputs vary session-to-session; the recipe should still name
  them in one place.
- Workflow (numbered steps)
- Stop rules
- Example user prompt
- Example agent output (fictional)

Keep recipes short. If a recipe is growing past a page or two, consider
splitting it.

## Submitting changes

Open a pull request with a clear description of:

- the workflow the recipe covers,
- the connectors it expects,
- anything reviewers should look at closely.

We review for clarity, safety (user approval, no invented data), and that
examples stay fictional.
