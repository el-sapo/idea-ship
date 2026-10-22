# Contributing

## This repository is the source of truth

The skills under `plugins/factory/skills/` are the canonical text. Copies saved on a Claude account or committed into a project's `.claude/skills/` are mirrors: after a change here, re-save them there. Nothing syncs them for you, and git keeps no history of account skills.

## Editing a skill

- Keep the five principles at the top of each skill true. A new rule should follow from one of them, or earn a sixth.
- Prefer a sentence that explains the reason over a rule that forbids. Agents follow reasons better than lists.
- Keep the examples neutral: `ABC-12` for an issue, `main` for the default branch, no real team keys, product names or people.
- No em dashes. Use a comma, a colon or a full stop.
- Stay under 500 lines per skill. A skill that needs more is two skills.
- A change in what a skill writes to Linear (a template, a section name) is a change every other skill reads. Check `build` reads what `spec` writes, `ship` reads what `build` writes, and `feature` reads all three. The same goes for the instructions file: when `build` or `ship` starts reading something new from it, `setup`'s template needs a section for it.

## Before a commit

```sh
python3 scripts/validate.py
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin validate plugins/factory --strict
```

The first runs in CI. The other two need the Claude Code CLI.

## Testing a change

Dry runs with fresh agents are the cheapest test: give a fresh session the changed skill, a fixture issue in a scratch folder (for `setup`, a fixture repository with a local bare remote), and the trigger phrase, and read what it produces against what the skill promises. Then run a real small ticket. A skill change that alters behaviour gets a line in `CHANGELOG.md` and bumps the version in all three plugin manifests.

## What does not belong here

Project-specific instructions (a stack, a repository's conventions) belong in that project's instructions file. Specs and plans belong in Linear and in ignored scratch folders. Third-party skills are not copied in, and no platform (hosting, CI, a store) is named in a skill.
