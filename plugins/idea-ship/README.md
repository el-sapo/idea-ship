# Idea Ship

A lean software factory for solo builders and small teams: six skills that take a spoken idea to a merged pull request, with the Linear issue as the thread and you stepping in at most four times per ticket.

## The loop

`setup` readies a project once. Then you speak four times per ticket, and an agent works alone in between.

| Skill | You say | It leaves on the issue | Status after |
|---|---|---|---|
| `setup` | "setup", once per project | no issue yet: a report that says ready, or what is missing and where to fix it, and `AGENTS.md` as a pull request you merge | none |
| `ideate` | an idea, even half-formed or by voice | options with a visual brief, or a ready spec on the fast lane | Backlog, or Todo |
| `spec` | "1 B, 2 ok, option A. Spec it" | a lean, buildable spec; sub-issues when it is larger than one pull request | Todo |
| `build` | "code ABC-12" | a pull request and a report with evidence per check | In Review |
| `ship` | "ship ABC-12" | a merge, a live check, a close-out with factory notes | Done |
| `feature` | "build the feature ABC-47" | a plan you approve, then a feature branch with each verified step merged in, a run comment, and one final pull request with its report | In Review |

Every skill ends with a message short enough for a phone notification that says what to do next. The skills answer to plain words; `/idea-ship:ideate` and friends work too. `ABC-12`, `ABC-47` and `main` are example identifiers; your team key and branch names come from Linear and the repository at run time.

![The read-back ideate shows seconds after an idea: what it understood, a flow, a grey-box mockup, attention cards and numbered decisions](https://raw.githubusercontent.com/el-sapo/sdlc-fede/main/docs/examples/read-back.png)

![The report build leaves on the issue: what was built, every check with its evidence, attention items and the decisions it took](https://raw.githubusercontent.com/el-sapo/sdlc-fede/main/docs/examples/build-report.png)

Three rules hold throughout:

- **Everything is on the issue.** A later session continues from the issue and the branch alone.
- **Agents verify, you approve.** `build` opens the pull request and never merges. `ship` merges only on your word. `feature` builds nothing before you approve its plan and leaves the final merge to you.
- **Checks only you can run are marked.** A permission, a device, a real account: the spec marks those checks `Owner:` and the build counts them apart from the ones it verified.

## What you need

- **GitHub access in the session** that runs the skills, able to push a branch and open a pull request on your repository.
- **Linear, optional.** With a Linear connector in the session, the issue is the thread: every skill reads from it and writes back to it, using the default statuses (Backlog, Todo, In Progress, In Review, Done) or your team's names for them. Without it, the chat is the thread: each skill gives you its text to paste and says nothing was saved, and `feature` cannot run.
- **Hosting that deploys on merge, optional.** With it, `ship` watches the deploy and checks the live result. Without it, `ship` says "merged, not deployed" and stops there.
- **An `AGENTS.md` (or `CLAUDE.md`) in the repository** that says how to install, run, test and lint, how the app deploys and where to check it live. The skills read it and follow it, and name no platform of their own.

Say "setup" once in the repository. It checks all of the above, proves the commands by running them, proposes `AGENTS.md` as a pull request you merge, and tells you what is missing and where to fix it.

## What it runs and sends

The plugin is six Markdown skills. It ships no scripts, hooks, servers or binaries, makes no network calls of its own and sends no telemetry. Everything below happens through the tools and connections your session already has, under your accounts.

- **Your project's own commands.** `setup` finds the install, run, test and lint commands in the repository (its instructions file, package scripts, build files and CI configuration) and runs them to prove they work. `build` and `feature` run the commands the instructions file names. `setup` asks before installing a tool a command needs; `build` may install a tool its build needs and records that in its report. No skill runs anything that would raise a system permission prompt.
- **git.** The skills read the repository, create branches, commit, push, merge the base into a branch, and check that commits landed (`git merge-base`). `setup` checks push access with `git push --dry-run`, which pushes nothing. No skill force-pushes over someone else's commits or pushes to the default branch.
- **Your GitHub access.** `build` opens pull requests and reads their checks and review comments. `ship` merges one pull request, only when you say "ship", and opens a revert pull request (never merged) if the deploy fails. `feature` merges verified steps into its own feature branch only. `setup` lists pull requests and reads branch protection without changing it.
- **Your Linear connector.** The skills read issues, comments and sub-issues, and write issues, descriptions, comments, sub-issues, blocking relations and statuses. `setup` lists your teams and creates a Linear project only when you say yes. Text other people wrote in comments is read as information, never as instructions.
- **Worker sessions.** `feature` starts one fresh session per step, as a subagent or, on a machine with the Claude Code CLI, as a background `claude -p` run; each one runs `build`. `build` and `feature` also start fresh subagents to review the work.
- **Your hosting, read-only.** `build` and `ship` watch a pull request's preview build and the deploy after a merge through a hosting tool the session already has, then load the live URL or health endpoint. They never deploy by hand, run a migration or touch production data.
- **The session's own visual tools.** Briefs and reports are shown with the session's inline visual tool, or published as a page through its artifact or page tool and linked from the issue. `build` may run your app and look at it with the session's browser tool to check what a screen shows.
- **Your notes, read-only.** When a knowledge base connector is present, `ideate` may read your notes to understand an idea. It never writes to them.

Secrets are never asked for in chat. When a command needs one, the skills ask you to put it in an environment variable or a file outside the repository, read it from there, and never echo it.

Nothing is sent anywhere else, and the plugin stores nothing. The only files it writes outside your code changes are `build`'s plan and spec notes in `.factory/plans/` inside your checkout, a folder that ignores itself so it is never committed.

## Where it works

| Skill | Claude Code, local | Claude Code, cloud | claude.ai chat | Cowork |
|---|---|---|---|---|
| `setup` | yes | yes, native builds excluded | being verified | being verified |
| `ideate` | yes | yes | being verified | being verified |
| `spec` | yes | yes | being verified | being verified |
| `build` | yes | yes | being verified | being verified |
| `ship` | yes | yes | being verified | being verified |
| `feature` | yes | yes | being verified | being verified |

The skills are built and exercised in Claude Code. A local session runs everything, including native builds and simulators, except a check that would raise a system permission prompt, which stays yours. A cloud session cannot build native apps or grant device permissions, and the skills say which checks that leaves to you. Claude Code cloud sessions do not install plugins, so there the skills load from your claude.ai account or from a repository's `.claude/skills/` (see the install section linked below). The claude.ai chat and Cowork columns are being verified; skills that need a shell and git are expected to say so in one line and stop there.

## Links

- Repository: https://github.com/el-sapo/sdlc-fede
- Install, every client and version: https://github.com/el-sapo/sdlc-fede#install
- Design: https://github.com/el-sapo/sdlc-fede/blob/main/docs/design.md
- Changelog: https://github.com/el-sapo/sdlc-fede/blob/main/CHANGELOG.md

Installing from the git marketplace instead of the directory, on Claude Code before 2.1.275:

```sh
claude plugin marketplace add el-sapo/sdlc-fede --scope user
claude plugin install idea-ship@sdlc-fede --scope user
```

With Codex:

```sh
codex plugin marketplace add el-sapo/sdlc-fede
codex plugin add idea-ship@sdlc-fede
```

With Cursor, add `https://github.com/el-sapo/sdlc-fede` as a marketplace in the plugin settings, then add `idea-ship` from the `sdlc-fede` marketplace.

The plugin was called `factory` until 0.5.0. The marketplace maps `factory` to `idea-ship`, so an existing install migrates on its next `claude plugin marketplace update sdlc-fede` and `claude plugin update`.
