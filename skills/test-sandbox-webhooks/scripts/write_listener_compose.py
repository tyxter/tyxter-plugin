#!/usr/bin/env python3
"""Write a reusable Tyxter CLI compose file for a customer app repo."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose", default="compose.tyxter-cli.yaml")
    parser.add_argument("--env-example", default=".env.tyxter-cli.example")
    parser.add_argument("--api-url", default="https://api.tyxter.com")
    parser.add_argument("--app-port", default="3000")
    parser.add_argument("--webhook-path", default="/webhooks/tyxter")
    parser.add_argument(
        "--image",
        default="ghcr.io/tyxter-dev/tyxter-cli:latest",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    compose_path = Path(args.compose)
    env_path = Path(args.env_example)
    if compose_path.resolve() == env_path.resolve():
        parser.error("--compose and --env-example must name different files")
    for path in (compose_path, env_path):
        if path.exists() and not path.is_file():
            parser.error(f"{path} must be a regular file")
        if path.exists() and not args.force:
            raise SystemExit(f"{path} already exists. Pass --force to overwrite.")

    forward_url = f"http://host.docker.internal:{args.app_port}{normalize_path(args.webhook_path)}"
    staged = []
    created = []
    try:
        # Stage both outputs before publishing either, including with --force.
        for path, text in (
            (compose_path, compose_text(args.image, env_path.name)),
            (env_path, env_text(args.api_url, forward_url)),
        ):
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as file:
                staged.append((Path(file.name), path))
                file.write(text)
        for temporary, path in staged:
            if args.force:
                os.replace(temporary, path)
            else:
                # Link exclusively so a concurrent invocation cannot overwrite a file.
                os.link(temporary, path)
                created.append(path)
    except OSError as error:
        for path in created:
            path.unlink(missing_ok=True)
        parser.exit(1, f"Cannot write listener setup: {error}\n")
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    print(f"Wrote {compose_path}")
    print(f"Wrote {env_path}")
    print(f"Copy {env_path} to {env_path.with_suffix('')} and set TYXTER_API_KEY.")
    return 0


def normalize_path(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def compose_text(image: str, env_file: str) -> str:
    return f"""name: tyxter-sandbox-webhook-test

services:
  tyxter-cli:
    image: {image}
    container_name: tyxter-cli
    restart: unless-stopped
    env_file:
      - {env_file.removesuffix(".example")}
    environment:
      TYXTER_CLI_STATE_DIR: /data
    volumes:
      - tyxter-cli-data:/data
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  tyxter-cli-data:
"""


def env_text(api_url: str, forward_url: str) -> str:
    return f"""TYXTER_API_URL={api_url}
TYXTER_API_KEY=tx_sandbox_replace_me
TYXTER_WEBHOOK_FORWARD_URL={forward_url}

# Use the same local-only secret in your app's webhook verifier.
# Real Tyxter signing secrets are 64-char hex (no prefix).
TYXTER_WEBHOOK_SECRET=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

TYXTER_WEBHOOK_LIMIT=20
TYXTER_WEBHOOK_POLL_INTERVAL_MS=1000
"""


if __name__ == "__main__":
    raise SystemExit(main())
