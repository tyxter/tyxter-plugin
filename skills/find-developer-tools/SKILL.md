---
name: find-developer-tools
description: Find and install the official Tyxter Messaging developer tools — the tyxter TypeScript/JavaScript SDK and the tyxter-cli — and how to authenticate them.
---

# Find Tyxter Messaging developer tools

Tyxter Messaging is an agent-first WhatsApp Business messaging API. These are the
official, supported ways to integrate it from code or a terminal.

## TypeScript / JavaScript SDK — `tyxter`

Published on npm:

    npm install tyxter

A typed client for the public `/v1/*` API — messages, templates, broadcasts,
phone numbers, payments, and signed webhooks. Runs in Node and edge runtimes.

## CLI — `@tyxter/cli`

Published on npm. Requires Node.js 22.12+, with no Docker, pnpm, or clone:

    npx @tyxter/cli --help
    npx @tyxter/cli listen --from-now --forward-to http://localhost:3000/webhooks/tyxter

Load a sandbox key through `TYXTER_API_KEY` in your environment or ignored
secret file; do not pass its value on the command line. The normal listener
requires a `tx_sandbox_` key. It prints a local signing secret for the app's
verifier and persists state in the ignored `.tyxter-cli/` directory.

Install globally with `npm install --global @tyxter/cli` for the `tyxter`
command. The official `npx tyxter-cli` compatibility package runs the same CLI.

Docker is also available:

    docker pull ghcr.io/tyxter/tyxter-cli:latest
    docker run --rm ghcr.io/tyxter/tyxter-cli:latest --help

Source and commands: https://github.com/tyxter/tyxter-cli

## Authenticate

Both use a Tyxter API key sent as a bearer token:

    Authorization: Bearer tx_live_xxxxxxxxxxxxxxxxxxxxxxxx

Use a `tx_sandbox_…` key for the deterministic sandbox environment or a
`tx_live_…` key for production. To bootstrap without an existing key, use the
device-code API-key flow in /auth.md:

    POST /v1/agent-api-key-device-authorizations
    POST /v1/agent-api-key-device-authorizations/token

## Keep exploring

- OpenAPI 3.1: /openapi.json
- Capability manifest: /.well-known/tyxter.json
- API catalog (RFC 9727): /.well-known/api-catalog
- Docs MCP server card: /.well-known/mcp/server-card.json
- Docs index for agents: /llms.txt
