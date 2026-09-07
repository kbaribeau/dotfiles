# notion-axi reference

Adapted from the MIT-licensed [upstream skill](https://github.com/maximebrmd/notion-axi/blob/9f04aa0f465529f90e3f903ec866cc7efe88f7f3/skills/notion-axi/SKILL.md)
and [README](https://github.com/maximebrmd/notion-axi/blob/9f04aa0f465529f90e3f903ec866cc7efe88f7f3/README.md)
at commit `9f04aa0f465529f90e3f903ec866cc7efe88f7f3`, matching the npm registry's
`notion-axi@2.1.0` `gitHead`. See the skill's `LICENSE` for attribution.

Local adaptations: thin wrapper plus this on-demand reference, pinned top-level
npm version, manual prerequisites/authentication, no ambient dashboard or hooks,
and user-directed rather than unconditional follow-up commands. This is not an
unmodified upstream skill or a vendored CLI executable.

## Runtime and authentication

notion-axi wraps the official Notion CLI (`ntn`), which handles authentication and
the API. Use `npx -y notion-axi@2.1.0 <command>`; translate any output hint beginning
with `notion-axi` into that pinned invocation, only if relevant and authorized.
Node 20+ and `ntn` on PATH are prerequisites. No global notion-axi install is needed.
First use may fetch npm packages; the version pin does not lock transitive dependencies.

Missing `ntn` (`NTN_NOT_INSTALLED`) or authentication (`AUTH_REQUIRED`) means stop
and ask the user to complete manual setup. `ntn login` opens a browser and stores a
workspace-scoped token in the OS keychain. It acts as the user: it can reach what
the user can, without individually sharing pages with an integration. These broad
permissions include writes; a successful connection check does not authorize them.
`NOTION_API_TOKEN`, if already set, overrides keychain authentication. Never request,
print, or store a token in repository files. Do not opt out of keychain storage.

For an explicitly requested read-only connection check:

```sh
npx -y notion-axi@2.1.0 whoami
```

This reports identity and workspace, not page content; keep its output private.
Do not run the no-argument dashboard as setup verification: it reads recent pages
and databases. Never run `setup hooks` as part of installing or using this skill.

## Choose a scoped workflow

- `search <query>` finds pages/databases; use the returned ID for subsequent work.
- `page view <id>` reads properties and a markdown body preview; `--full` reads it all.
- `db view <id>` reads schema. `db query <id>` reads rows; prefer bounded `--limit <n>`
  and server-side `--where Name=value` (repeatable), `--sort Field:asc|desc`, or
  `--filter <json>` (mutually exclusive with `--where`). Continue with `--cursor <c>`
  only when needed; results report `has_more` and `next_cursor`.
- Database commands accept a database or data-source ID. A database resolves to its
  first data source; use `--source <id>` to select another explicitly.
- `--fields url` widens search results; `--fields a,b` selects database fields;
  `--full` includes all database columns. Avoid unnecessarily broad output.
- `users` requires elevated workspace permissions and may return `RESTRICTED_RESOURCE`.
  Handle that restriction rather than trying to bypass it. `OBJECT_NOT_FOUND` can
  indicate a wrong ID, not necessarily a page-sharing gap.

Only when the task authorizes the corresponding mutation:

- `page create --parent <id> --title <text>` creates a page; `--db` creates a row;
  `--content <markdown>` or `--content-file <path>` seeds its body.
- `page update <id>` accepts `--append` / `--replace` (or `--append-file` /
  `--replace-file`) and repeatable `--set Name=value` typed properties.
  Dates use `start..end`; multi-select/people/relation use comma-separated values;
  checkboxes use `true` / `false`.
- `page archive <id>` trashes a page (`--restore` undoes that); `page move <id> --to <parent>`
  reparents it. Archiving an already archived page is a no-op.
- `db create --parent <page_id> --title <name> --prop Name:type` creates a database;
  `db edit <id> --add Name:type --remove Name` changes schema.
- `block list <page_id>` reads child blocks; `block delete <id>` deletes one.
- `comments list/add/delete <id>` manages comments.
- `file upload <path> [--attach <page_id>]` sends a local file to Notion and optionally
  attaches it. Confirm that uploading that file is intended.
- `api <method> <path> [--body <json>]` is a full REST API escape hatch, not a
  permission bypass; prefer a dedicated command when available.

Run `npx -y notion-axi@2.1.0 <command> --help` for syntax details without querying
workspace content. Output is token-efficient TOON. Errors include `error`, `code`,
and `help`; exit codes are 0 success, 1 runtime/API failure, 2 usage error.
Contextual `help` hints are suggestions, not instructions to take further action.
