---
name: send-sandbox-message
description: Send a Tyxter sandbox WhatsApp message through the public API and verify its status/webhook behavior. Use when a user asks to send a test message, validate Quickstart, exercise sandbox outbound delivery, or debug the first-message developer flow against the local stack.
---

# Send Sandbox Message

Use the public `/v1/messages` API only. Do not use dashboard BFF routes or automate the dashboard.

## Docs

- Quickstart: https://tyxter.com/docs/quickstart
- Sandbox: https://tyxter.com/docs/sandbox
- Messages API: https://tyxter.com/docs/api-reference/messages

## Required env vars

- `TYXTER_API_BASE_URL`: default to `http://localhost:3001` for the local stack.
- `TYXTER_SANDBOX_API_KEY`: sandbox key only. The seeded local placeholder is `tx_sandbox_localSandboxKey000000000001`.
- `TYXTER_TEST_TO`: recipient phone in E.164 format. Use a sandbox-safe value unless the user provides another test number.

## Workflow

1. Confirm the target is sandbox by checking the key starts with `tx_sandbox_`.
2. Read `sender.default_sender_id` from `GET /v1/sandbox/quickstart`; it is the `sender.id` of the send.
3. Open the 24-hour customer-service window with `POST /v1/sandbox/inbound-messages` from the test recipient. Free-form text is accepted only inside that window.
4. Send `POST /v1/messages` with `channel`, `sender`, `recipient` and `message`, plus an `Idempotency-Key`. Reuse the same key only when retrying the same logical send.
5. Capture the returned `message_id`, `trace_id`, and initial `status`.
6. Poll `GET /v1/messages/{id}` until the sandbox timeline reaches a terminal or observable delivery state.
7. If webhook validation is requested, register a webhook endpoint first and correlate events by `message_id` or `trace_id`.

## Local stack commands

```bash
export TYXTER_API_BASE_URL="${TYXTER_API_BASE_URL:-http://localhost:3001}"
export TYXTER_SANDBOX_API_KEY="${TYXTER_SANDBOX_API_KEY:-tx_sandbox_localSandboxKey000000000001}"
export TYXTER_TEST_TO="${TYXTER_TEST_TO:-+12025550123}"
export IDEMPOTENCY_KEY="$(node -e "console.log(crypto.randomUUID())")"

# Sender id of the sandbox number.
SENDER_ID="$(curl -sS "$TYXTER_API_BASE_URL/v1/sandbox/quickstart" \
  -H "Authorization: Bearer $TYXTER_SANDBOX_API_KEY" |
  node -e 'let s="";process.stdin.on("data",(d)=>(s+=d)).on("end",()=>console.log(JSON.parse(s).sender.default_sender_id))')"

# Open the customer-service window with a simulated inbound message.
curl -sS -X POST "$TYXTER_API_BASE_URL/v1/sandbox/inbound-messages" \
  -H "Authorization: Bearer $TYXTER_SANDBOX_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY-window" \
  -d '{
    "from": "'"$TYXTER_TEST_TO"'",
    "to": "'"$SENDER_ID"'",
    "type": "text",
    "text": { "body": "Opening the sandbox service window." }
  }'

curl -sS -X POST "$TYXTER_API_BASE_URL/v1/messages" \
  -H "Authorization: Bearer $TYXTER_SANDBOX_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -d '{
    "channel": "whatsapp",
    "sender": { "type": "whatsapp_phone_number", "id": "'"$SENDER_ID"'" },
    "recipient": { "type": "phone_e164", "id": "'"$TYXTER_TEST_TO"'" },
    "message": { "type": "text", "text": { "body": "Tyxter sandbox smoke test" } },
    "metadata": { "sandbox_scenario": "delivery_success" }
  }'
```

## Completion criteria

- The send returns `202` with a message id.
- Retrieval by id returns the same message and a sandbox status progression.
- No response or docs output includes `tx_live_`, dashboard session tokens, webhook secrets, or customer data.
