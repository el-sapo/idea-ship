# Setup

How a project gets ready for the first ticket: install the plugin, connect accounts, say "setup". Most of it happens once per project.

## 1. Install the plugin

Install the plugin for local sessions. Cloud sessions do not install plugins, so for those save the six skills on your account or commit them to the repository's `.claude/skills/`; the [README](../README.md#where-the-skills-load) says why both exist.

Those copies are mirrors. Nothing syncs them with the plugin, so re-save them after every update, or cloud sessions keep running the old skills.

## 2. Connect accounts

The sessions that run the skills need the repository, with push access and a way to open pull requests, so `build` can open a pull request and `ship` can merge.

The Linear connector is your choice. With it, every skill reads the issue and writes back to it, so any later session can pick up the work; the connector writes as you, so Linear will usually not notify you of an agent's comment, and each skill ends with a short ping in the session for that reason. Without it, the chat is the thread: each skill gives you its text to paste instead of saving it, and `feature`, which keeps a run's state on the parent issue, cannot run. Setup suggests connecting it each time it runs, and never holds back a Ready for it; no other skill asks.

If you use Linear, turn on the GitHub integration, so a branch named the way Linear suggests links its pull request to the issue. `build` uses Linear's suggested branch name when it can read it.

Optionally, connect the hosting, if the app deploys and you want `ship` to watch the deploy and check the result live. CI is optional too: when it exists, `build` waits for it and fixes failures its change caused, and `ship` treats a red check as not ready.

## 3. Say "setup"

In a session on the repository, say "setup" and stay for it. It asks a few questions and waits for your yes before it writes anything, so it is not an unattended run.

- It reads the repository and proves the install, run, test and lint commands by running them. A command it could not find or run stays out of the instructions file and goes in the report.
- It asks only what the repository cannot say: how the app deploys and where to check it live, as numbered questions with defaults you can take with "ok".
- It checks each connection by using it, without creating any, then checks the Linear team, a project for the repository and the statuses. It creates the project only if you say yes.
- It drafts the instructions file, or lists what an existing one is missing, and shows you the draft. On your yes it opens a pull request that carries only that file. You merge it.
- It reports "Ready" with anything only you can check and anything worth fixing, or "Not ready" with a table of what is missing, why it matters and where to fix it.
- When the repository is ready and the project has no issues yet, it offers a first ticket.

Setup remembers nothing between runs, so say "setup" again after fixing a row, or whenever you want to know whether the repository is still ready. A re-run on a ready repository changes nothing.

## What setup checks, and what it leaves to you

Setup checks:

- the commands: install, run, test and lint, each one run and seen to work;
- the connections: Linear can be read, a branch can be pushed, a pull request can be opened, the hosting is visible when the repository shows any;
- when Linear is connected, the team, a project for the repository, and the statuses;
- branch protection on the default branch, which it reads and for which it recommends a rule.

It leaves to you:

- creating the repository and the hosting project;
- a Linear team, and any missing status;
- setting branch protection;
- merging its pull request;
- keeping the instructions file right afterwards. Agents never edit it, and setup only ever proposes it, or its missing sections, through a pull request.

**The statuses.** The skills move issues through Backlog, Todo, In Progress, In Review and Done. A team with renamed statuses works as long as the equivalents exist, such as "Ready" for Todo; setup reports a missing one and says to add it in the team's workflow settings.

**The instructions file** (`AGENTS.md`, or `CLAUDE.md` if that is what you use) says how to install, run, test and lint, how the app deploys, where to check it live, and which Linear team and project to use. `build` reads it in preflight and runs the tests as its baseline, so without a test command it cannot prove its changes; `ship` follows its deploy section. The skills name no platform of their own, so this file is where your platform choices live. Setup proposes no file until a test command works, because `build` runs the suite once before changing anything, as the baseline.

**The deploy.** `ship` watches the deploy after a merge and checks the result live. For that it needs hosting that deploys on merge to the default branch and, ideally, builds a preview per pull request so `build` can record the preview link. Without it, `ship` merges and reports "merged, not deployed". Native apps have no deploy to watch; `ship` says so and closes out on the merge.

**Branch protection** is your choice. The skills never push to the integration branch or force a merge, so protection costs nothing. Setup recommends pull requests required, the CI checks required when there is CI, and no force-push or deletion. It recommends a required review only when the history shows more than one person merging, because alone nobody could approve your pull requests and `ship` never goes around a protection.

**The integration branch** is the default branch unless you name another when you approve a feature plan, so a long-lived branch a team integrates on works. `feature` creates one branch per feature off it and ships back into it with one pull request; "Automatically delete head branches" is your choice and nothing depends on it.

**Nothing else.** Specs live in Linear and plans live in `.factory/plans/`, which `build` ignores with its own `.gitignore`, so setup leaves it alone.

## Where to run a session

| Session | Good for | Cannot |
|---|---|---|
| Cloud | Web apps, services, anything that builds on Linux | Build native apps, grant device permissions, run simulators or emulators |
| Your machine | Native and multiplatform apps, anything that needs a device or a local tool | Run while the machine is asleep |
| Remote Control from your phone | Steering a session on your machine while away | Nothing extra; it is your machine's session |

The skills find out where they run and say which checks that leaves to you. On your machine, a tool install is a recorded decision and a system permission prompt is a stop.

## The first ticket

Setup offers one when the repository is ready and the project has no issues yet: one small idea grounded in what it read, which it hands to `ideate` on your yes. Your own idea works just as well. Either way, start with something small enough for one pull request, ideally one with code to read, so `ideate` can take the fast lane. Watch three things: that the Linear writes land, that the published page opens from your phone, and how long the spec turns out. Then run a feature of three or four sub-issues through `feature` and watch the plan before you say "go".
