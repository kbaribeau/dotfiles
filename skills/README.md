# Shared personal skills

One canonical source per repository-owned skill here in `skills/`, exposed to
Codex, Cursor, and Claude Code through tracked per-skill directory aliases. Thin `SKILL.md` wrappers select relevant contexts
and load their own supporting documents only when needed:

- [Organizational lifecycle](organizational-lifecycle/SKILL.md) → [reference](organizational-lifecycle/references/organizational-lifecycle.md)
- [Consulting principles](consulting-principles/SKILL.md) → [reference](consulting-principles/references/weinberg-secrets-of-consulting.md)

The durable ownership boundary is defined in the root
[skill ownership policy](../README.md#philosophy-skill-ownership). This guide owns
installation and discovery details, not third-party installation recipes.

Keep framework content and source caveats in references, not tool-specific copies.
Do not add client assessments, identities, tokens, or other non-public details.
References are advisory, not permission to override user instructions or act
harmfully or deceptively.

The layout follows the [Agent Skills specification](https://agentskills.io/specification):
`SKILL.md` links directly to on-demand documents under its own `references/` directory.
Moving or linking the whole skill carries its reference. Paths resolve from the
skill directory, including through a directory symlink; no root `notes/`, parent
traversal, or custom loader is required.

## Installation and coexistence

Storage here alone does not activate skills. The [repository installer](../README.md#gnu-stow-installation)
uses the `personal-skills` Stow package. All three tools receive tracked relative
per-skill aliases that resolve through the package to the canonical directories
here. This preserves directory-level discovery: a Codex fixture did not discover
skills when only `SKILL.md` and reference files were symlinked individually.
Neither installer nor package scans/adopts other skills found on the laptop.

Existing shared real parents retain their identity. Unrelated operator-installed
skills, supporting files and settings remain untouched. Ordinary occupied-file or
foreign-link conflicts abort the plan. Stow can merge real directories; reconcile
same-name skills separately rather than mixing two owners' contents. No entire
shared skill root is linked. See the root guide for Stow's safety limits.

Editing or adding canonical files is visible in all tools immediately through the
per-skill directory aliases. References remain skill-relative and standalone-copy
compatible. A moved/deleted clone breaks links; keep the installing clone available.

## Discovery evidence

Authoritative discovery documentation checked during implementation:

| Local tool | User destination used here | Evidence / limits |
| --- | --- | --- |
| [Codex](https://developers.openai.com/codex/skills/) | `~/.agents/skills/<name>` | Documents user-scope discovery and following symlinked skill folders. |
| [Cursor](https://cursor.com/docs/context/skills) | `~/.cursor/skills/<name>` | Documents this global location, plus `.agents`, Claude, and Codex compatibility locations. The skills page does **not** specify symlink support or duplicate-target precedence; live discovery remains unverified. |
| [Claude Code](https://code.claude.com/docs/en/skills#where-skills-live) | `~/.claude/skills/<name>` | Documents personal skills, directory symlinks, and loading the same target only once. |

Cursor can also see the Codex/Claude locations: verify that its UI lists one usable
entry per name rather than assuming deduplication. These are local-machine
integrations, not Claude.ai/Cowork, Cursor Cloud Agents, remote SSH, or automatic
cloud syncing. The installer changes no sync/disable settings and neither grants
tool permissions nor invokes skills. Sandboxes must be able to read the source
clone. Custom tool-directory overrides are unsupported.

## Verification without skill invocation

Run the offline fixture suite and optional isolated Codex probe from the root
[validation instructions](../README.md#validation). Fixtures read every `SKILL.md`
and reference through all three destinations, check shared-source updates and
standalone portability, and test repeat runs, conflicts, and coexistence with
unrelated operator-installed skill directories and symlinks. Filesystem checks are
**not** proof that Cursor or Claude loaded the skill.

After a separately authorized installation on a future laptop:

- **Codex:** restart if needed and inspect the skill list (`/skills`); both personal
  skill names should be available unless disabled. The optional probe verifies
  discovery without a model turn in an isolated home.
- **Cursor:** open Settings → Rules (skills appear under Agent Decides), or Customize
  → Skills on newer versions; confirm both personal skill names and no duplicate
  entries. Inspect each linked `SKILL.md` and its relative reference without invoking it.
- **Claude Code:** restart if the top-level skills directory was newly created;
  inspect `/skills` for both personal skill names. No skill invocation is needed.
  Local overrides, enterprise policy, and same-name skills can affect availability.

Cursor and Claude executables were unavailable in the implementation environment;
no live discovery or model-driven reference-read claim is made for them. Do not
silently replace links with copies if a version cannot discover them: report the
version and reconcile separately.
