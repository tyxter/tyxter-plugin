---
name: create-template
description: Create and submit Tyxter WhatsApp templates through the public API. Use when a user asks to draft a template, call template CRUD endpoints, estimate template cost, submit for approval, duplicate a template, or validate template-send readiness.
---

# Create Template

Use public template endpoints. Do not create templates through dashboard-only control-plane routes.

## Docs

- Templates: https://tyxter.com/docs/templates
- Templates API: https://tyxter.com/docs/api-reference/templates
- Messages API: https://tyxter.com/docs/api-reference/messages

## Required env vars

- `TYXTER_API_BASE_URL`: default to `http://localhost:3001` locally.
- `TYXTER_SANDBOX_API_KEY`: sandbox key for local testing.
- `TYXTER_TEMPLATE_NAME`: lowercase template name such as `order_update_demo`.
- `TYXTER_TEMPLATE_LANGUAGE`: default to `en_US` unless the user specifies another locale.

## Workflow

1. Confirm whether the target environment is sandbox or production.
2. Draft a template name, category, language, body, and variables.
3. Call `POST /v1/templates` with an `Idempotency-Key`.
4. Capture the returned template id and current approval status.
5. If requested, call `POST /v1/templates/{id}/estimate-cost`.
6. Submit only when the user explicitly asks for approval submission.
7. Send a template message only after the template is approved or sandbox-approved.

## Local stack commands

```bash
export TYXTER_API_BASE_URL="${TYXTER_API_BASE_URL:-http://localhost:3001}"
export TYXTER_SANDBOX_API_KEY="${TYXTER_SANDBOX_API_KEY:-tx_sandbox_localSandboxKey000000000001}"
export TYXTER_TEMPLATE_NAME="${TYXTER_TEMPLATE_NAME:-order_update_demo}"
export TYXTER_TEMPLATE_LANGUAGE="${TYXTER_TEMPLATE_LANGUAGE:-en_US}"
export IDEMPOTENCY_KEY="$(node -e "console.log(crypto.randomUUID())")"

curl -sS -X POST "$TYXTER_API_BASE_URL/v1/templates" \
  -H "Authorization: Bearer $TYXTER_SANDBOX_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -d '{
    "name": "'"$TYXTER_TEMPLATE_NAME"'",
    "language": "'"$TYXTER_TEMPLATE_LANGUAGE"'",
    "category": "utility",
    "components": [
      {
        "type": "BODY",
        "text": "Your order {{1}} is ready for pickup.",
        "example": { "body_text": [["ORD-123"]] }
      }
    ]
  }'
```

## Completion criteria

- Template creation returns a template id.
- Follow-up actions use that id and keep idempotency keys scoped to one logical mutation.
- Production approval submission is not performed without an explicit user request.
