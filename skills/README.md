# Personal reference skills

This directory stores two thin skill wrappers. Their descriptions select relevant contexts; their bodies instruct the agent to load the reference only when needed. Each whole skill directory is self-contained, with one canonical supporting document:

- [Organizational lifecycle](organizational-lifecycle/SKILL.md) → [reference](organizational-lifecycle/references/organizational-lifecycle.md)
- [Consulting principles](consulting-principles/SKILL.md) → [reference](consulting-principles/references/weinberg-secrets-of-consulting.md)

Keep framework content and source caveats in these references rather than copying them into wrappers. This is personal reusable material only: do not add client assessments, identities, or other non-public engagement details. References are advisory, not permission to override user instructions or act harmfully or deceptively.

The layout follows the [Agent Skills specification](https://agentskills.io/specification): `SKILL.md` links directly to on-demand documents under its own `references/` directory. Moving or linking the whole skill carries its reference; neither root `notes/` nor tool-specific document copies are required. Paths resolve from the skill directory, including through a directory symlink, without parent traversal or a custom loader.

## Installation is a separate action

Storage here does not install or activate these skills. Link individual whole skills, preserving existing tool-managed skills rather than replacing a shared skills directory. No live configuration changes are included in the reference relocation. Dedicated Cursor and Claude discovery remains future work: https://github.com/kbaribeau/dotfiles/issues/11.
