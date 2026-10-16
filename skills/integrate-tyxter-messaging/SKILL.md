---
name: integrate-tyxter-messaging
description: Integrate Tyxter Messaging into an existing repository by installing the official JavaScript/TypeScript SDK, obtaining a human-approved sandbox API key, proving a first send, adding verified webhooks, handling stable errors and idempotency, and promoting to production only as a separate action.
---

# Integrate Tyxter Messaging

Work inside the customer's repository. Leave it with a tested sandbox
integration and a verified webhook boundary. Do not start with production and
do not put credentials in source code, command history, logs, or committed
files.

## 1. Inspect the repository and install the SDK

1. Find the application package that will own messaging, its runtime, server
   framework, existing environment-file convention, and package manager.
2. Select the package manager from the repository's `packageManager` field or
   lockfile. Do not create a second lockfile.
3. Install `tyxter` in that application package:

       pnpm add tyxter
       npm install tyxter
       yarn add tyxter
       bun add tyxter

   Run only the command that matches the repository. If the repository has no
   JavaScript/TypeScript runtime, ask before adding a Node 20+ integration
   package instead of silently introducing another ecosystem.

## 2. Obtain a sandbox key through device authorization

Use the SDK's unauthenticated `TyxterBootstrap` client. The following is the
complete SDK shape for `POST /v1/agent-api-key-device-authorizations` and its
`POST /v1/agent-api-key-device-authorizations/token` poll. Adapt the
surrounding file/module style, but do not change the request fields or requested
sandbox scopes:

    import { TyxterApiError, TyxterBootstrap } from 'tyxter';

    const bootstrap = new TyxterBootstrap(
      process.env.TYXTER_API_BASE_URL
        ? { baseUrl: process.env.TYXTER_API_BASE_URL }
        : {},
    );
    const authorization =
      await bootstrap.agentApiKeyDeviceAuthorizations.create({
        client_name: 'Messaging integration for <repository-name>',
        environment: "sandbox",
        scopes: [
          'sandbox:write',
          'messages:send',
          'messages:read',
          'webhooks:write',
          'webhooks:read',
        ],
      });

    // Show only this approval URL to the human. Never print a returned secret.
    console.info(authorization.verification_uri_complete);

    const deadline = Date.now() + authorization.expires_in * 1_000;
    let intervalSeconds = authorization.interval;
    let approvedSecret: string | undefined;

    while (Date.now() < deadline) {
      await new Promise((resolve) =>
        setTimeout(resolve, intervalSeconds * 1_000),
      );
      try {
        const token =
          await bootstrap.agentApiKeyDeviceAuthorizations.token({
            grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
            device_code: authorization.device_code,
          });
        if (token.status === 'pending') {
          intervalSeconds = Math.max(intervalSeconds, token.interval);
          continue;
        }
        approvedSecret = token.api_key.secret;
        break;
      } catch (error) {
        if (
          error instanceof TyxterApiError &&
          (error.code === 'device_code_expired' ||
            error.code === 'authorization_denied')
        ) {
          throw new Error(`Tyxter device authorization stopped: ${error.code}`);
        }
        throw error;
      }
    }

    if (!approvedSecret || !approvedSecret.startsWith('tx_sandbox_')) {
      throw new Error('A tx_sandbox_ key is required.');
    }

HTTP 202 is returned by the token endpoint as the typed
`status: "pending"` result above. Never poll faster than the latest
`interval`. The example fails closed on transport and 429 errors; restart the
device authorization instead of guessing a retry delay. Stop on
`device_code_expired` or `authorization_denied`, and never fall back to asking
the human to paste a live key.

After approval, take `api_key.secret` from the one-time approved response. It
must start with `tx_sandbox_`; otherwise stop and request a new sandbox
authorization.

