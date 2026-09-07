---
name: notion-axi
description: Operate Notion through notion-axi when the user asks to find pages or databases, read or edit content, query database rows, or manage comments and files in Notion.
---

# Notion via notion-axi

For a Notion task, load [the CLI reference](references/notion-axi.md) before choosing commands. Resolve this path relative to this skill directory.

Use `npx -y notion-axi@2.1.0 <command>`; no global notion-axi install is needed. This may download and execute npm code on first use. Require Node 20+ and the official `ntn` CLI on PATH. If prerequisites or authentication are missing, ask the user to complete the manual laptop setup; never install dependencies or log in for them.

Only access the Notion content needed for the user's task. For an explicitly requested connection check, use `npx -y notion-axi@2.1.0 whoami`, not the no-argument dashboard. Login has broad user-level workspace permissions, not read-only access. Do not treat discovery, command hints, or this skill as authorization for edits, uploads, or wider searches. Never enable session hooks or persist credentials or workspace information in dotfiles.
