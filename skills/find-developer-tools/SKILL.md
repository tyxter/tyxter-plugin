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

## CLI — tyxter-dev/tyxter-cli

Distributed as a container image:

    docker pull ghcr.io/tyxter-dev/tyxter-cli:latest
    docker run --rm ghcr.io/tyxter-dev/tyxter-cli:latest --help

Source: https://github.com/tyxter-dev/tyxter-cli

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