Store the secret as `TYXTER_API_KEY` using the repository's existing local
secret convention. Ensure the real env file is ignored. Add only blank
`TYXTER_API_KEY=`, `TYXTER_TEST_RECIPIENT=`, and
`TYXTER_WEBHOOK_SECRET=` placeholders to the repository's example env file,
and never inline the key. Use `https://api.tyxter.com` as the default API base
unless the repository already has an explicit `TYXTER_API_BASE_URL` override.

## 3. Prove the first sandbox send

Put the following proof in a repository-appropriate script or focused test.
`TYXTER_TEST_RECIPIENT` must be a human-approved E.164 number such as
`+5511999999999`; do not invent or contact an unapproved number.
The calls map to `GET /v1/sandbox/quickstart`,
`POST /v1/sandbox/inbound-messages`, and `POST /v1/messages` in that order.

    import { randomUUID } from 'node:crypto';
    import { Tyxter } from 'tyxter';

    function requiredEnv(name: string): string {
      const value = process.env[name];
      if (!value) throw new Error(`Missing ${name}`);
      return value;
    }

    const apiKey = requiredEnv('TYXTER_API_KEY');
    if (!apiKey.startsWith('tx_sandbox_')) {
      throw new Error('The first-send proof requires a tx_sandbox_ key.');
    }
    const testRecipient = requiredEnv('TYXTER_TEST_RECIPIENT');
    if (!/^\+[1-9]\d{7,14}$/.test(testRecipient)) {
      throw new Error('TYXTER_TEST_RECIPIENT must be E.164.');
    }

    const tyxter = new Tyxter({
      apiKey,
      ...(process.env.TYXTER_API_BASE_URL
        ? { baseUrl: process.env.TYXTER_API_BASE_URL }
        : {}),
    });
    const quickstart = await tyxter.sandbox.quickstart();
    const sender = quickstart.sender.default_sender_id;
    if (!sender || !quickstart.capabilities.send_outbound_messages) {
      throw new Error(
        `Sandbox is not send-ready; missing scopes: ${quickstart.missing_scopes.join(', ')}`,
      );
    }

    await tyxter.sandbox.inboundMessages.create(
      {
        channel: 'whatsapp',
        from: testRecipient,
        to: sender,
        type: 'text',
        text: { body: 'Opening the Tyxter sandbox service window.' },
      },
      { idempotencyKey: randomUUID() },
    );

    const outbound = await tyxter.whatsapp.sendText(
      {
        from: sender,
        to: testRecipient,
        body: 'Tyxter sandbox integration check.',
      },
      { idempotencyKey: randomUUID() },
    );
    if (outbound.status !== 'accepted') {
      throw new Error(`Unexpected create status: ${outbound.status}`);
    }
    const detail = await tyxter.messages.retrieve(outbound.id);
    console.info({
      message_id: outbound.id,
      trace_id: outbound.trace_id,
      status: detail.status,
    });

The simulated inbound opens WhatsApp's service window before the free-form
text send. Each write receives a distinct `randomUUID()`; save and reuse that
same value only when retrying the same logical write. The `POST /v1/messages`
response must be `accepted`. A later retrieve may already have advanced to
`sent` or `delivered`; `failed` is a failed proof. Sandbox success does not
require a live Meta connection or billing.

## 4. Add a verified webhook receiver

Locate the repository's existing HTTP server and add a webhook route using its
normal routing conventions. Enable that framework's raw-body option before any
JSON parser, scoped to this route when the framework supports it. The SDK
verifier accepts the exact UTF-8 request body as a string:

    import { verifyWebhookSignature } from 'tyxter/webhook-verifier';

    type HeaderValue = string | string[] | undefined;

    function oneHeader(value: HeaderValue): string | undefined {
      return Array.isArray(value) ? value[0] : value;
    }

    function acceptTyxterWebhook(input: {
      headers: Record<string, HeaderValue>;
      rawBody: Buffer;
      secret: string;
    }) {
      const webhookId = oneHeader(input.headers['tyxter-webhook-id']);
      const timestamp = oneHeader(input.headers['tyxter-webhook-timestamp']);
      const signature = oneHeader(input.headers['tyxter-webhook-signature']);
      if (!webhookId || !timestamp || !signature) {
        return { status: 400 as const };
      }
      const rawBody = input.rawBody.toString('utf8');
      const valid = verifyWebhookSignature({
        secret: input.secret,
        timestamp,
        signature,
        rawBody,
      });
      if (!valid) return { status: 401 as const };
      return {
        status: 200 as const,
        webhookId,
        event: JSON.parse(rawBody) as unknown,
      };
    }

