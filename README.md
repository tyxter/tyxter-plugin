# Tyxter Messaging plugin for Codex and Claude Code

Eight shared skills for the Tyxter Messaging API, Tyxter's WhatsApp Business messaging API.
Claude Code connects to your account through the plugin's MCP prompts; Codex uses a separate
native MCP registration with your own URL and an API key from your environment.

The plugin is beta, version `0.2.0`. Its canonical repository is
[tyxter/tyxter-plugin](https://github.com/tyxter/tyxter-plugin).
Both host manifests describe the same release and skill tree: `.claude-plugin/plugin.json`
and `.codex-plugin/plugin.json`. The catalogs `.claude-plugin/marketplace.json` and
`.agents/plugins/marketplace.json` expose it as `tyxter@tyxter`.

## Skills

The plugin ships eight skills. Each line below quotes the skill's own `description`:

- `/tyxter:create-template`: Create and submit Tyxter WhatsApp templates through the public API. Use when a user asks to draft a template, call template CRUD endpoints, estimate template cost, submit for approval, duplicate a template, or validate template-send readiness.
- `/tyxter:debug-failed-delivery`: Debug failed Tyxter message delivery by inspecting message status, trace IDs, sandbox scenarios, webhook attempts, provider error codes, and retry posture. Use when a user reports failed, stuck, cancelled, bounced, or missing WhatsApp messages.
- `/tyxter:find-developer-tools`: Find and install the official Tyxter Messaging developer tools — the tyxter TypeScript/JavaScript SDK and the tyxter-cli — and how to authenticate them.
- `/tyxter:inspect-billing-usage`: Inspect Tyxter billing balance, usage, ledger entries, invoices, and rate-card context through public read APIs. Use when a user asks about prepaid credits, usage reconciliation, cost records, billing hard-blocks, invoice downloads, or spend investigation.
- `/tyxter:integrate-tyxter-messaging`: Integrate Tyxter Messaging into an existing repository by installing the official JavaScript/TypeScript SDK, obtaining a human-approved sandbox API key, proving a first send, adding verified webhooks, handling stable errors and idempotency, and promoting to production only as a separate action.
- `/tyxter:send-sandbox-message`: Send a Tyxter sandbox WhatsApp message through the public API and verify its status/webhook behavior. Use when a user asks to send a test message, validate Quickstart, exercise sandbox outbound delivery, or debug the first-message developer flow against the local stack.
- `/tyxter:test-sandbox-webhooks`: Set up and run Tyxter sandbox webhook tests against a customer app using the public Tyxter CLI Docker container. Use when a user asks Codex or Claude Code to test a Tyxter webhook integration, validate local sandbox webhooks, run the CLI listener against their app, create reusable sandbox webhook smoke tests, or debug the CLI + app combo.
- `/tyxter:verify-webhook-signature`: Verify Tyxter webhook signatures and replay protections. Use when a user asks to implement, audit, test, or debug HMAC webhook verification, raw-body handling, timestamp tolerance, replay rejection, or local tunnel webhook delivery.

## Install in Codex

With a Codex CLI supporting plugin commands:

```bash
codex plugin marketplace add tyxter/tyxter-plugin
codex plugin add tyxter@tyxter
codex plugin list --marketplace tyxter
```

For a local checkout, run `codex plugin marketplace add .` from the repository root, then
`codex plugin add tyxter@tyxter`. Start a new Codex session and request a skill such as
`$integrate-tyxter-messaging`. Both hosts load the same `skills/` directory.

The Codex manifest deliberately declares an empty `mcpServers` object. Installing the plugin
adds skills; it does not register an account MCP connection or consume Claude's configuration.
Copy your exact project/environment MCP URL from the Tyxter dashboard Connections page, MCP tab.
Export `TYXTER_MCP_URL` and a matching `TYXTER_API_KEY` in your shell using your normal secret
management, then register the URL with Codex:

```bash
: "${TYXTER_MCP_URL:?Set your account MCP URL from the dashboard}"
: "${TYXTER_API_KEY:?Load your matching API key into the shell environment}"
codex mcp add tyxter-messaging --url "$TYXTER_MCP_URL" --bearer-token-env-var TYXTER_API_KEY
codex mcp get tyxter-messaging --json
```

The shell expands the URL when you register it. Codex stores that URL and the variable name
`TYXTER_API_KEY`, not the key value. Keep the key exported in the environment that launches
Codex; restart an existing host/session with that environment after changing it. Re-register
the server when you select a different project/environment URL. Inspect any existing
`tyxter-messaging` registration before replacing it.

`codex mcp get` and plugin listings verify configuration and installation. They do not establish
an authenticated connection, a successful Tyxter tool call, or approval in a public plugin
directory. Confirm account access through the host's MCP tools after setup.
For the compatibility packaging layout, see [OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins).

## Install in Claude Code

Add the marketplace, then install the plugin:

```bash
claude plugin marketplace add tyxter/tyxter-plugin
claude plugin install tyxter@tyxter
```

The skills appear as `/tyxter:<skill>`, for example `/tyxter:send-sandbox-message`.

To try a local checkout instead, run Claude Code from the checkout with the plugin directory
flag:

```bash
claude --plugin-dir .
```

## Claude Code configuration

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
with `TYXTER_API_KEY` or `TYXTER_SANDBOX_API_KEY`; set them in the shell that launches Claude Code
or Codex. When `TYXTER_API_BASE_URL` is unset, the first four fall back to `http://localhost:3001`, a
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
make the host call the Tyxter API you configure (`TYXTER_API_BASE_URL` for the curl and SDK
skills, `TYXTER_API_URL` for the CLI container; the hosted API is `https://api.tyxter.com`) with
your API key, sending what you ask it to send, such as recipient numbers and message and template
content, to the Tyxter account that key belongs to, or to a local Tyxter stack when the base URL
points there. Claude's MCP entry uses the API key you enter as a bearer token for the URL you
enter; Codex's native MCP registration reads the bearer key from `TYXTER_API_KEY` at runtime.

A few skills also reach other places:

- `find-developer-tools` and `integrate-tyxter-messaging` install `tyxter` from npm, and
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

## Upgrade and verify

Refresh your marketplace and reinstall/update the plugin, then start a new host session:

```bash
codex plugin marketplace upgrade tyxter
codex plugin add tyxter@tyxter
claude plugin marketplace update tyxter
claude plugin update tyxter@tyxter
```

Use the commands for your host, including for an existing Claude installation registered
from the repository's previous URL. Keep your selected account MCP URL and secret environment
configuration when upgrading. Plugin installation does not prove account authentication.
For a local checkout, register its
path instead of the remote repository.

Maintainers can validate Claude's manifests locally:

```bash
claude plugin validate --strict .claude-plugin/plugin.json --json
claude plugin validate --strict .claude-plugin/marketplace.json --json
```

Local validation and isolated host installs cover package parsing, discovery, cached skills,
and MCP configuration. Public directory submissions and authenticated customer tool calls are
separate checks.

## Generated skills

`skills/` is generated from Tyxter's source repository by its `claude-plugin:sync` command, and
that repository's `claude-plugin:check` command compares this folder with the source byte for
byte. Do not edit `skills/` here. To report a problem with a skill, open an issue in this
repository.

## License

MIT. See `LICENSE`.
