# Capsa cookbook index

Use this page to choose one recipe. Read only the linked skill or reference page
needed for the current request. Do not load the whole cookbook at connection
startup or before every Capsa tool call.

For a simple data lookup, use the relevant Capsa tool directly. Use
`capsa_describe_tool` if its inputs are unclear. Use `capsa_list_capabilities`
when you need to discover what this connection can do; use
`capsa_describe_capability` for one selected capability. Connection access and
filter values come from live Capsa tools, not this index.

| User's task | Read on demand |
| --- | --- |
| New to Capsa or uncertain about approval and completion rules | [Orientation](skills/capsa-orientation/SKILL.md) |
| Draft and send proposal follow-ups | [Proposal follow-up batch](skills/proposal-followup-batch/SKILL.md) |
| Draft notices for sensitive upcoming visits | [Sensitive visit notice](skills/sensitive-visit-notice/SKILL.md) |
| Rank a renewal book | [Renewal portfolio triage](skills/renewal-portfolio-triage/SKILL.md) |
| Review one renewal in depth | [Renewal deep dive](skills/renewal-deep-dive/SKILL.md) |
| Save reviewed meeting notes to a property | [Meeting notes to Command Center](skills/meeting-notes-to-command-center/SKILL.md) |
| Draft a property update | [Property site update](skills/property-site-update/SKILL.md) |
| Build a forward-looking property plan | [Property plan builder](skills/property-plan-builder/SKILL.md) |
| Review active jobs across a book | [Job book review](skills/job-book-review/SKILL.md) |
| Triage a property book | [Property book triage](skills/property-book-triage/SKILL.md) |
| Prepare a budget item change | [Budget item change](skills/budget-item-change/SKILL.md) |
| Prepare a price recommendation | [Price recommendation change](skills/price-recommendation-change/SKILL.md) |
| Explain or change teammate permissions and roles | [Teammate permission management](skills/teammate-permission-management/SKILL.md) |
| Review Ops or Sales scorecards | [Scorecard review](skills/scorecard-review/SKILL.md) |
| Start an improvement plan | [Improvement plan start](skills/improvement-plan-start/SKILL.md) |
| Resolve an ambiguous person or property name | [Name resolution pattern](reference/patterns/resolve-ambiguous-names.md) |

For tool behavior, read only the matching [capability reference](reference/README.md).
For automated routing, use [index.json](index.json). Reuse a page already read
in the current task; fetch it again only when the task changes or guidance is stale.
