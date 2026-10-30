# Tyxter Messaging plugin for Codex and Claude Code

Eight shared skills for the Tyxter Messaging API, Tyxter's WhatsApp Business messaging API.
Claude Code connects to your account through the plugin's MCP prompts; Codex uses a separate
native MCP registration with your own URL and an API key from your environment.

The plugin is beta, version `0.2.1`. Its canonical repository is
[tyxter/tyxter-plugin](https://github.com/tyxter/tyxter-plugin).
Both host manifests describe the same release and skill tree: `.claude-plugin/plugin.json`
and `.codex-plugin/plugin.json`. The catalogs `.claude-plugin/marketplace.json` and
`.agents/plugins/marketplace.json` expose it as `tyxter@tyxter`.

## Skills

The plugin ships eight skills. Each line below quotes the skill's own `description`:

- `/tyxter:create-template`: Use when a user needs to draft, create, estimate, or submit a WhatsApp template through the Tyxter API.
- `/tyxter:debug-failed-delivery`: Use when a Tyxter WhatsApp message fails, stalls, disappears, or needs investigation through status, traces, and webhook attempts.
- `/tyxter:find-developer-tools`: Find and install the official Tyxter Messaging developer tools — the tyxter TypeScript/JavaScript SDK and the tyxter-cli — and how to authenticate them.
- `/tyxter:inspect-billing-usage`: Use when a user needs to reconcile Tyxter usage, investigate charges or billing blocks, or inspect balances, ledger entries, and invoices.
- `/tyxter:integrate-tyxter-messaging`: Integrate Tyxter Messaging into an existing repository by installing the official JavaScript/TypeScript SDK, obtaining a human-approved sandbox API key, proving a first send, adding verified webhooks, handling stable errors and idempotency, and promoting to production only as a separate action.
- `/tyxter:send-sandbox-message`: Use when a user needs a first Tyxter sandbox send, wants to validate Quickstart, or needs to inspect test-message delivery.
- `/tyxter:test-sandbox-webhooks`: Use when a user needs to test Tyxter sandbox webhooks against a local app, run the CLI listener, or generate a reusable Docker Compose setup.
- `/tyxter:verify-webhook-signature`: Use when a user needs to implement or debug Tyxter webhook HMAC verification, raw-body handling, timestamp checks, or replay protection.

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

`.claude-plugin/plugin.json` declares two account MCP options:

- **Tyxter MCP URL** (`TYXTER_MCP_URL`): your Tyxter MCP server URL, shaped
  `https://api.tyxter.com/mcp/p/<project>/<environment>`. Copy it from the Tyxter dashboard
  Connections page, MCP tab.
- **Tyxter API key** (`TYXTER_API_KEY`): sent as a bearer token to that URL. Use a key whose
  prefix matches the URL's environment. The value is declared `sensitive`.

`.mcp.json` uses those two values, and only those values, to configure the `tyxter-messaging`
MCP server. It contains no URL or key of its own.

For a skills-only install, leave those MCP options unset. With Claude Code 2.1.312,
`claude plugin install tyxter@tyxter` succeeds and enables the plugin without either value;
it reports the two missing options, and all eight skills appear in the host's command catalog.
Configure them later with `/plugin configure tyxter@tyxter`
when you want the account MCP connection. The API skills still require their own shell
variables as described below. Installation does not establish an authenticated MCP connection.

The skills do not read those two values. They use the environment variables listed in each
`SKILL.md`. `send-sandbox-message`, `create-template`, `debug-failed-delivery`,
`inspect-billing-usage` and `integrate-tyxter-messaging` call the API at `TYXTER_API_BASE_URL`
with `TYXTER_API_KEY` or `TYXTER_SANDBOX_API_KEY`; set them in the shell that launches Claude Code
or Codex. When `TYXTER_API_BASE_URL` is unset, these skills use `https://api.tyxter.com`.
Load a matching API key into the shell environment; the examples require one explicitly.
For a local Tyxter stack, set `TYXTER_API_BASE_URL=http://localhost:3001` and supply that
stack's sandbox key. `inspect-billing-usage` also requires `TYXTER_USAGE_FROM` and
`TYXTER_USAGE_TO` as ISO 8601 timestamps with offsets.

`test-sandbox-webhooks` does not use
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
Claude Code resolves `${CLAUDE_SKILL_DIR}` to the installed skill directory. In Codex,
use the absolute directory containing the loaded `SKILL.md`: the bundled helper lives at
`scripts/write_listener_compose.py` within that directory. Run it with `python3` from the
customer app's directory. Both output files are staged before either is written; an
unwritable destination reports an error without leaving a partial setup during staging.
Existing files require `--force`.

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

## Releases

Pushes to `main` and pull requests validate the manifests and run the release and helper tests.
A pushed `v*` tag runs the same validation, then creates a GitHub release with generated notes.
The tag must exactly match `v<version>` in both host manifests. Plain `X.Y.Z` versions become
latest releases; versions with prerelease or build suffixes become prereleases. Reruns
preserve an existing release.

To release, sync the canonical skills, update both manifests and the README version, run:

```bash
node .github/release-metadata.mjs
node --test .github/release.test.mjs
python3 skills/test-sandbox-webhooks/scripts/write_listener_compose.test.py
```

Commit and push the reviewed changes, then create and push the matching version tag:

```bash
git tag v0.2.1
git push origin v0.2.1
```

GitHub provides source archives for the tagged revision, containing both host manifests and
the shared skill tree. Marketplace installs continue to use the repository's default branch.

## Generated skills

`skills/` is generated from Tyxter's source repository by its `claude-plugin:sync` command, and
that repository's `claude-plugin:check` command compares this folder with the source byte for
byte. Do not edit `skills/` here. To report a problem with a skill, open an issue in this
repository.

## License

MIT. See `LICENSE`.
