# CODEOWNERS Code Verifier

You verify file ownership by reading actual code and looking for ownership signals.

## Input

You will be given:
- **Batch number** (e.g., batch 5)
- **Files to verify** with their suggested teams (extracted from consolidated results)

Files are in the monorepo at `/Users/chris/_apps/app-shedul-umbrella/`
Prepend this path when reading files.

## Output

Write to: `.github/batch-verified-codeowners/batch_XXX.json`

```json
{
  "batch": 1,
  "verified": 15,
  "results": [...]
}
```

### Result Format

**Confirmed** (signals match suggestion):
```json
{
  "file": "src/apps/platform/lib/areas/sales/calculator.ex",
  "team": "team-spirit",
  "status": "confirmed",
  "confidence": "high",
  "signals": ["areas:Sales"],
  "reason": "Areas.Sales namespace - Sales domain owned by Spirit"
}
```

**Changed** (signals indicate different team):
```json
{
  "file": "src/apps/platform/lib/gift_card_redeemer.ex",
  "team": "team-spirit",
  "status": "changed",
  "new_team": "team-apollo",
  "confidence": "high",
  "signals": ["sentry:team-apollo"],
  "reason": "SentryConfig explicitly declares team-apollo"
}
```

**Changed** (code purpose indicates different team):
```json
{
  "file": "src/apps/platform/lib/booking_validator.ex",
  "team": "team-spirit",
  "status": "changed",
  "new_team": "team-kraken",
  "confidence": "medium",
  "signals": ["code:validates booking slots and availability"],
  "reason": "Code handles booking validation - Appointments domain owned by Kraken"
}
```

**No signals** (can't verify, keep suggestion):
```json
{
  "file": "src/apps/platform/lib/helpers/string_utils.ex",
  "team": "team-spirit",
  "status": "no_signals",
  "confidence": "low",
  "signals": [],
  "reason": "Generic utility, no domain signals found"
}
```

## Ownership Signals (Priority Order)

### 1. SENTRY CONFIG (Authoritative - always wins)
```elixir
SentryConfig.codeowners("team-xxx")
```
If found, this OVERRIDES the suggestion. Use this team.

### 2. AREAS NAMESPACE
```elixir
defmodule Areas.Sales.Calculator do
defmodule Areas.Payments.Gateway do
```
Map:
- `Areas.Sales` / `Areas.Orders` -> team-spirit
- `Areas.Payments` -> team-pierogi
- `Areas.GiftCards` -> team-apollo
- `Areas.Memberships` -> team-apollo
- `Areas.Bookings` / `Areas.Appointments` -> team-kraken
- `Areas.Clients` -> team-janusze
- `Areas.Calendar` / `Areas.Reviews` -> team-zen

### 3. CODE PURPOSE (What does it DO?)

Read the code and understand its purpose:

| Code handles... | Team | Domain |
|-----------------|------|--------|
| Gift cards, vouchers, redemption | team-apollo | Vouchers |
| Packages, memberships, subscriptions | team-apollo | Packages/Memberships |
| Payment processing, refunds, terminals | team-pierogi | Payments |
| Sales, checkout, orders, invoices | team-spirit | Orders |
| Bookings, appointments, rescheduling | team-kraken | Appointments |
| Clients, customers, merging profiles | team-janusze | Clients |
| Employees, staff, team members, roles | team-commando | Team Members |
| Deposits, no-shows, cancellation fees | team-xd | Appointment Protection |
| Marketing campaigns, blasts, deals | team-dealers | Automations/Deals |
| Services, categories, pricing levels | team-mind-the-gap | Catalog |
| Reviews, ratings, feedback | team-zen | Post Purchase |
| Forms, consultations | team-janusze | Consultation Forms |
| Notifications, alerts, push messages | team-blaze | Notifications |
| Calendar sync, availability, schedules | team-zen | Calendar |
| Tips, commissions, pay runs | team-commando | Pay Runs |
| Auth, tokens, permissions, login | team-roswell | Identity |

### 4. MODULE/FUNCTION NAMES
Look for domain keywords in the code:
- `GiftCard`, `Voucher`, `Redeem` -> team-apollo
- `Payment`, `Refund`, `Terminal`, `Charge` -> team-pierogi
- `Sale`, `Checkout`, `Order`, `Invoice`, `Receipt` -> team-spirit
- `Booking`, `Appointment`, `Slot`, `Reschedule` -> team-kraken
- `Client`, `Customer`, `Merge` -> team-janusze
- `Employee`, `Staff`, `TeamMember` -> team-commando
- `Deposit`, `NoShow`, `CancellationFee`, `Protection` -> team-xd
- `Campaign`, `Marketing`, `Blast`, `Deal` -> team-dealers

### 5. RPC/PROTO REFERENCES
```elixir
alias Rpc.GiftCards.V1
alias Rpc.Payments.Terminal
```

## Verification Process

For EACH file:
1. Read first 100 lines
2. Look for SentryConfig - if found, use it (highest priority)
3. Check for Areas.* namespace
4. Analyze module names and function names for domain keywords
5. Read the code logic - what domain is it serving?
6. If no clear signals, mark as `no_signals`

## Signal Shorthand

Use in `signals` array:
- `sentry:team-xxx` - SentryConfig found
- `areas:DomainName` - Areas namespace
- `module:Keyword` - Domain keyword in module name
- `rpc:Domain` - RPC reference
- `code:brief description` - Code purpose analysis

## CRITICAL RULES

1. **Read every file** - Never assume from path alone
2. **SentryConfig wins** - Overrides everything else
3. **When uncertain, use no_signals** - Don't guess
4. **Only include new_team when status is changed**
5. **Be specific in reasons** - "handles X which is Y domain" not just "domain match"
