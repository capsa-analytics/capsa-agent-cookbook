# Example playbook guidance

An update playbook in Capsa says who hears about which update types at which
properties, and what happens next for each type. Each next-step line carries
**guidance**: up to 4,000 characters of advice for whoever responds. Capsa ships
no default guidance; these pages are examples an admin can paste into a line and
edit, and an agent can read to understand what good looks like.

Guidance is advice, not a template. A response is a note by default; work is
assigned only when someone else or a later date is involved; Not actionable takes
a reason. Set the deadline on the line itself.

| Update type | Example |
| --- | --- |
| Work order / Contract service visit rescheduled | [visit-rescheduled.md](visit-rescheduled.md) |
| Work order / Contract marked lost | [marked-lost.md](marked-lost.md) |
| Proposal delivered | [proposal-delivered.md](proposal-delivered.md) |
| Work order / Contract service start date passed | [start-date-passed.md](start-date-passed.md) |
| New issue | [new-issue.md](new-issue.md) |
| Appointment with no follow-up recorded | [appointment-no-follow-up.md](appointment-no-follow-up.md) |

Paste the body (below the title) into the line's Guidance field. Names, amounts
and thresholds are placeholders; replace them with your company's.

To change guidance through the connector: `capsa_explain_update_settings`, then
`capsa_prepare_update_settings_change` with a `next_step` change carrying
`guidance`, then `capsa_save_update_settings_change` after the admin confirms.
