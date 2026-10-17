# Setup

What a repository and its surroundings need before the first ticket goes through. Most of it is one-time.

## 1. Linear

- A team with the default statuses: Backlog, Todo, In Progress, In Review, Done. The skills move issues between these; a team with renamed statuses works as long as the equivalents exist.
- The GitHub integration turned on, so a branch named the way Linear suggests links its pull request to the issue. `build` uses Linear's suggested branch name when it can read it.
- A Linear connector in the sessions that run the skills. The connector writes as you, so Linear will usually not notify you of an agent's comment; each skill ends with a short ping in the session for that reason.

## 2. GitHub

- The repository attached to the session, with push access, so `build` can open a pull request and `ship` can merge.
- CI is optional. When it exists, `build` waits for it and fixes failures its change caused, and `ship` treats a red check as not ready.
- Branch protection is your choice. The skills never push to the default branch or force a merge, so protection costs nothing.

## 3. Hosting

`ship` watches the deploy after a merge and checks the result live. For that it needs hosting that deploys on merge to the default branch and, ideally, builds a preview per pull request so `build` can record the preview link. Without it, `ship` merges and reports "merged, not deployed". Native apps have no deploy to watch; `ship` says so and closes out on the merge.

## 4. The repository

- **An instructions file** (`CLAUDE.md` or `AGENTS.md`) that says how to install, run, test and lint. `build` reads it in preflight and stops when it cannot find out how to run the tests. Agents never edit this file; keeping it right is your job.
- **A test suite that runs.** `build` runs it once before changing anything, as the baseline.
- **Optional: the execution skills.** See [tools/README.md](../tools/README.md). `build` works without them.
- **Nothing else.** Specs live in Linear and plans live in `.superpowers/plans/`, which `build` ignores with its own `.gitignore`.

## 5. The skills

Install the plugin for local sessions, and save the five skills on your account or commit them to the repository's `.claude/skills/` for cloud sessions; the [README](../README.md#where-the-skills-load) says why both exist. A session needs the Linear connector and the repository, and nothing else.

## 6. Where to run a session

| Session | Good for | Cannot |
|---|---|---|
| Cloud | Web apps, services, anything that builds on Linux | Build native apps, grant device permissions, run simulators or emulators |
| Your machine | Native and multiplatform apps, anything that needs a device or a local tool | Run while the machine is asleep |
| Remote Control from your phone | Steering a session on your machine while away | Nothing extra; it is your machine's session |

The skills find out where they run and say which checks that leaves to you. On your machine, a tool install is a recorded decision and a system permission prompt is a stop.

## The first ticket

Start with something small enough for one pull request, ideally one with code to read, so `ideate` can take the fast lane. Watch three things: that the Linear writes land, that the published page opens from your phone, and how long the spec turns out. Then run a feature of three or four sub-issues through `feature` and watch the plan before you say "go".
