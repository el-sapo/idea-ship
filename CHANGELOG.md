# Changelog

The plugin version lives in `plugins/factory/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and `.cursor-plugin/plugin.json`; the three move together.

## 0.3.1 (2026-10-19)

- Cursor manifests: `.cursor-plugin/marketplace.json` at the root and `plugins/factory/.cursor-plugin/plugin.json`, so Cursor shows the marketplace as `sdlc-fede` instead of a generated name. The validator checks them.

## 0.3.0 (2026-10-19)

- `build`: no third-party execution skills. The by-hand discipline (tests first, a fresh implementer per task, a fresh reviewer at the end, evidence per check) is the only path, and the preflight no longer looks for copied skills. The scratch folder is `.factory/plans/`, in place of `.superpowers/plans/`.
- `build`, `ship`: the repository's instructions file also says how the app deploys and where to check it live. The skills follow it and name no platform of their own, so hosting, CI and stores vary per app without touching the skills.
- `build`, `ideate`, `spec`: the instructions file is named as `AGENTS.md` first, `CLAUDE.md` second.
- Removed `tools/superpowers-skills.py` and its README; the CI step that compiled it is gone.
- Docs and README updated to match; `docs/setup.md` says what the instructions file must cover.

## 0.2.0 (2026-10-17)

From the first real `feature` run.

- `feature`: a feature branch per feature, created at "go" from the integration branch. Every step builds on it and targets its pull request at it, verified steps merge into it with merge commits as the run goes (or on the owner's word with "steps on my word"), and the run ends with one final pull request into the integration branch for the owner to ship. Replaces stacked pull requests, which did not retarget themselves.
- `feature`: a taken step is "in the integration branch" only when `git merge-base --is-ancestor` says so; Linear's Done proves nothing. Owner results are recorded on the sub-issue so `ship` can read them. Holds can be added mid-run from a step's report. Secrets, keychain profiles and preconditions outside the repository are numbered plan decisions. Without Linear the run stops at preflight.
- `feature`: one reviewer by default, two (evidence re-run, and scope plus later-step impact) on high-complexity, integration-heavy or many-touch-point steps.
- `feature`: a renamed field between a spec and the code is a recorded decision, not a stop; only a changed shape a later step builds on stops the run.
- `feature`: on the owner's machine, a checkout in use gets a worktree for the run; workers are handed its path and never create one.
- `feature`, `build`: secrets are never asked for in chat; a file or an environment variable, and a pasted secret is reported as needing rotation.
- `ship`: refuses a pull request whose base is an unmerged step branch, treats a merge into a feature branch as "merged, not deployed", ships a parent's final pull request like any other, and proves every merge with `git merge-base --is-ancestor`.
- `build`: branch base and pull request target come from the prompt when an orchestrator sets them; works in a named worktree, never creates one.
- Docs: the production rule's one exception (a stop, the stated risk, and the owner's in-session word) recorded as such.

## 0.1.0 (2026-10-17)

First public version.

- `ideate`: visual read-back, three lanes (options, fast, parked), the vocal list with the Foundation card, options or a ready spec on a Linear issue.
- `spec`: lean buildable spec in the same issue, `Owner:` checks, sub-issues in build order, foundations as the first sub-issue.
- `build`: unattended build to a pull request with evidence per check, owner checks counted apart, machine-aware stops, optional Superpowers execution skills, Handoff when it must stop.
- `ship`: readiness checks, merge, watch the deploy, check it live, close out with factory notes, revert pull request on a failed deploy.
- `feature`: orchestrator with a plan approved before any worker starts, one fresh worker per sub-issue, a fresh reviewer per step, chained branches, the run kept on the parent issue.
- `tools/superpowers-skills.py`: copy and track the eight execution skills at a pinned release (v7.0.0).
- Marketplace manifests for Claude Code and Codex, a validator, CI.
