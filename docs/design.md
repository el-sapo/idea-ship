# Design

How the factory works and why it is shaped this way. The skills themselves, under `plugins/idea-ship/skills/`, are the source of truth for what agents do; this page explains the shape around them.

## What it is for

A lean, repeatable way to take an idea to shipped code with agents doing most of the work, where a handoff between sessions never depends on someone remembering a chat. The constraints it was designed under:

- **Lean.** Not an enterprise process. No big tickets with test cases, no points, no ceremonies. A process, and speed, but robust enough to trust.
- **Phone first.** The idea is given by voice in a short session, often away from a desk, and the agent then works alone in the cloud or on a machine.
- **Centralised.** Nobody traces back through chat sessions to find where something was discussed. The work has one place.
- **Visual.** The first answer to an idea uses diagrams and a light mockup, and is direct, so the person can steer fast.
- **Autonomous agents that speak up.** The agent decides how much detail a ticket needs, and is loud about what needs attention.
- **Loose over strict.** No locked templates for how things look. Trust the agent and correct it when needed.
- **Shareable.** Something a friend with no process, or a startup of three to five developers, could adopt in an afternoon.

## The rule

**The Linear issue is the thread, and sessions are disposable.** Every run in the loop starts by reading the issue and ends by writing to it; `setup`, which readies a project before there is an issue, ends with a report in the session instead. That one rule is what makes the rest work: any session can continue from the issue and the branch, so the orchestrator, a phone session and a terminal session are interchangeable.

## Setup

`setup` runs once per project, and again when asked, outside the four moments the person triggers. It readies the repo for the loop: it proves the install, run, test and lint commands by running them, asks only how the app deploys and where to check it live, checks the connections and the Linear team, project and statuses, and reports ready or what is missing and where to fix it. It remembers nothing between runs, so a re-run checks everything again and, on a ready repo, changes nothing.

The instructions file is what every later agent obeys, so a change to it is a change to every agent. That is why setup never writes it directly: it proposes the file, or only the sections an existing one is missing, as a pull request the owner merges, and it never rewrites what is already there. The owner stays the only one who changes the file, and the pull request also proves the session can push and open one, which `build` depends on. When a harness blocks the write, setup gives the draft in chat for the owner to commit. It verifies connections without creating them and reads branch protection without setting it, because accounts and repository settings are the owner's to grant, and a session should not hold admin rights. No tracker is not a gap: setup suggests connecting Linear each time it runs, and the repo can still be ready. Setup is the one place that suggests a tracker; the other skills never ask for one.

## The loop

One skill per stage. The person speaks, the agent works alone, and the result lands on the issue.

| # | The person says | Skill | The agent does alone | Lands on the issue | Status after |
|---|---|---|---|---|---|
| 1 | An idea | `ideate` | Visual read-back at once, then explores and prepares options | Idea, flow, attention items, options, numbered decisions | Backlog |
| 2 | "1 B, 2 ok, option A. Spec it" | `spec` | Grounds the pick in the code, flags risks, sizes it, writes checks an agent can verify | The spec replaces the description; the options move to a comment | Todo |
| 3 | "Code ABC-12" | `build` | Branch, plan, tests first, code, review, verification, pull request | A report comment with evidence per check | In Review |
| 4 | "Ship ABC-12" | `ship` | Checks it is ready, merges, watches the deploy, checks it live | A close-out comment with what is next and factory notes | Done |

Every status where an issue rests (Backlog, Todo, In Review) is the person's turn. In Progress means an agent is working. Linear's default statuses are enough; nothing custom is needed.

## Lanes

`ideate` picks one of three lanes. Its read-back names the lane it expects, as a forecast from the idea alone, and reading the code settles it.

- **Options** is the default and is the loop above.
- **Fast** is for an idea that is small and clear. `ideate` skips the options and files a ready-to-build spec in Todo, so the person speaks three times: the idea, "code", "ship". All five conditions must hold: it fits one pull request; there is one obvious way to do it; nothing on the vocal list earns a card; no decision is open; there is code to read.
- **Parked** is for an idea that cannot move yet, or that the person only wants noted. It goes to Backlog with a "Waiting for" section, with no options and no decisions.

