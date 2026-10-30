---
name: verify-webhook-signature
description: Use when a user needs to implement or debug Tyxter webhook HMAC verification, raw-body handling, timestamp checks, or replay protection.
---

# Verify Webhook Signature

Verify against the raw request body. Do not parse and re-stringify JSON before computing the HMAC.

## Docs

- Webhooks: https://tyxter.com/docs/webhooks
- Webhook endpoints API: https://tyxter.com/docs/api-reference/webhook-endpoints
- Errors: https://tyxter.com/docs/errors

## Required env vars

- `TYXTER_WEBHOOK_SECRET`: endpoint signing secret. Use placeholders in examples; never commit a real value.
- `TYXTER_WEBHOOK_ID`: expected `tyxter-webhook-id` header when replay checking.
- `TYXTER_WEBHOOK_TIMESTAMP`: expected `tyxter-webhook-timestamp` header.
- `TYXTER_WEBHOOK_SIGNATURE`: expected `tyxter-webhook-signature` header.

## Registered endpoint readiness

For an already registered public HTTPS endpoint, prefer the canonical empty
`POST /v1/webhook-endpoints/{id}/test` request with an `Idempotency-Key` to
exercise one signed worker delivery. Store its `webhook_event_id`, then inspect
`GET /v1/webhook-events/{id}` for terminal status and first-attempt evidence.
This probe ignores subscriptions, is limited to five requests per endpoint per
minute (including idempotent replays), and each failure is terminal after one
attempt while normal endpoint breaker accounting still applies. A disabled
endpoint returns `409 webhook_endpoint_disabled`: repair the receiver and PATCH
it to `status: active` before making a fresh probe. Do not resend
`webhook.test`; use this route again when a new rate-limited probe is needed.

Use the CLI listener instead for local/container-forwarded sandbox testing: the
registered-endpoint probe cannot replace that workflow.

## Workflow

1. Read the raw request body bytes before JSON parsing.
2. Reject missing signature headers.
3. Reject timestamps outside a five minute tolerance.
4. Compute `HMAC-SHA256(secret, timestamp + "." + rawBody)`.
5. Compare signatures using constant-time comparison.
6. Store seen `tyxter-webhook-id` values for the replay window and reject duplicates.
7. Return any `2xx` only after verification and durable handling succeed.

## Local verification snippet

```bash
node - <<'NODE'
const crypto = require('crypto');

// Real Tyxter signing secrets are 64-char hex (no prefix), returned once by
// create / rotate-signing-secret. The fallback below is a local placeholder.
const secret =
  process.env.TYXTER_WEBHOOK_SECRET ||
  '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef';
const timestamp = process.env.TYXTER_WEBHOOK_TIMESTAMP || '1700000000';
const rawBody = '{"type":"message.delivered","data":{"message_id":"msg_test"}}';

const signature = crypto
  .createHmac('sha256', secret)
  .update(`${timestamp}.${rawBody}`)
  .digest('hex');

console.log(`tyxter-webhook-signature: ${signature}`);
NODE
```

## Completion criteria

- Tests cover valid signature, wrong signature, stale timestamp, missing headers, and replayed webhook id.
- The implementation uses raw body bytes and constant-time comparison.
- No real webhook secret, API key, or customer payload is written to docs, tests, logs, or commits.
