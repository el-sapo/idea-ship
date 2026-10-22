---
name: setup
description: Use when the user says "setup", "set up this repo for the factory" or "is this repo ready": check that a project is ready for the factory loop, prove its commands, verify the connections and the Linear team, propose the instructions file as a pull request, report what is missing and where to fix it, and offer a first ticket.
---

# Setup

The owner has a repository and wants the factory loop (`ideate`, `spec`, `build`, `ship`) to work on it. Read what the repo already says, prove its commands by running them, check every connection the loop depends on, get the instructions file right through a pull request the owner merges, and tell them in one report what is ready and what is still theirs to fix. Setup runs once per project, outside the loop, and again whenever the owner asks whether the repo is still ready.

The owner is in the session for this one. Setup asks a few questions and waits for a yes before it writes anything, so it is not an unattended run.

Five principles explain the rules below:

- **The instructions file is the owner's.** Every later agent obeys it, so a change to it is a change to every agent. Setup drafts and proposes; the file reaches the repo only through a pull request the owner merges.
- **Verify connections, never create them.** Accounts, integrations and permissions are the owner's to grant. Setup proves what works and says exactly what is missing and where to connect it.
- **Stateless and safe to re-run.** Setup remembers nothing between runs, so every run checks everything again from the repo, the tracker and the connections. A re-run on a ready repo changes nothing, and no run duplicates a project, a branch, a pull request or a ticket.
- **Ask only what the repo cannot say.** Files answer most questions. The owner is asked only for what no file can tell, which is usually how the app reaches users and where to check it live.
- **Evidence, not claims.** A command goes in the instructions file only if setup ran it and saw it work. One it could not find, or that failed, is reported as missing, never guessed.

## 1. Read the repo and prove the commands

Read the README, the instructions file if there is one (`AGENTS.md` or `CLAUDE.md`), the package scripts and build files (a package manifest, a lockfile, a makefile or task runner), and the CI configuration if there is one, since it often runs the real test and lint commands. Find the default branch from the remote. If no repository is attached to the session, stop and say where to attach one, because everything else depends on it.

Find the commands to install, run, test and lint, and run each one in that order:

- **Install** worked when it finished without errors. The lockfile decides the package manager.
- **Run** worked when the app came up: it printed its ready line or answered on its port. Stop it afterwards. A library or tool with no app to start has nothing to run, and the file says so.
- **Test** worked when the suite ran to the end and reported. A suite with failing tests is a working command with a red baseline: it goes in the draft, and the failures go in the report, because `build` will meet them on every run.
- **Lint** works the same way. A repo with no linter at all has none, and the file says so; that is not a gap.

A command that cannot be found, or stops before doing its job (a missing tool, a missing secret, an error in the script), is missing. Leave its section out of the draft and list it in the report with the error, so a later run can propose it once it works. A test command is never optional: without one, `build` has no baseline, so setup proposes no instructions file until one works (section 5).

When a command needs a secret, do not ask for it in chat. Name the variable or file it reads, and ask the owner to put the value in an environment variable or a file outside the repository.

Running the commands can change files (a lockfile, a build folder). None of that goes into setup's pull request, which carries the instructions file and nothing else.

Note where the session runs, as `build` does. In the cloud it cannot build native apps, run simulators or grant device permissions, so a command that needs those is one the owner proves on their machine, and the report says so. On the owner's machine, ask before installing a tool a command needs, and never run anything that would put a system permission prompt on their screen. The report says where the session ran.

## 2. Ask only what the repo cannot say

The repo cannot say how the app reaches users or where to check that it works, so those are normally the only questions. Ask them in one message, numbered, each with a default drawn from what the repo shows, so the owner can answer by number or say "ok" to take every default:

```
1. How does the app reach users? Default: the hosting deploys `main` on merge and builds a preview per pull request (its config file is in the repo).
2. Where do you check it live? Default: nothing to check yet.
```

