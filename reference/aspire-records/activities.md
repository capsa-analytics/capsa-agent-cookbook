# Activities: tasks, issues, appointments, and emails

Aspire keeps tasks, issues (including customer complaints), appointments, and
logged emails as **Activities**. This page explains how to find them with the
[Aspire records](../capabilities/aspire-records.md) tools. Read it when a user
asks about any of these. You don't need the rest of the cookbook.

> The connector's live output is the source of truth. For the current fields,
> call `capsa_describe_aspire_resources` with `resource: "Activities"`. For the
> open/closed rules and pitfalls, call it with `concept: "activities_open"`.
> Aspire records is enabled per connection. If `capsa_list_capabilities` does
> not list it, these tools are not available.

## Use when

- "What open issues does Maple Ridge HOA have?"
- "Which tasks are overdue?" or "What's on Dana's plate?"
- "How many complaints did we log last month, by category?"
- "What appointments are scheduled this week?"
- "What happened on this opportunity or work ticket?" (its activity history)

If a named Capsa capability already answers the question, prefer it. For
example, [property context](../capabilities/property-context.md) carries a
property's open-issue signals, and [job context](../capabilities/job-context.md)
has a job's issue drilldown. Use Activities for the individual records behind
those signals, or for questions those capabilities don't cover.

## The resources

| Resource | One row per | Use it for |
| --- | --- | --- |
| `Activities` | Task, issue, appointment, or email | The item itself: type, status, dates, category, and what it's attached to |
| `ActivityContacts` | Person on an activity | Who a task, issue, or appointment involves |
| `ActivityCommentHistories` | Comment on an activity | The discussion thread on an item |
| `ActivityCategories` | Company-defined category | The category names a company uses, such as complaint types |

`ActivityType` tells the kinds apart: `Issue`, `Task`, `Appointment`, or
`Email`. Casing and spacing can vary, so match with `contains` rather than
`equals`.

An activity can be attached to a property, an opportunity, a work ticket, an
invoice, or a payment, or to none of them. Related fields only go from a
child record to its parent. Start from `Activities` and filter on a field such
as `Property.PropertyName`. A property query can't list its activities.

## Open or closed

An activity is **open** when `CompleteDate` is empty **and** `Status` is not
`Completed`. Either signal closes it.

For emails, `Status` often shows where the email came from (for example,
`Source MS 365`). That is not a lifecycle state, so don't count those emails as
open work. Filter to the activity type you mean.

## Recipes

Each recipe is a query shape. Look up exact field names with
`capsa_describe_aspire_resources` first.

**Open issues for one property.** Use `capsa_find_aspire_records` on
`Activities` with these filters: `ActivityType` contains `Issue`, `CompleteDate`
is null, `Status` not equal to `Completed`, and `Property.PropertyName` (or
`PropertyID` once resolved). Ask for the subject, category, start and due
dates, and `CreatedByUserName`.

**Overdue tasks.** Use the same open filters with `ActivityType` contains
`Task`, plus `DueDate` before today. Sort by `DueDate`, oldest first.

**Complaints by category per month.** Use `capsa_summarize_aspire_records` on
`Activities` with a count, grouped by the category name and by month of
`StartDate` (or `CreatedDate`). Filter to issues. Categories are
company-defined, so ask the user which categories count as complaints rather
than guessing.

**Upcoming appointments.** Filter `ActivityType` contains `Appointment` and
`StartDate` from today to the end of the window. Sort by `StartDate`.

**Activity history for an opportunity or work ticket.** Filter `Activities` on
`OpportunityID` or `WorkTicketID`, sorted by `CreatedDate`. Report types,
dates, and subjects. Email subjects are blank, so for an email say that one was
logged and when.

**Who's on a task or issue.** Use `capsa_find_aspire_records` on
`ActivityContacts` filtered by `ActivityID`. To answer "what's open for Dana,"
filter by the person (`ContactName` or `ContactID`) and apply the full open
rule through the parent: `Activity.ActivityType` contains `Task` (or `Issue`),
`Activity.CompleteDate` is null, **and** `Activity.Status` not equal to
`Completed`. See the `AssignmentType` pitfall below.

**Who created or completed something.** `Activities` records who created each
item and who completed it. These names aren't returned by default, so ask for
`CreatedByUserName` and `CompletedByUserName` by name. Use `CompleteDate` to
place a completion in a period.

## Pitfalls

- **`AssignmentType` is about emails, not ownership.** On `ActivityContacts`,
  `TO`, `CC`, and `FROM` appear only on emails and describe who the email was
  addressed to. The people on a task, issue, or appointment have an empty
  `AssignmentType`. Don't read `TO` as "assigned to," and don't drop rows with
  an empty assignment type when looking for who owns a task.
- **`ActivityContacts` isn't available on every connection.** If the describe
  call says it isn't available, tell the user you can't see who is on each item
  on this connection. Don't infer an owner from the creator.
- **Email content is never returned.** Email subjects and notes come back
  blank. Never present an email's content or imply that you read it.
- **Private activities are excluded entirely**, along with their comments,
  people, and attachments. A count of activities is a count of non-private
  activities.
- **Notes are long.** On a large account, asking for `Notes` across many
  records can exceed the request size limit. List records without `Notes`
  first, then fetch notes for the few that matter.
- **Complaint labels in Capsa reports aren't an Aspire field.** Capsa's
  complaint classification combines AI with company category settings. Aspire
  activity categories are the closest raw equivalent. Say which one you used.

## Freshness

Data may be up to 24 hours old. Don't present it as a live to-do list. Say
"as of the last update."

## Related

- Capability: [Aspire records](../capabilities/aspire-records.md)
- Skill: [answer-a-data-question](../../skills/answer-a-data-question/SKILL.md),
  for counts and trends
- Pattern: [Resolving ambiguous names](../patterns/resolve-ambiguous-names.md),
  for "Dana" (contact? sales rep?) or a property name
