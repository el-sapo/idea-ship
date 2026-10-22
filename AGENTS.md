# Working in this repository

This is a plugin marketplace: the deliverable is the text of six agent skills under `plugins/idea-ship/skills/`, plus the manifests that let Claude Code and Codex install them. There is no application to run.

- Validate with `python3 scripts/validate.py` before committing. It checks the manifests, every skill's front matter, and the prose rules below.
- Prose rules: no em dashes anywhere; neutral examples only (`ABC-12`, `main`); no real team keys, product names or people in skills or docs.
- The three plugin manifests (`plugins/idea-ship/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and `.cursor-plugin/plugin.json`) carry the same version, and the three marketplace files (`.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`) list the same plugin. A behaviour change bumps all three and adds a line to `CHANGELOG.md`.
- `docs/design.md` explains the shape; the skills are the truth. When they disagree, fix the doc.
- No third-party skills. The five skills stand on their own; do not copy skills from other projects in.
- No platform names in the skills (no hosting, CI or store products). Platform facts belong in each project's instructions file; the skills read it and follow it.
- Copies of these skills saved on an account or in another repository are mirrors; after editing here, tell the owner to re-save them.