Skip a question the repo already answers, for example when the README names the deploy and the live URL. "Nothing yet" is an answer, not a gap: `ship` will then say merged, not deployed. The only other questions are the tracker's (section 4) and the yes on the draft (section 5).

Never ask for a secret in chat, not even one the deploy uses. The hosting or CI keeps its own credentials, and no skill deploys by hand.

## 3. Verify connections, never create them

Check each connection the loop needs by using it, read-only:

- **The tracker can be read.** List the Linear teams. Without a Linear connector every skill falls back to the chat; report it and say to add the connector to the sessions that run the skills.
- **A branch can be pushed.** Run `git push --dry-run origin HEAD:refs/heads/factory-setup-check`: it checks access and pushes nothing. When setup opens its pull request, that push proves it for real. Without push access `build` cannot open a pull request; say to give the session write access to the repository.
- **The hosting is visible**, when the repo shows any (a config file, a deploy workflow, a live link in the README). Use a hosting tool the session already has to see the project and its last deploy, or load the live URL. When neither works, `ship` can merge but cannot watch the deploy; say to connect the hosting to the sessions.

Never create an account, a token, an integration or a hosting project to make a check pass. Report exactly what is missing and where the owner connects it.

## 4. Check the tracker

Skip this section when the tracker cannot be read; section 3 already reported it.

- **The team.** Use the one team when there is one. When several could fit, ask which, with the one whose name or existing issues match the repository as the default. Never create a team: with none, say where to create one in Linear's settings.
- **The project.** Look for a project for this repository, by its name or by a link to the repository. Reuse a match; when several match, ask which. With none, ask whether to create one named after the repository, and create it only when the owner says yes in this session: silence is not a yes. `ideate` files ideas into this project.
- **The statuses.** The loop moves issues through Backlog, Todo, In Progress, In Review and Done: `ideate` files into Backlog or Todo, `build` moves them to In Progress and In Review, `ship` to Done. The team's own names count when they mean the same step, such as "Ready" for Todo or "Code review" for In Review. Never create or rename a status: report a missing one and say to add it in the team's workflow settings.
- **Pull requests linking to issues.** `build` names its branch the way Linear suggests so the pull request links itself to the issue. That needs Linear's integration with the code host, which a session usually cannot see; when it cannot, list it as an owner check, not a gap.

## 5. The instructions file

Every later agent obeys this file, so only the owner changes it. That is why setup never writes it directly: it drafts, the owner reads the draft here, and the file reaches the repository through a pull request the owner merges. The pull request also proves that setup can push a branch and open one, which `build` depends on.

The file is `AGENTS.md` at the root, or `CLAUDE.md` when that is what the repo uses. When `CLAUDE.md` only points to `AGENTS.md`, the file is `AGENTS.md`.

The template. Its sections are what `build` reads in preflight and what `ship` follows after a merge:

````markdown
# <repository name>

How to work in this repository. Agents follow this file; the owner changes it.

## Install
`<command>`

## Run
`<command>`, and how to tell it is up (the port, the ready line). Or: nothing to run, this is a library.

## Test
`<command>`

## Lint
`<command>`. Or: no linter in this repository.

## Deploy
How the app reaches users: the hosting deploys `main` on merge and builds a preview per pull request; a workflow ships a build when <trigger>; or nothing yet.

## Check live
The URL or health endpoint to load after a deploy, and what a healthy answer looks like. Or: nothing to check yet.

## Tracker
Linear team: <name> · Project: <name>
Statuses: the defaults, or the team's names for them when they differ.
````

Each section holds a command setup ran and saw work, an answer the owner gave, or a plain statement that the repo has none. A section setup could not prove is left out, never filled with a guess.

**Not without a test command.** When the Test section could not be proven, propose nothing yet. `build` stops in preflight without it, and a file that lacks it would look finished. The report names the gap, and the run after it is fixed proposes the whole file.

