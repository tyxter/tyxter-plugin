---
name: debug-failed-delivery
description: Use when a Tyxter WhatsApp message fails, stalls, disappears, or needs investigation through status, traces, and webhook attempts.
---

# Debug Failed Delivery

Start with public read APIs and trace evidence. Do not inspect dashboard BFF routes unless the user specifically asks to debug dashboard code.

## Docs

- Messages API: https://tyxter.com/docs/api-reference/messages
- Sandbox: https://tyxter.com/docs/sandbox
- Webhooks: https://tyxter.com/docs/webhooks
- Errors: https://tyxter.com/docs/errors

## Required env vars

- `TYXTER_API_BASE_URL`: default to `https://api.tyxter.com`; set `http://localhost:3001` explicitly for a local stack.
- `TYXTER_API_KEY`: sandbox or production key for the environment being investigated.
- `TYXTER_MESSAGE_ID`: message id to inspect.
- `TYXTER_TRACE_ID`: optional trace id from API response or logs.

## Workflow

1. Retrieve `GET /v1/messages/{id}` and record `status`, `trace_id`, recipient, message type, provider error, and timeline entries.
2. If the message is sandbox, check `metadata.sandbox_scenario` and expected deterministic outcome.
3. If the message is production, confirm key prefix and environment match. Sandbox keys must not target production and live keys must not target sandbox.
4. Inspect webhook event delivery with `GET /v1/webhook-events` and correlate by `message_id` or `trace_id`.
5. Classify the failure as validation, idempotency conflict, opt-out/consent block, provider rejection, billing hard-block, worker retry, webhook delivery, or unknown.
6. Recommend the next action based on class: fix request shape, retry with same idempotency key, opt contact in, top up balance, resend webhook event, or escalate with trace evidence.

## API commands

```bash
export TYXTER_API_BASE_URL="${TYXTER_API_BASE_URL:-https://api.tyxter.com}"
: "${TYXTER_API_KEY:?Load a matching API key into your environment}"

curl -sS "$TYXTER_API_BASE_URL/v1/messages/$TYXTER_MESSAGE_ID" \
  -H "Authorization: Bearer $TYXTER_API_KEY"
```

## Completion criteria

- The investigation names a concrete failure class or states what evidence is missing.
- The answer includes the message id, trace id when available, and the next retry/escalation step.
- Logs and summaries redact phone numbers, API keys, webhook secrets, and customer message bodies unless the user explicitly provided them for debugging.
