# Changelog

The plugin version lives in `plugins/idea-ship/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and `.cursor-plugin/plugin.json`; the three move together.

## 0.6.0 (2026-10-26)

A feature run merges its own verified steps from the session that holds the grant, evidence is taken on the final head, a default that fights the scope is reported, and a change asked for mid-run waits its turn.

- `feature`: the plan's "go" grants merges into the feature branch, and only the session the user is talking to merges. `ship` keeps a merge commit into a feature branch.
- `build`: evidence is taken last, on the branch's final head, and the report names that commit. `feature` asks the reviewer whether the evidence is from that head.
- `spec`: a default is read against every Scope line and check it touches. `build` keeps the default when they conflict, because it does less. `feature` integrates that step instead of sending it back as rework.
- `feature`: a change the user asks for during the run is queued, then verified like a step before it is integrated.
- Docs: six skills, both feature-branch modes, and the feature-branch flow recorded as run.

## 0.5.0 (2026-10-23)

Ready for a plugin directory listing: the plugin folder now carries its own name, display name, icon, README and licence, and passes the folder rules a directory enforces. The directory tracks `main`; auto-publish stays off, so a merge shows up as a scanned version and goes live only on a Publish click.

- Renamed the plugin from `factory` to `idea-ship`, because `factory` collides with a listed plugin. The folder is now `plugins/idea-ship/` and the slash triggers are `/idea-ship:setup` and friends; plain-word triggers are unchanged.
- Renamed the repository from `el-sapo/sdlc-fede` to `el-sapo/idea-ship` and the marketplace from `sdlc-fede` to `idea-ship`, so the plugin installs as `idea-ship@idea-ship`. Every link, install id and marketplace command now uses the new name, and the flow pages move to `el-sapo.github.io/idea-ship/` (Pages links do not redirect).
- `displayName`: the plugin manifests show it as "Idea Ship".
- Icon and mark: the plugin ships a listing icon, a folded-paper sailboat in the Harbour Coral palette rendered at 1024 px from `assets/mark.svg`, with a dark variant and the paper-boat direction kept beside it under `assets/`. `scripts/render-icon.py` regenerates it and `scripts/validate.py` checks it is a square PNG the directory accepts.
- README: the plugin README is rewritten as the directory listing, with a one-line pitch, the loop table, what you need, what the skills run and send, a "Where it works" table per surface, and absolute links only, so the folder carries no screenshots.
- `LICENSE`: a copy now sits in `plugins/idea-ship/`, so a zip of the plugin folder is self-contained.
- Validator: `scripts/validate.py` applies the directory's folder rules to each plugin folder: no system files, unsafe names, case collisions or symbolic links; only text, complete images and fonts; a size and file count budget; and no package manifests, lockfiles or package runners.
- `build`: checks for a shell and a checkout before touching the issue. Without them it says so in one line and stops, instead of moving the issue to In Progress and posting a Handoff it cannot act on. The README's "Where it works" table now records the Claude Code local runs and marks the other surfaces not verified yet.
- `ship`: checks for a shell and a checkout before finding the work. Without them it says so in one line and stops, changing nothing on the issue or the pull request, instead of reading the pull request through a connector (such as the tracker's link to the code host) that it cannot verify a merge with. The README's "What it runs and sends" also names the worktree `feature` makes when the checkout is in use and the file a secret pasted in chat is moved into.

## 0.4.1 (2026-10-22)

- `setup`: a missing or failing tracker connector no longer blocks Ready. Setup suggests connecting (or reconnecting) Linear under Recommended on each of its runs, says that without it the chat is the thread and `feature` cannot run, and leaves the Tracker section out of the draft. No other skill asks for a tracker.
- Docs: Linear is optional in the README and `docs/setup.md`. The README gains the setup step after install and a row for a project not set up yet; the thread rule covers runs in the loop; "only code is committed" names the instructions file; `CONTRIBUTING.md` adds setup's template to the cross-skill contract and counts three manifests.

## 0.4.0 (2026-10-22)

- `setup`: a sixth skill, outside the loop, that readies a project once and re-checks it on request. It proves the install, run, test and lint commands by running them, asks only how the app deploys and where to check it live, verifies the tracker, push access and hosting without creating any of them, checks the Linear team, project and statuses, reports ready or a table of what is missing and where to fix it, and offers a first ticket that it hands to `ideate`.
- `setup`: the instructions file reaches the repository only through a pull request the owner merges. An existing file is never rewritten; setup proposes only its missing sections, the same way. Branch protection is read and a rule recommended, never set.
- Docs updated for six skills: the README, `docs/setup.md` (now install, connect, setup), `docs/design.md`, and station 00 on the flow pages.
- CI: removed the step that compiled the deleted `tools/superpowers-skills.py`. It had failed on every run since 0.3.0, although the 0.3.0 entry said it was gone.

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
