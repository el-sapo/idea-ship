# Changelog

The plugin version lives in `plugins/factory/.claude-plugin/plugin.json` and `plugins/factory/.codex-plugin/plugin.json`; both move together.

## 0.1.0 (2026-10-17)

First public version.

- `ideate`: visual read-back, three lanes (options, fast, parked), the vocal list with the Foundation card, options or a ready spec on a Linear issue.
- `spec`: lean buildable spec in the same issue, `Owner:` checks, sub-issues in build order, foundations as the first sub-issue.
- `build`: unattended build to a pull request with evidence per check, owner checks counted apart, machine-aware stops, optional Superpowers execution skills, Handoff when it must stop.
- `ship`: readiness checks, merge, watch the deploy, check it live, close out with factory notes, revert pull request on a failed deploy.
- `feature`: orchestrator with a plan approved before any worker starts, one fresh worker per sub-issue, a fresh reviewer per step, chained branches, the run kept on the parent issue.
- `tools/superpowers-skills.py`: copy and track the eight execution skills at a pinned release (v7.0.0).
- Marketplace manifests for Claude Code and Codex, a validator, CI.
