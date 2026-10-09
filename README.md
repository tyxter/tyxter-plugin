# Tyxter Messaging plugin for Claude

Skills that help Claude work with the Tyxter Messaging API, Tyxter's WhatsApp Business messaging
API, plus a Tyxter MCP server entry that Claude Code connects with your own URL and API key.

The plugin is beta, version `0.1.1`. Skill wording and plugin configuration can change between
releases. This repository is both the plugin and its marketplace: `.claude-plugin/plugin.json`
describes the plugin and `.claude-plugin/marketplace.json` lists it under the `tyxter`
marketplace.

## Skills

The plugin ships eight skills. Each line below quotes the skill's own `description`:

- `/tyxter:create-template`: Create and submit Tyxter WhatsApp templates through the public API. Use when a user asks to draft a template, call template CRUD endpoints, estimate template cost, submit for approval, duplicate a template, or validate template-send readiness.
- `/tyxter:debug-failed-delivery`: Debug failed Tyxter message delivery by inspecting message status, trace IDs, sandbox scenarios, webhook attempts, provider error codes, and retry posture. Use when a user reports failed, stuck, cancelled, bounced, or missing WhatsApp messages.
- `/tyxter:find-developer-tools`: Find and install the official Tyxter Messaging developer tools — the @tyxter/sdk-js TypeScript/JavaScript SDK and the tyxter-cli — and how to authenticate them.
- `/tyxter:inspect-billing-usage`: Inspect Tyxter billing balance, usage, ledger entries, invoices, and rate-card context through public read APIs. Use when a user asks about prepaid credits, usage reconciliation, cost records, billing hard-blocks, invoice downloads, or spend investigation.
- `/tyxter:integrate-tyxter-messaging`: Integrate Tyxter Messaging into an existing repository by installing the official JavaScript/TypeScript SDK, obtaining a human-approved sandbox API key, proving a first send, adding verified webhooks, handling stable errors and idempotency, and promoting to production only as a separate action.
- `/tyxter:send-sandbox-message`: Send a Tyxter sandbox WhatsApp message through the public API and verify its status/webhook behavior. Use when a user asks to send a test message, validate Quickstart, exercise sandbox outbound delivery, or debug the first-message developer flow against the local stack.
- `/tyxter:test-sandbox-webhooks`: Set up and run Tyxter sandbox webhook tests against a customer app using the public Tyxter CLI Docker container. Use when a user asks Codex or Claude Code to test a Tyxter webhook integration, validate local sandbox webhooks, run the CLI listener against their app, create reusable sandbox webhook smoke tests, or debug the CLI + app combo.
- `/tyxter:verify-webhook-signature`: Verify Tyxter webhook signatures and replay protections. Use when a user asks to implement, audit, test, or debug HMAC webhook verification, raw-body handling, timestamp tolerance, replay rejection, or local tunnel webhook delivery.

## Install in Claude Code

Add the marketplace, then install the plugin:

```bash
claude plugin marketplace add tyxter-dev/claude-plugin
claude plugin install tyxter@tyxter
```

The skills appear as `/tyxter:<skill>`, for example `/tyxter:send-sandbox-message`.

To try a local checkout instead, run Claude Code from the checkout with the plugin directory
flag:

```bash
claude --plugin-dir .
```

## Configuration

`.claude-plugin/plugin.json` declares two values that Claude Code asks you for when you enable
the plugin:

- **Tyxter MCP URL** (`TYXTER_MCP_URL`): your Tyxter MCP server URL, shaped
  `https://api.tyxter.com/mcp/p/<project>/<environment>`. Copy it from the Tyxter dashboard
  Connections page, MCP tab.
- **Tyxter API key** (`TYXTER_API_KEY`): sent as a bearer token to that URL. Use a key whose
  prefix matches the URL's environment. The value is declared `sensitive`.

`.mcp.json` uses those two values, and only those values, to configure the `tyxter-messaging`
MCP server. It contains no URL or key of its own.

The skills do not read those two values. They use the environment variables listed in each
`SKILL.md`. `send-sandbox-message`, `create-template`, `debug-failed-delivery`,
`inspect-billing-usage` and `integrate-tyxter-messaging` call the API at `TYXTER_API_BASE_URL`
with `TYXTER_API_KEY` or `TYXTER_SANDBOX_API_KEY`; set them in the shell you start Claude Code
from. When `TYXTER_API_BASE_URL` is unset, the first four fall back to `http://localhost:3001`, a
local Tyxter stack, and to a seeded local placeholder key, while `integrate-tyxter-messaging`
defaults to the hosted API. To point those five skills at the hosted API, set
`TYXTER_API_BASE_URL=https://api.tyxter.com`. `test-sandbox-webhooks` does not use
`TYXTER_API_BASE_URL`: its CLI container reads `TYXTER_API_URL` (default
`https://api.tyxter.com`) and `TYXTER_API_KEY` from `.env.tyxter-cli`, the file its bundled
script's template becomes.

Start with a sandbox key: `send-sandbox-message`, `create-template`, `test-sandbox-webhooks` and
`integrate-tyxter-messaging` expect one. Keep keys in your environment or in the configuration
prompt. Do not paste them into the chat.

## claude.ai and Cowork

The plugin is not listed in Anthropic's plugin directory yet. claude.ai ignores an MCP server
whose URL comes from user configuration, and Cowork ignores one whose configuration value has no
default, which is the case for `TYXTER_MCP_URL`. To reach the Tyxter MCP server from claude.ai
or Cowork, add your MCP URL (`https://api.tyxter.com/mcp/p/<project>/<environment>`) as a custom
connector. claude.ai connects to it over OAuth instead of an API key. See
https://tyxter.com/docs/build-with-ai.

## What data the plugin sends

This plugin runs no service of its own and collects nothing: the skills are instructions that
make Claude call the Tyxter API you configure (`TYXTER_API_BASE_URL` for the curl and SDK
skills, `TYXTER_API_URL` for the CLI container; the hosted API is `https://api.tyxter.com`) with
your API key, sending what you ask it to send, such as recipient numbers and message and template
content, to the Tyxter account that key belongs to, or to a local Tyxter stack when the base URL
points there, and the MCP entry sends the API key you enter as a bearer token to the MCP URL you
enter.

A few skills also reach other places:

- `find-developer-tools` and `integrate-tyxter-messaging` install `@tyxter/sdk-js` from npm, and
  `find-developer-tools` and `test-sandbox-webhooks` use the `ghcr.io/tyxter-dev/tyxter-cli`
  image from GitHub Container Registry. `test-sandbox-webhooks` can instead clone
  `https://github.com/tyxter-dev/tyxter-cli` to build the CLI from source.
- `verify-webhook-signature` computes webhook signatures locally.
- `test-sandbox-webhooks` forwards sandbox events from the CLI container to the app URL you
  set in `TYXTER_WEBHOOK_FORWARD_URL`.

## Bundled script

`test-sandbox-webhooks` bundles `skills/test-sandbox-webhooks/scripts/write_listener_compose.py`.
By default it writes `compose.tyxter-cli.yaml` and `.env.tyxter-cli.example` into the current
directory.
The skill's example command uses the placeholder path `/path/to/test-sandbox-webhooks`; that
folder is `skills/test-sandbox-webhooks` in this plugin.

## Generated skills

`skills/` is generated from Tyxter's source repository by its `claude-plugin:sync` command, and
that repository's `claude-plugin:check` command compares this folder with the source byte for
byte. Do not edit `skills/` here. To report a problem with a skill, open an issue in this
repository.

## License

MIT. See `LICENSE`.
