# Working in this repository

This is a plugin marketplace: the deliverable is the text of five agent skills under `plugins/factory/skills/`, plus the manifests that let Claude Code and Codex install them. There is no application to run.

- Validate with `python3 scripts/validate.py` before committing. It checks the manifests, every skill's front matter, and the prose rules below.
- Prose rules: no em dashes anywhere; neutral examples only (`ABC-12`, `main`); no real team keys, product names or people in skills or docs.
- The two plugin manifests (`plugins/factory/.claude-plugin/plugin.json` and `plugins/factory/.codex-plugin/plugin.json`) carry the same version. A behaviour change bumps both and adds a line to `CHANGELOG.md`.
- `docs/design.md` explains the shape; the skills are the truth. When they disagree, fix the doc.
- Do not add skills from other projects by hand. `tools/superpowers-skills.py` is how third-party skills come in, with their license and a version record.
- Copies of these skills saved on an account or in another repository are mirrors; after editing here, tell the owner to re-save them.
