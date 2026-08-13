# Support load review: H1

A worked source for testing extraction. It deliberately mixes the shapes the
extractor is expected to recognise: a markdown table of periods, a table of
shares, a before/after pair, dated sentences, ordering language, contrast
language, and headline figures stated in prose.

## Summary

Ticket volume fell 14.2% against H2, but total handling hours were flat at 9,310.
Median time to close rose to 31 hours, up 22%. First-contact resolution fell to
61%. The easy tickets are the ones that went away; what remains takes longer.

## Volume by category

| Category | Before | After |
|---|---|---|
| Password & access | 5120 | 1880 |
| Billing questions | 4310 | 2240 |
| Booking changes | 3980 | 4110 |
| Property issues | 3450 | 3620 |
| Payouts | 2610 | 3180 |
| Everything else | 2010 | 3390 |

## Monthly arrivals

| Month | 2024 | 2025 | 2026 |
|---|---|---|---|
| January | 4210 | 4050 | 3910 |
| February | 4180 | 3920 | 3640 |
| March | 4020 | 3710 | 3120 |
| April | 3980 | 3480 | 2680 |

## Handling time by complexity band

| Band | Share |
|---|---|
| Under 1 hour | 9 |
| 1 to 8 hours | 24 |
| 1 to 3 days | 38 |
| Over 3 days | 29 |

## Conversion change by step

| Step | Change |
|---|---|
| Search to listing | 4.2 |
| Listing to enquiry | -1.8 |
| Enquiry to reply | -11.4 |
| Reply to agreement | 2.1 |

## What happens to a complex ticket

First the ticket is opened and lands in the general queue. Then it is triaged,
usually the same day. Next an owner is assigned, which is where most of the
delay accumulates. Finally it is either resolved or escalated. This is a loop
rather than a line: escalated tickets re-enter the queue and are triaged again,
which is why the backlog feeds itself.

## Timeline

In 2024 the team adopted the current platform. In March 2025 the self-serve
password flow shipped. In January 2026 the billing self-serve flow shipped. By
June 2026 both categories had fallen by more than half.

## Options

Assigning an owner at triage needs no new headcount, whereas weekend evening
cover does. Self-serve for payouts would cut handling hours, but it cannot ship
this quarter and is not reversible once launched.

### Pros

- No new headcount required for the triage change
- Ships within the quarter

### Cons

- Does not address weekend load
- Risks pushing the delay one step later