Rules that came out of testing the lanes with fresh agents:

- A decision is open when the person could reasonably answer either way and would notice the difference in the product. A small choice takes a default and is recorded.
- What the person asked for in so many words is not a finding. Its side effects can be.
- An idea moves to the fast lane after the read-back only if exploring removed every card and every decision the read-back raised. A decision already put to the person is theirs to answer.
- The person's words choose the lane: "fast", "options", "park it". If they ask for fast and a condition fails, the agent stays on options and says which.
- When exploring leaves the agent unsure, it takes the options lane.

## Foundations

Some ideas introduce something other work will reuse: a design kit (tokens, type scale, spacing, radii, shared primitives), a shared data layer, auth, a shared component. `ideate` and `spec` both flag this as a **Foundation** card. A foundation is filed as its own issue and built first, with the feature issues blocked on it, so it always rules out the fast lane. When options exist, every option builds on the same foundation and the options differ in what is built on it.

A foundation's spec covers three things: the document a later agent will read (the design-system doc, the data layer's shape), a propagation check that proves the foundation is used where it should be, and one `Owner:` check that the repository's instructions file points to that document. Agents never edit that file, and a later build reads only what it points to.

## Features

`feature` is the orchestrator for a parent issue whose sub-issues are specced and ordered. It plans the run, waits for approval on how far it goes, and then runs one fresh `build` worker per sub-issue on a feature branch, verifies each with a fresh reviewer, folds it into the feature branch, and hands back one pull request.

