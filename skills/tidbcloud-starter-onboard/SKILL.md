---
name: tidbcloud-starter-onboarding
description: Install and authenticate the TiDB Cloud CLI with OAuth, verify the active ticloud profile, and list accessible projects. Use when a user wants to sign in or sign up for TiDB Cloud, validate agent access to their TiDB Cloud account, or list the projects available to the coding agent.
---

# TiDB Cloud Starter Onboarding

Authenticate the user and list the TiDB Cloud projects the coding agent can access. This skill never creates, changes, or deletes cloud resources.

## Guardrails

- Do not request or reveal passwords, MFA codes, OAuth tokens, API private keys, SQL credentials, or connection strings.
- Leave browser identity work—sign-up, sign-in, email verification, CAPTCHA, MFA, billing, and consent—to the user.
- Do not use `ticloud config create` unless the user explicitly requests setup of an existing API-key pair. OAuth is the default for interactive use.
- Do not claim authentication is complete unless both `ticloud version` and `ticloud auth whoami` succeed.

## Install and authenticate

Use the normal `ticloud` command, not a workspace-local binary:

```sh
command -v ticloud
ticloud version
```

If unavailable, check the current official TiDB Cloud CLI instructions, obtain approval, then on macOS/Linux install it with:

```sh
curl https://raw.githubusercontent.com/tidbcloud/tidbcloud-cli/main/install.sh | sh
export PATH="$HOME/.ticloud/bin:$PATH"
command -v ticloud
ticloud version
```

Start OAuth sign-in when necessary:

```sh
ticloud auth login
ticloud auth whoami
ticloud config list
```

`ticloud auth login` uses a browser-mediated Device Code flow. The user completes that flow. Keep the terminal session running and actively monitor its output after presenting the authorization URL and code. Do not return control, run verification, or continue to another step until the command exits and prints `Successfully logged in.`. If it times out or is interrupted, report that state. A CLI profile is local configuration, not an organization user; select a non-default profile consistently with `-P <profile>` or `--profile <profile>`. Do not use `--insecure-storage` unless the user explicitly accepts plaintext local credential storage.

If either version or `whoami` fails, report the non-secret error and stop. Re-run login only with the user's direction.

## Discover account state

After successful authentication, collect the accessible project list only:

```sh
ticloud project list --output json
```

Do not list clusters, write discovery files, or classify the account. A project-list failure means the accessible project state could not be determined.

## Handoff

If `project list` succeeds, say:

> OAuth sign-in is complete. The coding agent can now use this account's authorized TiDB Cloud projects and resources.

Report the returned project names and IDs. Do not create or modify anything; wait for a user-directed action against existing resources.

## Authentication lifecycle

OAuth access can later expire or be revoked. Re-run `ticloud auth login` after a service authentication failure; use `ticloud auth logout` only when the user asks to clear the local login. Do not promise OAuth scopes or token lifetimes that are not published by the current official CLI documentation.
