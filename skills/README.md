# Shared skills

One canonical source per skill, linked as a whole directory for Codex, Cursor, and
Claude Code. Thin `SKILL.md` wrappers select relevant contexts and load their own
supporting documents only when needed:

- [Organizational lifecycle](organizational-lifecycle/SKILL.md) → [reference](organizational-lifecycle/references/organizational-lifecycle.md)
- [Consulting principles](consulting-principles/SKILL.md) → [reference](consulting-principles/references/weinberg-secrets-of-consulting.md)
- [notion-axi](notion-axi/SKILL.md) → [reference and upstream revision](notion-axi/references/notion-axi.md)

Keep framework content and source caveats in references, not tool-specific copies.
Do not add client assessments, identities, tokens, or other non-public details.
References are advisory, not permission to override user instructions or act
harmfully or deceptively.

The layout follows the [Agent Skills specification](https://agentskills.io/specification):
`SKILL.md` links directly to on-demand documents under its own `references/` directory.
Moving or linking the whole skill carries its reference. Paths resolve from the
skill directory, including through a directory symlink; no root `notes/`, parent
traversal, or custom loader is required.

## Installation and discovery

Storage here alone does not activate skills. The [repository installer](../README.md)
links each of the three skill directories individually into each destination below.
It preserves real parent directories, unrelated/tool-managed skills, and settings;
conflicts abort preflight without writes. Repeated installation keeps correct links
verbatim. A moved/deleted clone breaks links; keep the installing clone available.

Authoritative discovery documentation checked during implementation:

| Local tool | User destination used here | Evidence / limits |
| --- | --- | --- |
| [Codex](https://developers.openai.com/codex/skills/) | `~/.agents/skills/<name>` | Documents user-scope discovery and following symlinked skill folders. |
| [Cursor](https://cursor.com/docs/context/skills) | `~/.cursor/skills/<name>` | Documents this global location, plus `.agents`, Claude, and Codex compatibility locations. The skills page does **not** specify symlink support or duplicate-target precedence; live discovery remains unverified. |
| [Claude Code](https://code.claude.com/docs/en/skills#where-skills-live) | `~/.claude/skills/<name>` | Documents personal skills, directory symlinks, and loading the same target only once. |

All nine links point directly to the same three repository directories; no shared
parent is replaced. Cursor can also see the Codex/Claude locations: verify that its
UI lists one usable entry per name rather than assuming deduplication. These are
local-machine integrations, not Claude.ai/Cowork, Cursor Cloud Agents, remote SSH,
or automatic cloud syncing. The installer changes no sync/disable settings and
neither grants tool permissions nor invokes skills. Sandboxes must be able to read
the source clone. Custom tool-directory overrides are unsupported.

### Verification without Notion access

Run the offline fixture suite and optional isolated Codex probe from the root
[validation instructions](../README.md#validation). Fixtures read every `SKILL.md`
and reference through all three destinations, check shared-source updates and
standalone portability, and test repeat runs, conflicts, and unrelated state.
Filesystem checks are **not** proof that Cursor or Claude loaded the skill.

After a separately authorized installation on a future laptop:

- **Codex:** restart if needed and inspect the skill list (`/skills`); all three names
  should be available unless disabled. The optional probe verifies discovery without
  a model turn in an isolated home.
- **Cursor:** open Settings → Rules (skills appear under Agent Decides), or Customize
  → Skills on newer versions; confirm the three names and no duplicate entries.
  Inspect the linked `SKILL.md` and its relative reference, without invoking Notion.
- **Claude Code:** restart if the top-level skills directory was newly created;
  inspect `/skills` for the three names. No skill invocation is needed. Local
  overrides, enterprise policy, and same-name skills can affect availability.

Cursor and Claude executables were unavailable in the implementation environment;
no live discovery or model-driven reference-read claim is made for them. Do not
silently replace links with copies if a version cannot discover them: report the
version and reconcile separately.

## notion-axi: future-laptop setup (manual)

The [upstream README](https://github.com/maximebrmd/notion-axi/blob/9f04aa0f465529f90e3f903ec866cc7efe88f7f3/README.md)
recommends `npx skills add maximebrmd/notion-axi --skill notion-axi -g`, then on-demand
`npx -y notion-axi`; **no global notion-axi install is required**. Here the existing
manifest installer replaces only that skill-manager step: the reviewed, adapted
skill is checked in at a fixed upstream commit, uses the repository's reference
convention, and pins invocations to `notion-axi@2.1.0`. Do not also run `skills add`
over these destinations; it would introduce another owner/update path.

This repository has no general package/bootstrap manager; `install.sh` deliberately
only links files. Adding a package manager, downloader, submodule, global CLI wrapper,
or session hook is unnecessary. A fresh clone plus the normal link installer
reproducibly installs the same skill bytes, offline. CLI runtime prerequisites are
separate, explicit actions, like other tool dependencies in this repository:

1. Install a supported **Node.js 20+** with npm/npx using your normal Node setup.
   Check `node --version` and `npx --version`. Node is needed for notion-axi, not
   for the dotfiles link installer.
2. Install the **official Notion CLI (`ntn`)** following its
   [installation guide](https://developers.notion.com/cli/get-started/installation).
   Upstream recommends `curl -fsSL https://ntn.dev | bash` on macOS/Linux; inspect
   [the script](https://ntn.dev/install.sh) before deliberately executing it.
   The official npm alternative is `npm install --global ntn`, but currently
   requires **Node 22+ and npm 10+**, stricter than notion-axi's Node 20 minimum.
   Check `ntn --version` and ensure it is on PATH. Neither command is run by dotfiles.
3. **Manually authorize each laptop** with `ntn login`. Confirm the terminal and
   browser verification codes match before approving. See the official
   [authentication guide](https://developers.notion.com/cli/get-started/authentication).
   Login requires full workspace membership and stores a workspace-scoped token in
   the OS keychain (macOS Keychain / Linux Secret Service). It acts as **you**, with
   broad read/write access to what you can access in that workspace, without a
   per-page sharing step. It is **not a read-only integration**. Do not use the
   plaintext-storage opt-out or copy credentials/configuration into dotfiles.
   An existing `NOTION_API_TOKEN` overrides the keychain; do not commit or print it.
4. When explicitly ready to contact Notion, perform only a read-only identity check:
   `npx -y notion-axi@2.1.0 whoami`. This reports identity and workspace; keep output
   private. Do not use the no-argument dashboard: it reads recent workspace content.

`npx -y` may download and execute npm code on first use. The top-level version is
pinned, **not** the transitive npm dependency graph or independently installed `ntn`.
No npm packages, login, Notion requests (including `whoami`), live links, or session
hooks are part of this change's validation. In particular, never run `setup hooks`
as part of laptop setup; upstream's ambient-context hook is a separate optional
feature that this integration intentionally does not enable.

### Updating the upstream skill

Review upstream `README.md`, `skills/notion-axi/SKILL.md`, `package.json`, and license
at a chosen full commit. Confirm the published npm version's `gitHead` matches;
update the source links, adapted reference, wrapper's version, and setup instructions
together. Preserve the MIT notice and document local adaptations. Rerun offline
fixtures and available discovery probes. Do not fetch a moving branch or invoke
`npx skills` from the link installer, and never auto-update runtime dependencies.