**No file yet.** Draft it from the template and show it to the owner in the session. If they ask for changes, make them and show it again; a change they ask for is theirs, even a command setup could not prove, which the report then marks as unproven. On their yes, create the branch `factory-setup` from the default branch, commit only the instructions file, push, and open a pull request titled "Add the agent instructions file", with what setup proved and how in the body. When the session has no way to open a pull request, push the branch and tell the owner to open one from it. Never commit to the default branch, and never merge the pull request: merging is the owner's act.

**A file already exists.** Never rewrite it. Prove its commands as in section 1, then compare it to the template by meaning, not by heading: a Commands section that gives the test command covers Test. List the gaps. When sections are missing, propose only those, appended at the end, and on the owner's yes deliver them the same way, in a pull request whose diff only adds lines. A command in the file that no longer works is a finding for the report, not a change setup makes. When nothing is missing, open nothing.

**An earlier run's pull request.** Look for a `factory-setup` branch or pull request before creating one. When one is open, link it in the report and leave it alone. When one was closed without merging, the owner said no once: ask before proposing again.

**The write is blocked.** A harness may block the write as instruction poisoning, or refuse the permission. Do not look for another route: give the full draft in chat for the owner to commit themselves, and say so in the report.

## 6. Branch protection

Read the protection on the default branch when the session can see it, and say "not checked" when it cannot. Recommend a minimal rule: pull requests required, the CI checks required when there is CI, no force-push and no deletion. Do not recommend a required review when the owner works alone: nobody could approve their pull requests, and `ship` never goes around a protection.

Never change the setting. It needs admin rights a session should not have, and it is the owner's choice. The skills never push to the integration branch anyway, so missing protection is a recommendation in the report, not a gap.

## 7. Report

When nothing is missing, the report is one line:

```
Ready: install, run, test and lint proven · deploys on merge, checked at <URL> · Linear <team> / <project> · session: cloud
```

When the only thing left is setup's own pull request, the line starts "Ready when you merge <link>".

Otherwise say "Not ready" and give a table with one row per gap:

````markdown
## Not ready
| Missing | Why it matters | Where to fix it |
|---|---|---|
| A test command | `build` runs the suite before and after every change, and stops without one | Add a test script, then say "setup" again |
| The Linear connector | Every skill reads and writes the issue | The connectors of the sessions that run the skills |

Instructions file: <pull request link, or "draft in chat"> · Proven: install, run · Session: cloud
Recommended: <branch protection rule, failing tests, anything else worth fixing>
````

End with a ping short enough for a phone notification: ready or not, how many gaps, the pull request link, and the next step, which is to merge the pull request, fix the rows, or say "setup" again to re-check. When section 8 makes an offer, it goes in the same message, just before the ping.

## 8. First ticket

Offer one, do not force it. A first ticket runs the whole loop once and shows what still slows it down. Offer it only when the report says ready, or ready once the pull request merges, and the project has no issues yet. An issue in the project means the loop has already started, so a re-run offers nothing.

Make the offer one line with one small idea grounded in what you read: a missing test for a function you saw, a README step that is out of date, a lint warning. Pick something that fits one pull request and has code to read, so `ideate` can take the fast lane. On the owner's yes, or with their own idea in its place, hand the idea to `ideate` exactly as if the owner had said it. `ideate` files it; setup writes no spec of its own.

## Never

- Write to the default branch, or merge setup's own pull request.
- Rewrite an existing instructions file, or change a line already in it.
- Create a team, a status, a repository or a hosting project. A Linear project is the one thing setup creates, and only on the owner's yes.
- Change repository settings, such as branch protection.
- Ask for a secret in chat. A secret belongs in a file outside the repository or an environment variable; one pasted anyway is reported as needing rotation.
- Copy third-party skills into the repository.

Setup does not install the plugin (if setup is running, it is installed), create the repository or the hosting project, or make the scratch folder, which `build` makes for itself.