- **The plan is the contract.** A "Feature plan" comment lists the steps, the worker per step (model and effort from the sub-issue's complexity), what each step builds on, the reviewers per step, the checks, the stops, and numbered decisions. Nothing starts before "go". A default that changes how the result reaches the integration branch is never silent.
- **One worker per step, fresh context.** The worker is a child: a subagent or a background `claude -p "code ABC-48"` run. Its return is the signal that it finished. The orchestrator reads its report on the issue, never its transcript, so its own context stays small. No event bus, no polling.
- **Verify before integrating.** A smaller model checks the worker's report against the spec: evidence re-run, owner checks match, diff in scope and matching the report, nothing that changes a shape a later step builds on. One reviewer by default; two (one re-runs evidence, one takes the rest) when the step is high complexity, depends on an integration, or touches many areas.
- **The feature branch is the sandbox.** Created at "go" from the integration branch (`main`, or a long-lived branch the person names). Step 1 builds on it, each later step builds on the previous step's branch, and every step's pull request targets the feature branch, so there is one stable base and no retargeting: once a step merges, the next pull request shrinks to its own diff. Verified steps merge into the feature branch as the run goes, unless the person says "steps on my word". Nothing deploys from it.
- **One final pull request.** At the stop line the orchestrator merges the integration branch into the feature branch, runs the full suite, opens the feature branch's pull request into the integration branch, and moves the parent to In Review. "Ship" on the parent is the one approval that deploys.
- **Stops are explicit.** The approved stop line, holds on owner checks, two failed verification rounds, a worker Handoff, a report that changes a shape a later step builds on. A name that differs between a spec and the code is a recorded decision, not a stop. For anything else it decides and records.
- **Never merges into the integration branch.** That is `ship`'s and the person's.

On the person's machine, when the checkout is in use, the orchestrator makes a worktree for the run and hands workers its path; `build` itself never creates one. Secrets a spec needs go in a file or an environment variable the worker reads; no skill asks for one in chat, and one pasted anyway is reported as needing rotation.

The worker mapping: low complexity runs Opus at medium effort, medium at high, high at xhigh with ultracode when the session can start a worker that way. The person can state different mappings and the plan uses theirs.

## When a ticket leaves the straight path

- **The person asks for changes.** At In Review they say what to change in place of "ship". `build` takes it on the same branch and reports again. `ship` will not merge an approval that carries a code change.
- **The spec is larger than one pull request.** `spec` splits it into sub-issues in build order. Each `build` run does one, or `feature` runs them all. `ship` names the next unblocked one and closes the parent when all are Done.
- **Build has to stop.** It pushes the branch as it is and posts a Handoff comment (Done, Open, Check, Next). The issue stays In Progress, and the next session continues from the issue and the branch.
- **The deploy fails.** `ship` finds out what users see, opens a revert pull request without merging it, posts "Not live" and pings at once. The issue stays In Review. Reverting is the person's call.
- **A merge has to be proven.** After any merge, `ship` and `feature` check `git merge-base --is-ancestor`. A pull request's merged state is not proof that the commits reached the branch the person expects, and Linear moves an issue to Done on a merge into any branch.
- **The session is on the person's machine.** Installing a tool the build needs is a decision to record. Anything that would put a system permission prompt on their screen is a stop. The report says where the session ran.

## How agents present things

Whatever an agent shows is one visual page, laid out for a phone, built from the parts the idea needs: what it understood, how it works (flow diagrams), what it looks like (grey-box mockups), what needs attention (one card per item), and numbered decisions the person answers as "1 B, 2 ok".

Two tags, `Complexity` and `Risk of breaking`, each low, medium or high, coloured green, amber or red with the word always printed.

The **vocal list** is what agents are loud about, at every stage:

- behaviour change: something that works today will work differently, or stop
- risk of breaking existing features, data, integrations or other clients
- security and privacy
- data that cannot be undone
- a design problem, said plainly, with the better shape
- cost and dependencies
- a scope surprise
- a shaky assumption
- a foundation: something other work will reuse

The test for whether something earns a card: would the person be surprised or annoyed to learn it only after the build? Routine work gets no card, because if everything is flagged, flags get ignored.

## Where the person is in the loop

| Issue rests in | They look at | They say | Their word approves |
|---|---|---|---|
| No issue yet: the project is not set up | Setup's report and its pull request | "setup", then merge | The instructions every agent follows |
| Not filed yet | The read-back, if they are still there | The idea | Starting the work |
| Backlog | The options page | "1 B, 2 ok, A. Spec it" | The direction. Skipped on the fast lane |
| Todo | The spec in Linear, which they can edit | "Code ABC-12" | What gets built. This is where their time pays off most |
| Feature plan | Steps, workers, reviewers, stop line, holds | "go", or "3: after step 2, go" | How far the orchestrator goes |
| In Review | The pull request, the preview and the report | "Ship ABC-12", or the changes they want | The merge, which is also the deploy |
| In Review, a feature's parent | The final pull request, the preview and the "Feature built" report | "Ship ABC-47", or changes on a step | The merge of the whole feature, which is the deploy |
| In Review, after a failed deploy | The "Not live" comment and the revert pull request | Merge the revert, or not | Rolling back |

**Agents stop and ping** when an operation cannot be undone; when the work touches secrets, credentials, payments or permissions beyond the spec; when a discovery changes what was approved; when the plan is so broken that every path is a guess; when the issue has no spec; when a readiness check fails before a merge; and on the person's own machine, when a system permission prompt would appear. For anything else the agent decides, records the call under Decisions, and keeps going. A question with a recorded default never blocks a build.

**Agents never** merge during `build` or push to the integration branch outside `ship`; weaken a test to get to green; force a merge or use admin rights; deploy by hand or touch production data; merge a revert; edit a repository's instructions file (setup only proposes it, through a pull request the owner merges) or copy third-party skills into a repository; commit specs, plans or ledgers; ask for a secret in chat; or start two workers on the same files at once.

The production rule has one shape of exception, and it is not a rule change: when a run stops on it and the person, in the session, reads the stated risk and says to continue, the agent continues. It never happens unattended, and the stop and the risk come first.

## What each step generates

Decisions and reports live on the Linear issue. Only code is committed, plus the instructions file that `setup` proposes for the owner to merge.

| Skill | Output | Where it lives |
|---|---|---|
| `setup` | Report: ready, or what is missing and where to fix it | Inline in the chat |
| `setup` | Instructions-file pull request | GitHub, left for the owner to merge |
| `setup` | A Linear project for the repository, only on the owner's yes | Linear |
| `ideate` | Visual read-back | Inline in the chat |
| `ideate` | Options page | A published page, linked from the issue |
| `ideate` | The issue: options, a ready spec, or a parked note | Linear, assigned to the person |
| `spec` | Spec: Goal, Decision, Scope, Flow, Needs attention, Done when, Plan, Decisions | Linear, as the issue description |
| `spec` | "Options considered" comment | Linear |
| `spec` | Sub-issues in build order, only when larger than one pull request | Linear |
| `spec` | Attention page, only when something needs the person's eyes | A published page or inline |
| `build` | Spec copy and task plan | `.factory/plans/` in the working copy, ignored by git, never committed |
| `build` | Branch, code and tests | GitHub, committed |
| `build` | Pull request | GitHub |
| `build` | Report: Built, Checks, Needs attention, Decisions, Follow-ups | A Linear comment, plus a visual report page |
| `build` | Follow-up issues for problems outside the scope | Linear, Backlog |
| `build` | Handoff comment, only if it has to stop | Linear |
| `feature` | "Feature plan" comment and a visual plan | Linear, on the parent |
| `feature` | Feature branch, with the verified steps merged into it | GitHub |
| `feature` | "Feature run" comment, updated per step | Linear, on the parent |
| `feature` | The final pull request, feature branch into integration branch | GitHub |
| `feature` | "Feature built" report | Linear, on the parent |
| `ship` | Merge | GitHub |
| `ship` | Close-out: Shipped, Checked live, Answers, Next, Factory notes | A Linear comment |
| `ship` | Revert pull request, only if the deploy fails | GitHub, left unmerged |

Factory notes are one line for anything that made a ticket harder than it should have been. They are the raw material for improving the skills. Nothing reads them yet; see Parked below.

## Principles written into the skills

- Pictures steer faster than paragraphs.
- Depth follows the idea. The agent decides how much to show.
- Loud about what needs attention, quiet about the rest.
- Evidence, not claims. A check has passed only when something was run and seen to pass. Checks only the owner can run are counted apart.
- Only code is committed, plus the instructions file the owner merges from `setup`.
- Decide what you can, stop for what you must.
- One approval covers one pull request. Merging is the deploy, so agents need no production credentials.
- The plan is the contract. An orchestrator builds nothing before the plan is approved, and stops where the plan says.

## Decisions, and what was rejected

| Decided | In place of | Why |
|---|---|---|
| Four moments the person triggers, one skill each | Seven stations and a core plugin with tracker, version-control and stack adapters | Too heavy, and the core plugin was unclear |
| An async, phone-first flow | A set of terminal commands for a team | It is how the work actually happens. The team layer is parked |
| The Linear issue carries everything | A handoff command or note | Every run already ends by writing to the issue |
| The agent decides the depth | Fixed limits (one sentence, a word count) | Not every ticket is that small |
| No fixed look for the pages | A style template | Loose over strict; correct when needed |
| The spec stays in Linear, never in the repository | Living specs in the repository | Linear already holds the spec; a second home would be a second truth |
| `build` keeps its own discipline: tests first, a fresh reviewer, evidence | Copies of third-party execution skills in every repository | The by-hand path was enough on every real run, and the copies added a dependency and a version to track |
| Platform facts live in the repository's instructions file; the skills name no platform | Deploy steps or platform adapters inside the skills | Every app deploys differently, and a platform written into a skill breaks the next app |
| Agents never edit a repository's instructions file; setup's one route is a pull request the owner merges | The agent adding to it | An agent's attempt was blocked as instruction poisoning in a test, and it should be |
| `setup` proposes the instructions file, or its missing sections, as a pull request the owner merges | `setup` writing the file, or rewriting it on a re-run | Every later agent obeys it, so the owner stays the only one who changes it; the pull request also proves push access; and a harness had blocked a direct write as instruction poisoning |
| `setup` checks branch protection and recommends a rule | `setup` setting it | It needs admin rights, and it is the owner's choice |
| `setup` suggests a tracker on its own runs and never blocks on it | A missing tracker as a gap, or a reminder from every skill on every run | The skills already fall back to the chat; setup is the place to suggest one, and only there |
| A fast lane in `ideate` | Every idea going through options and a spec turn | Taken from Warp Factories' triage step (implement, spec or wait) |
| Visual proof in `build` stays a soft rule | Making it mandatory | Production is a single person for now |
| No scoring of runs | Two facts recorded on each close-out | It would make the flow more complex |
| An orchestrator that is itself a skill | A platform orchestrator (Warp, Projects, agent teams) | The issue already carries everything, so a skill with a worker per step is enough, and it runs wherever the skills run |
| A plan approved before any worker starts | Running to the end by default | How far an unattended run goes is the person's call |
| A feature branch per feature, one final pull request | Step pull requests stacked on each other and shipped one by one into the integration branch | The first real run showed that stacked pull requests do not retarget themselves; a feature branch gives every step one stable base, keeps half a feature off the integration branch, and makes the deploy one approval |
| The orchestrator merges verified steps into the feature branch | Approving each step's merge | Nothing deploys from the feature branch, so the merge is integration, not release; "steps on my word" keeps the other option |
| One reviewer by default, two on complex or integration-heavy steps | Two reviewers on every step | Two found real things on the first run, but at a token cost that only pays on the risky steps |
| Owner checks counted apart | Reporting them as not passing | "3 of 6 passed, 3 owner" says what it means; "3 of 6" does not |
| The plugin directory is the distribution for Claude surfaces; the git marketplace stays for Codex, Cursor and following `main` | Skill copies saved on the account, or a git marketplace added on claude.ai, to reach cloud sessions | A directory install syncs to the account, so it reaches chat, Cowork and every Claude Code session, and it updates when a version is published; copies had to be re-saved after every change, and an old copy kept answering beside the new one |

## Parked

Thought through and not built:

- **A skill that reads the factory notes.** `ship` writes one line per friction on every close-out, and nothing reads them. A skill could read those notes and the owner's corrections across recent issues and propose skill edits. A necessity for any factory in the long run, and a token cost, so a nice-to-have for now.
- **A team layer for three to five developers.** Ticket ownership and a limit on work in progress, one teammate's review after the agent's, autonomy levels per repository, a release step.
- **Other trackers.** The issue templates are Linear-shaped. A tracker adapter would let the same skills read and write another tool; until then the chat fallback is the only alternative.
- **Parallel steps in `feature`.** v0.1 runs steps one at a time. Independent sub-issues could run at once, on separate files.

Considered and declined: mandatory visual proof in `build`; scoring each run; benchmarks re-run when a skill changes; a foreman agent that routes work (the person is the router).

## Tested, and not

Tested on real tickets: `ideate`, `spec` and `build` end to end on a native desktop app and on a multiplatform app, including a run on the person's machine with a tool install and an owner-only permission check; `feature` on a multi-issue feature. Tested in dry runs with fresh agents: the three lanes, the Foundation card, the feature plan against a fixture of four sub-issues, `build` with and without a subagent tool.

Not tested yet: `ship` against hosting that deploys on merge; a fast-lane spec going through `build`; the Codex manifest; `feature` continuing from a "Feature run" comment in a later session; `setup` on a real repository, tried only in dry runs against three fixture repositories (fresh, ready, missing pieces).

## Known gaps

Found on real runs and not fixed yet. Each has a workaround.

- **Workers without a subagent tool self-review.** When a worker runs somewhere it cannot start a fresh reviewer, `build`'s whole-branch review is a self-review and its report says so. `feature`'s own reviewer covers the gap; a single `build` run does not have that cover, so read the report harder.
- **The feature branch flow has not run on a real feature yet.** 0.2.0 replaced stacked pull requests with a feature branch after the first real run exposed the retarget problem. Until a feature has gone through it, check the final pull request's diff against the steps before shipping it.
