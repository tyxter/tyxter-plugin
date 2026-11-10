---
name: send-sandbox-message
description: Use when a user needs a first Tyxter sandbox send, wants to validate Quickstart, or needs to inspect test-message delivery.
---

# Send Sandbox Message

Use the public `/v1/messages` API only. Do not use dashboard BFF routes or automate the dashboard.

## Docs

- Quickstart: https://tyxter.com/docs/quickstart
- Sandbox: https://tyxter.com/docs/sandbox
- Messages API: https://tyxter.com/docs/api-reference/messages

## Required env vars

- `TYXTER_API_BASE_URL`: default to `https://api.tyxter.com`; set `http://localhost:3001` explicitly for a local stack.
- `TYXTER_SANDBOX_API_KEY`: sandbox key only. The seeded local placeholder is `tx_sandbox_localSandboxKey000000000001`.
- `TYXTER_TEST_TO`: recipient phone in E.164 format. Use a sandbox-safe value unless the user provides another test number.

## Workflow

1. Confirm the target is sandbox by checking the key starts with `tx_sandbox_`.
2. Read `sender.default_sender_id` from `GET /v1/sandbox/quickstart`; it is the `sender.id` of the send. Each new sandbox environment comes with one simulated sender, at signup and when you create a project. It is created in the same transaction and is active when signup or project creation returns. Read `GET /v1/sandbox/quickstart` once for `sender.default_sender_id`. The sender appears in `GET /v1/phone-numbers` as a connected number (`source: "byon"`, `status: "active"`), with a reserved, non-assignable phone number that cannot be dialed. Quickstart selects the oldest active, unreleased sender. An older environment may need a sender added manually. If the environment has no active sender (for example, an older environment where nobody added one, or one whose sender was removed or released, or moved to another environment), quickstart returns null: ask a person to provision one in the dashboard or use a non-agent key with `phone_numbers:write`. Agent keys cannot hold that write scope. Production environments get no automatic sender. Send only with a non-null sender and `capabilities.send_outbound_messages` true; report a missing sender separately from missing scopes.
3. Open the 24-hour customer-service window with `POST /v1/sandbox/inbound-messages` from the test recipient. Free-form text is accepted only inside that window.
4. Send `POST /v1/messages` with `channel`, `sender`, `recipient` and `message`, plus an `Idempotency-Key`. Reuse the same key only when retrying the same logical send.
5. Capture the returned `message_id`, `trace_id`, and initial `status`.
6. Poll `GET /v1/messages/{id}` until the sandbox timeline reaches a terminal or observable delivery state.
7. If webhook validation is requested, register a webhook endpoint first and correlate events by `message_id` or `trace_id`.

## API commands

```bash
export TYXTER_API_BASE_URL="${TYXTER_API_BASE_URL:-https://api.tyxter.com}"
: "${TYXTER_SANDBOX_API_KEY:?Load a matching sandbox API key into your environment}"
export TYXTER_TEST_TO="${TYXTER_TEST_TO:-+12025550123}"
export IDEMPOTENCY_KEY="$(node -e "console.log(crypto.randomUUID())")"

# Sender id of the active sandbox number. Read quickstart once as in step 2.
SENDER_ID="$(curl -sS "$TYXTER_API_BASE_URL/v1/sandbox/quickstart" \
  -H "Authorization: Bearer $TYXTER_SANDBOX_API_KEY" |
  node -e 'let s="";process.stdin.on("data",(d)=>(s+=d)).on("end",()=>{
    const ready=JSON.parse(s);
    if(ready.error) throw new Error(ready.error.code+": "+ready.error.message);
    const sender=ready.sender.default_sender_id;
    if(!sender) throw new Error("Sandbox has no active sender. Ask a person to provision one in the dashboard or use a non-agent key with phone_numbers:write.");
    if(!ready.capabilities.send_outbound_messages) throw new Error("Sandbox cannot send; missing scopes: "+ready.missing_scopes.join(", "));
    console.log(sender);
  })')"
: "${SENDER_ID:?Quickstart returned no active sender; see the message above}"

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
