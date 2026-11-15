---
title: "Pricing"
description: "Three plans metered in credits, where one credit buys 350 bytes of ingested payload. Storage and seats are not metered."
canonical: https://past.dev/pricing
last-updated: 2026-11-15
---
# Pricing

> Three plans, metered in credits. One credit buys 350 bytes of an ingested payload. Recall is metered on Pay as you go only. Storage, entities and seats are not metered.

Source: https://past.dev/pricing

## How credits work

- **1 credit** per 350 bytes of an ingested payload, rounded up for each data point. A 700 byte payload costs 2 credits.
- **0.1 credit** per webhook event. Every event a webhook sends is counted, including events your filters do not ingest. An event that is ingested also pays the ingestion credits for its payload.
- **1 credit** per recall or answer call on Pay as you go, and above fair use on Flex and Enterprise.
- **0 credits** for storage, memories, entities, relationships and seats, on every plan.

Credits per month = ingestions x credits per payload + webhook events x 0.1 + ingested webhook events x credits per payload.
The calculator assumes your filters ingest one webhook event in five. Each ingested event pays the ingestion credits for its payload on top of the 0.1 credit every event costs.
Credits per payload = the payload size in UTF-8 bytes divided by 350, rounded up, with a floor of 1.
On Pay as you go, recall and answer calls add 1 credit each: recall credits = recall calls.
*Fair use applies. Above it, a recall costs 1 credit.
Pay as you go's starting credits are granted once, so a month of steady use buys every credit it spends, at least 100,000 at a time. Past its included credits, Flex buys on the same sheet.
Pay as you go and Flex buy more credits on one sheet, from 100,000 credits: the prices are under "Buy more credits" below.

## Input tokens saved

Tokens saved per month = recall calls x (history tokens - 8,000).

- Without memory, each recall sends one month of ingested text: 4 bytes per token, capped at 1,000,000 tokens.
- With past.dev, each recall sends at most 8,000 tokens of evidence: the recall page on Pay as you go and Flex.
- On Pay as you go each recall costs 1 credit. On Flex and Enterprise recall is unlimited, with fair use.

## Pay as you go: $0 / month

For starting with your own data and growing at your own pace. Buy credits when you need them.

Included credits: 50,000 once, to start (200,000 if you sign up with a work email). Buy more from 100,000 credits for $30. Credit rollover: None.

- 50,000 credits (a $15 value) to start
- 200,000 credits (a $60 value) if you sign up with a work email
- Buy more from 100,000 credits for $30, valid for 90 days
- 1 credit per recall call
- Up to 8,000 tokens per recall
- 1 project
- 500 requests per minute
- Unlimited storage
- 365 day data retention
- Unlimited seats
- Community support

## Flex: $99 / month

For an application in production. Credits meter ingestion. Recall calls are unlimited*.

Included credits: 400,000 per month. Buy more from 100,000 credits for $30. Credit rollover: 30 days.

- 400,000 credits per month
- Buy more from 100,000 credits for $30, valid for 365 days
- Unlimited recall calls*
- Up to 8,000 tokens per recall
- 5 projects
- 750 requests per minute
- Unlimited storage
- 3 year data retention
- Webhooks
- Email support
- Automatic top-up at a threshold you set

## Enterprise: Custom

The whole engine, from 5,000,000 credits a month, priced against your deployment and your terms.

Included credits: from 5,000,000 per month. Buys no packs. Credit rollover: None.

- From 5,000,000 credits per month
- Unlimited recall calls*
- Up to 32,000 tokens per recall
- Unlimited projects
- 1,000 requests per minute
- Unlimited storage and retention
- Custom retrieval arms
- SSO and SAML
- Bring your own cloud
- Slack or Teams support with an account manager

