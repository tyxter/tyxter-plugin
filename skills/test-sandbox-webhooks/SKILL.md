---
name: test-sandbox-webhooks
description: Use when a user needs to test Tyxter sandbox webhooks against a local app, run the CLI listener, or generate a reusable Docker Compose setup.
---

# Test Sandbox Webhooks

Use Tyxter CLI as the customer would: a sandbox API key, a local app webhook
URL, and signed forwarded events. Do not ask the user to register a normal
dashboard webhook endpoint for this local sandbox flow.

Canonical CLI repo: `https://github.com/tyxter-dev/tyxter-cli`.
Published image: `ghcr.io/tyxter-dev/tyxter-cli:latest`.

## Registered HTTPS endpoint versus local listener

For an already registered public HTTPS endpoint, the preferred receiver-readiness
probe is the empty, idempotent `POST /v1/webhook-endpoints/{id}/test` request.
It stores one signed `webhook.test` delivery; retain `webhook_event_id` and read
`GET /v1/webhook-events/{id}` for the terminal result and first-attempt evidence.
The route is endpoint-scoped at five requests per minute, ignores subscriptions,
and never retries a failed test. Repair and PATCH a disabled endpoint to
`status: active` before making a fresh probe.

This does not replace the CLI workflow below. Use the CLI when the app is local
or container-bound, when it needs localhost forwarding, or when the objective is
to validate the sandbox listener itself. That flow needs no normal dashboard
webhook endpoint.

## Safety Rules

- Use sandbox keys only. Stop if the key starts with `tx_live_`.
- Never commit API keys, webhook secrets, dashboard cookies, or received payloads.
- Prefer env files named like `.env.tyxter-cli`; add only `.example` files to git.
- Treat `TYXTER_WEBHOOK_SECRET` as a local test secret shared by the CLI and the app verifier.

## Workflow

1. Identify the app under test.
   - Find the dev command, package manager, port, and webhook route.
   - Find the webhook secret env var, raw-body handling, and event-type dispatch.
   - If any of these cannot be inferred safely, ask one concise question.

2. Choose the CLI mode.
   - Pull image: use `ghcr.io/tyxter-dev/tyxter-cli:latest`.
   - Build source: clone `https://github.com/tyxter-dev/tyxter-cli` and use its
     `compose.yaml` or `compose.image.yaml`.
   - If the customer app repo has no compose file and the user wants reusable setup, run the
     bundled script from this skill's `scripts/` directory:

     ```bash
     python3 "${CLAUDE_SKILL_DIR}/scripts/write_listener_compose.py" \
       --app-port 3000 \
       --webhook-path /webhooks/tyxter
     ```

     Claude Code expands `${CLAUDE_SKILL_DIR}` to this skill's installed directory.
     In Codex, use the absolute directory containing the loaded `SKILL.md` instead.
     In a Messaging checkout it is `plugin/skills/test-sandbox-webhooks`; in a plugin
     checkout it is `skills/test-sandbox-webhooks`. An API-served `SKILL.md` has no
     bundled script: use a plugin or repository checkout for this setup.

     Then copy `.env.tyxter-cli.example` to `.env.tyxter-cli` and set the sandbox key.

3. Start the app with a known local signing secret.
   - Prefer
     `TYXTER_WEBHOOK_SECRET=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`
     for repeatable tests (real signing secrets are 64-char hex, no prefix).
   - The CLI and app must use the same value.
   - For a Docker CLI calling a host app, set:
     `TYXTER_WEBHOOK_FORWARD_URL=http://host.docker.internal:<port><path>`.

4. Start the listener.

   ```bash
   docker compose up -d
   ```

   For a source build:

   ```bash
   docker compose -f compose.yaml up -d --build
   ```

5. Run preflight checks.

   ```bash
   docker compose run --rm tyxter-cli status
   docker compose run --rm tyxter-cli doctor
   ```

   If `doctor` fails only because the app rejects the diagnostic event type,
   note that clearly and continue with a real sandbox event.

6. Fire a real sandbox webhook.

   ```bash
   docker compose run --rm tyxter-cli simulate inbound \
     --from +15551230000 \
     --to +15557650000 \
     --body "Tyxter sandbox webhook smoke"
   ```

   Use `tour` instead when you need to checkpoint old events before creating
   the test event.

7. Verify evidence from both sides.
   - CLI: `docker compose logs --tail=80 tyxter-cli`.
   - App: route logs, test assertion, database row, queue job, or UI state.
   - Correlate by `message_id`, `trace_id`, and webhook id.
   - Confirm the app returned `2xx` only after signature verification and durable handling.

8. Make it reusable when asked to "set up tests".
   - Add a script such as `scripts/tyxter-sandbox-webhook-smoke`.
   - Add a package script or CI job only if the repo already uses that pattern.
   - Keep required env vars explicit: `TYXTER_API_KEY`, `TYXTER_WEBHOOK_FORWARD_URL`, `TYXTER_WEBHOOK_SECRET`.
   - Do not bake customer-specific phone numbers, API keys, or secrets into committed files.

## Completion Criteria

- The app is running and reachable by the CLI container.
- `status` prints a persisted local signing secret and cursor.
- `doctor` passes, or any diagnostic-only failure is explained and a real event succeeds.
- A sandbox event is created and forwarded to the app.
- The final report includes exact commands run, event identifiers, verification evidence, and any files changed.