Normalize the framework's header keys to lowercase before this adapter. Reject
missing or invalid signatures before parsing. After verification, insert
`tyxter-webhook-id` into the repository's durable store with a unique
constraint or equivalent atomic insert-if-absent, enqueue or persist the event,
and return a 2xx quickly. If the repository has no durable store, surface that
design decision instead of silently using process memory. Do not hand-roll HMAC
logic and do not verify a parsed or re-serialized JSON body.

When the receiver has a human-approved public HTTPS URL, register the minimum
sandbox subscription through `POST /v1/webhook-endpoints` with the exact SDK
shape below. Add further published event types only when the application handles
them:

    const endpoint = await tyxter.webhookEndpoints.create(
      {
        url: approvedPublicHttpsUrl,
        description: 'Sandbox integration receiver',
        subscribed_events: ['message.received'],
      },
      { idempotencyKey: randomUUID() },
    );

Store the one-time `endpoint.signing_secret` as `TYXTER_WEBHOOK_SECRET` in
the ignored secret store. Restart the receiver so it validates that both env
values are present at startup. Trigger a new
`tyxter.sandbox.inboundMessages.create` call using the complete request shape
from step 3 and confirm the registered receiver returns 2xx.

For the tamper proof, capture that genuine sandbox request's raw body and three
headers only in memory in a test/diagnostic run. Replay them immediately through
the handler and require 2xx; change one byte of the body while keeping the same
headers and require 401. Do not commit the capture, secret, or test phone data.
If no public HTTPS URL has been approved, finish the receiver and focused local
tests but report endpoint registration as pending; do not invent or publish a
tunnel.

## 5. Handle the public contract explicitly

- Supply an idempotency key on every SDK write that accepts one. Reuse it only
  for retries of the same logical operation.
- Catch `TyxterApiError` from `tyxter` and branch on its
  stable `code`, never on its human `message`. A safe boundary is
  `error instanceof TyxterApiError`; log only `code`, `requestId`, and
  `traceId`, then apply repository-specific recovery for known codes and
  rethrow unknown ones. Never log credentials, signing secrets, or webhook
  bodies.
- Keep sandbox and production configuration separate. Do not make behavior
  depend on guessed IDs or undocumented routes.
- Run the repository's focused tests, typecheck, and lint for the files changed
  by the integration.

## 6. Promote only as a separate, deliberate action

Do not replace the sandbox key as part of the first-send task. After the human
confirms the sandbox send and webhook proof, start a new device authorization
with `environment: "production"`. The approved key must start with
`tx_live_`.

Before switching a production deployment, use `GET /v1/account`,
`GET /v1/provider-connections/status`, `GET /v1/phone-numbers`, and
`GET /v1/templates` to confirm the intended organization/environment, a ready
WhatsApp connection, an active sender, and any approved template the
application needs. Register the production webhook endpoint with the
production key and store its distinct signing secret. Keep the working sandbox
configuration available for deterministic tests.

## Completion checklist

- The repository uses its existing package manager and env convention.
- No real `TYXTER_API_KEY` or `TYXTER_WEBHOOK_SECRET` is committed.
- A `tx_sandbox_` key produced an accepted first message.
- The receiver uses `verifyWebhookSignature` over the raw body and rejects a
  tampered request.
- Writes carry retry-stable idempotency keys and errors branch on
  `TyxterApiError.code`.
- Production remains an explicit human-approved follow-up.