SOC 2 Type II audited, ISO 27001 and ISO 27701 certified. Reports and a data processing agreement are available on request. [Security](https://past.dev/security)

## Buy more credits

Pay as you go and Flex can buy more credits at any time from the console. The larger the purchase, the less each credit costs.

| Credits | Price | Per 1,000 credits |
| --- | --- | --- |
| 100,000 | $30 | $0.30 |
| 500,000 | $130 | $0.26 |
| 1,000,000 | $220 | $0.22 |
| 5,000,000 | $850 | $0.17 |
| 10,000,000 | $1,300 | $0.13 |

Buy any amount from 100,000 to 50,000,000 credits in one purchase, in steps of 1,000. Each row is a quantity at which the price per 1,000 credits changes. All of the purchase pays the rate of the largest row it reaches.
Bought credits last 90 days on Pay as you go and 365 days on Flex. Flex can also buy them automatically when the balance reaches a threshold you set.
Enterprise buys no packs. Its agreement sets its monthly credits, from 5,000,000.

## Compare the plans

| | Pay as you go | Flex | Enterprise |
| --- | --- | --- | --- |
| **Credits and billing** |  |  |  |
| Price per month | $0 | $99 | Custom |
| Included credits | 50,000 to start, 200,000 if you sign up with a work email | 400,000 per month | From 5,000,000 per month |
| Buy more credits | From 100,000 for $30 | From 100,000 for $30 | No |
| Credit rollover | None | 30 days | None |
| Bought credits expire | After 90 days | After 365 days | Not needed |
| Automatic top-up | No | Yes | No |
| Billing | Card | Card | Annual agreement |
| **Usage and limits** |  |  |  |
| Ingestion | Metered in credits | Metered in credits | Metered in credits |
| Recall calls | 1 credit each | Unlimited* | Unlimited* |
| Tokens per recall | Up to 8,000 | Up to 8,000 | Up to 32,000 |
| Projects | 1 | 5 | Unlimited |
| Requests per minute | 500 | 750 | 1,000 |
| Storage | Unlimited | Unlimited | Unlimited |
| Data retention | 365 days | 3 years | Unlimited |
| API log retention | 7 days | 90 days | Unlimited |
| Seats | Unlimited | Unlimited | Unlimited |
| **Engine** |  |  |  |
| Memories | Unlimited | Unlimited | Unlimited |
| Entities and relationships | Unlimited | Unlimited | Unlimited |
| Source-backed memory | Yes | Yes | Yes |
| Recall with dated evidence | Yes | Yes | Yes |
| Tracing | Yes | Yes | Yes |
| Usage analytics | Yes | Yes | Yes |
| Webhooks | No | Yes | Yes |
| Entity type and edge customization | No | No | Yes |
| Custom retrieval arms | No | No | Yes |
| **Enterprise and support** |  |  |  |
| Support | Community | Email | Slack or Teams |
| Account manager | No | No | Yes |
| SSO | No | No | Yes |
| SAML | No | No | Yes |
| Bring your own cloud | No | No | Yes |

## Questions about pricing

### What is a credit?

A credit buys 350 bytes of an ingested payload. Every data point costs at least 1 credit, and one more credit for each additional 350 bytes or part of it. A batch prices each of its data points in the same way and adds them up. A 700 byte payload costs 2 credits. A 27,000 byte meeting transcript costs 78 credits. A batch of 10 data points of 100 bytes each costs 10 credits.

### What does not cost credits?

Storage, memories, entities, relationships and seats cost nothing on any plan. Recall and answer calls cost nothing on Flex and Enterprise, within fair use. On Pay as you go they cost 1 credit each, so 1,000 recall calls cost 1,000 credits. A data point that past already holds unchanged costs nothing when you send it again, and a retry with the same idempotency key costs nothing. On Flex and Enterprise, within fair use, your bill depends only on how much data you send in.

### How much evidence does one recall return?

A recall returns up to 8,000 tokens of evidence on Pay as you go and Flex: the memories that answer the query, with the excerpts of the data points behind them. Enterprise returns up to 32,000 tokens of evidence per recall.

### Is the payload measured in bytes or characters?

Bytes, encoded as UTF-8. An unaccented Latin character is 1 byte, an accented Latin character is 2, a Chinese, Japanese or Korean character is 3, and an emoji is 4 or more. The same text in Japanese therefore costs about three times as many credits as it does in English. The calculator on this page counts the bytes of whatever you paste into it, so you can measure your own content rather than estimate it.

### What happens when I use all my included credits?

On Pay as you go and Flex you buy more credits whenever you need them, at least 100,000 at a time: 100,000 for $30, and less per credit as the purchase grows, down to $0.13 per 1,000 from 10,000,000 credits. The table under the plans gives every price. On Flex you can also have them bought automatically when the balance reaches a threshold you set. When the balance reaches zero, sends return a billing error, and on Pay as you go recall calls too, until you buy credits or, on Flex, the month resets. On Enterprise a send past the month's credits is refused until the reset, and the console offers to book a call. Your project data is not changed or deleted.

### Do unused credits roll over?

The starting credits on Pay as you go (50,000, or 200,000 if you sign up with a work email) are granted once and do not come back. Credits you buy expire 90 days after purchase on Pay as you go and 365 days after purchase on Flex. On Flex, unused included credits roll over for 30 days, after which they expire. Enterprise's monthly credits, from 5,000,000, do not roll over.

### When should I move from Pay as you go to Flex?

When you need what Pay as you go does not include: webhooks, more than one project, unlimited recall calls, 3 year data retention, email support, or 750 requests per minute. Flex's $99 also includes 400,000 credits a month, more than $99 of packs buys, and on either plan a larger purchase costs less per credit. The calculator below prices your volume on both.

### Does the cost grow as a project gets larger?

Ingestion cost grows with the amount of data you send. On Pay as you go recall cost grows with the number of recall calls, at 1 credit each; on Flex and Enterprise recall is unlimited, with fair use. Query cost does not scale linearly with total stored history, and storage is not metered on any plan.

### Do my end users need a past.dev account?

No. Every plan allows unlimited seats and your end users do not need past.dev accounts. Billing is based on API usage.

### Can I see what a call cost?

The console dashboard records each ingest and recall call by project, with the credits it consumed. You can use those records to price a feature or set a limit for one of your own customers.

### What is the difference between Flex and Enterprise?

Both serve unlimited recall calls. Flex is bought with a card at $99 a month, with 400,000 credits a month plus top-up packs, 5 projects, 3 year data retention and up to 8,000 tokens of evidence per recall. Enterprise is an annual agreement, from 5,000,000 credits a month, with unlimited projects, storage and retention, up to 32,000 tokens of evidence per recall, custom retrieval arms, SSO, SAML, deployment in your own cloud, and Slack or Teams support with an account manager.

### Can past.dev run in my own cloud?

Pay as you go and Flex run on the managed service. On an Enterprise agreement, past.dev runs with your own AWS, Google Cloud or Azure account, operated by us. You choose the database only, where your memory is stored in a database that you own and the engine runs on our infrastructure, or the full deployment, where the engine and its databases run in your account. Book a call to discuss your constraints.

Get API key: https://sso.past.dev/sign-up
Book a demo: https://past.dev/call