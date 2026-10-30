---
name: inspect-billing-usage
description: Use when a user needs to reconcile Tyxter usage, investigate charges or billing blocks, or inspect balances, ledger entries, and invoices.
---

# Inspect Billing Usage

Use read-only public billing and usage endpoints first. Top-ups, saved payment methods, and spend-limit changes are dashboard workflows.

## Docs

- Billing: https://tyxter.com/docs/billing
- Billing API: https://tyxter.com/docs/api-reference/billing
- Usage API: https://tyxter.com/docs/api-reference/usage
- Errors: https://tyxter.com/docs/errors

## Required env vars

- `TYXTER_API_BASE_URL`: default to `https://api.tyxter.com`; set `http://localhost:3001` explicitly for a local stack.
- `TYXTER_API_KEY`: sandbox or live key for the environment being inspected.
- `TYXTER_USAGE_FROM`: required ISO 8601 instant with an offset for the usage window.
- `TYXTER_USAGE_TO`: required ISO 8601 instant with an offset for the usage window.

## Workflow

1. Read `GET /v1/billing/balance` and record available BRL credit.
2. Read `GET /v1/rate-cards/current` to understand current pricing inputs.
3. Read `GET /v1/usage` with the requested date range and dimensions: `period_start` and `period_end` are required ISO 8601 instants with an offset (for example `2026-10-01T00:00:00Z`); `group_by` is optional, one of `destination_country`, `template_id`, `meta_pass_through_fee`, `tyxter_markup` or `package_consumption`.
4. Read `GET /v1/billing/ledger` for reconciliation when balance or charges are disputed. An approved phone rental holds its first month in `held_brl` on the balance, with no ledger line until the carrier delivers the number.
5. Read `GET /v1/invoices` and `GET /v1/invoices/{id}/download` only when invoice context is needed.
6. If delivery is blocked, check for production credit exhaustion and connect the result to the message trace or API error.

## API commands

```bash
export TYXTER_API_BASE_URL="${TYXTER_API_BASE_URL:-https://api.tyxter.com}"
: "${TYXTER_API_KEY:?Load a matching API key into your environment}"

curl -sS "$TYXTER_API_BASE_URL/v1/billing/balance" \
  -H "Authorization: Bearer $TYXTER_API_KEY"

: "${TYXTER_USAGE_FROM:?Set the usage window start, for example 2026-10-01T00:00:00Z}"
: "${TYXTER_USAGE_TO:?Set the usage window end, for example 2026-11-01T00:00:00Z}"
curl -sS --get "$TYXTER_API_BASE_URL/v1/usage" \
  -H "Authorization: Bearer $TYXTER_API_KEY" \
  --data-urlencode "period_start=$TYXTER_USAGE_FROM" \
  --data-urlencode "period_end=$TYXTER_USAGE_TO"
```

## Completion criteria

- The answer distinguishes sandbox zero-cost usage from production prepaid BRL usage.
- Billing findings cite balance, usage window, ledger evidence, or invoice id.
- No top-up or payment-method mutation is attempted through public API or dashboard automation.
