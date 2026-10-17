# Design

How the factory works and why it is shaped this way. The skills themselves, under `plugins/factory/skills/`, are the source of truth for what agents do; this page explains the shape around them.

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

**The Linear issue is the thread, and sessions are disposable.** Every agent run starts by reading the issue and ends by writing to it. That one rule is what makes the rest work: any session can continue from the issue and the branch, so the orchestrator, a phone session and a terminal session are interchangeable.

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

`feature` is the orchestrator for a parent issue whose sub-issues are specced and ordered. It plans the run, waits for approval on how far it goes, and then runs one fresh `build` worker per sub-issue, verifies each with a fresh reviewer, and keeps the state on the parent.

- **The plan is the contract.** A "Feature plan" comment lists the steps, the worker per step (model and effort from the sub-issue's complexity), the base branch per step, the checks, the stops, and numbered decisions. Nothing starts before "go".
- **One worker per step, fresh context.** The worker is a child: a subagent or a background `claude -p "code ABC-48"` run. Its return is the signal that it finished. The orchestrator reads its report on the issue, never its transcript, so its own context stays small. No event bus, no polling.
- **Verify before moving on.** A smaller model checks the worker's report against the spec: evidence per check, owner checks match, diff in scope, nothing that changes a later step.
- **Chained branches.** Each step builds on the previous step's branch, so no step waits for a merge. The chain is shipped in order at the end, with the retarget caveat under Known gaps.
- **Stops are explicit.** The approved stop line, holds on owner checks, two failed verification rounds, a worker Handoff, a report that changes a later step. For anything else it decides and records.
- **Never merges.** Shipping stays one approval per pull request.

The worker mapping in v0.1: low complexity runs Opus at medium effort, medium at high, high at xhigh with ultracode when the session can start a worker that way. The person can state different mappings and the plan uses theirs.

## When a ticket leaves the straight path

- **The person asks for changes.** At In Review they say what to change in place of "ship". `build` takes it on the same branch and reports again. `ship` will not merge an approval that carries a code change.
- **The spec is larger than one pull request.** `spec` splits it into sub-issues in build order. Each `build` run does one, or `feature` runs them all. `ship` names the next unblocked one and closes the parent when all are Done.
- **Build has to stop.** It pushes the branch as it is and posts a Handoff comment (Done, Open, Check, Next). The issue stays In Progress, and the next session continues from the issue and the branch.
- **The deploy fails.** `ship` finds out what users see, opens a revert pull request without merging it, posts "Not live" and pings at once. The issue stays In Review. Reverting is the person's call.
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
| Not filed yet | The read-back, if they are still there | The idea | Starting the work |
| Backlog | The options page | "1 B, 2 ok, A. Spec it" | The direction. Skipped on the fast lane |
| Todo | The spec in Linear, which they can edit | "Code ABC-12" | What gets built. This is where their time pays off most |
| Feature plan | Steps, workers, stop line, holds | "go", or "3: after step 2, go" | How far the orchestrator goes |
| In Review | The pull request, the preview and the report | "Ship ABC-12", or the changes they want | The merge, which is also the deploy |
| In Review, after a failed deploy | The "Not live" comment and the revert pull request | Merge the revert, or not | Rolling back |

**Agents stop and ping** when an operation cannot be undone; when the work touches secrets, credentials, payments or permissions beyond the spec; when a discovery changes what was approved; when the plan is so broken that every path is a guess; when the issue has no spec; when a readiness check fails before a merge; and on the person's own machine, when a system permission prompt would appear. For anything else the agent decides, records the call under Decisions, and keeps going. A question with a recorded default never blocks a build.

**Agents never** merge during `build` or push to the default branch; weaken a test to get to green; force a merge or use admin rights; deploy by hand or touch production data; merge a revert; edit a repository's instructions file or copy third-party skills into a repository; commit specs, plans or ledgers; or start two workers on the same files at once.

## What each step generates

Decisions and reports live on the Linear issue. Only code is committed.

| Skill | Output | Where it lives |
|---|---|---|
| `ideate` | Visual read-back | Inline in the chat |
| `ideate` | Options page | A published page, linked from the issue |
| `ideate` | The issue: options, a ready spec, or a parked note | Linear, assigned to the person |
| `spec` | Spec: Goal, Decision, Scope, Flow, Needs attention, Done when, Plan, Decisions | Linear, as the issue description |
| `spec` | "Options considered" comment | Linear |
| `spec` | Sub-issues in build order, only when larger than one pull request | Linear |
| `spec` | Attention page, only when something needs the person's eyes | A published page or inline |
| `build` | Spec copy and task plan | `.superpowers/plans/` in the working copy, ignored by git, never committed |
| `build` | Branch, code and tests | GitHub, committed |
| `build` | Pull request | GitHub |
| `build` | Report: Built, Checks, Needs attention, Decisions, Follow-ups | A Linear comment, plus a visual report page |
| `build` | Follow-up issues for problems outside the scope | Linear, Backlog |
| `build` | Handoff comment, only if it has to stop | Linear |
| `feature` | "Feature plan" comment and a visual plan | Linear, on the parent |
| `feature` | "Feature run" comment, updated per step | Linear, on the parent |
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
- Only code is committed.
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
| `build` works by hand, execution skills optional | Requiring a copy of Superpowers in every repository | The by-hand path proved enough on the first real run; the copies are a bonus |
| Eight Superpowers execution skills, as copies, when wanted | The whole Superpowers plugin | Its design and finishing steps overlap with `ideate`, `spec` and `ship`, and it stops four times to ask a person |
| The owner brings third-party skills into a repository | The agent doing it, or editing the repository's instructions file | An agent's attempt was blocked as instruction poisoning in a test, and it should be |
| A fast lane in `ideate` | Every idea going through options and a spec turn | Taken from Warp Factories' triage step (implement, spec or wait) |
| Visual proof in `build` stays a soft rule | Making it mandatory | Production is a single person for now |
| No scoring of runs | Two facts recorded on each close-out | It would make the flow more complex |
| An orchestrator that is itself a skill | A platform orchestrator (Warp, Projects, agent teams) | The issue already carries everything, so a skill with a worker per step is enough, and it runs wherever the skills run |
| A plan approved before any worker starts | Running to the end by default | How far an unattended run goes is the person's call |
| Owner checks counted apart | Reporting them as not passing | "3 of 6 passed, 3 owner" says what it means; "3 of 6" does not |

## Parked

Thought through and not built:

- **A skill that reads the factory notes.** `ship` writes one line per friction on every close-out, and nothing reads them. A sixth skill could read those notes and the owner's corrections across recent issues and propose skill edits. A necessity for any factory in the long run, and a token cost, so a nice-to-have for now.
- **A weekly version check.** A scheduled task that runs `tools/superpowers-skills.py check` and files an issue when a new Superpowers release touches one of the eight skills.
- **A team layer for three to five developers.** Ticket ownership and a limit on work in progress, one teammate's review after the agent's, autonomy levels per repository, a release step.
- **Parallel steps in `feature`.** v0.1 runs steps one at a time. Independent sub-issues could run at once, on separate files.

Considered and declined: mandatory visual proof in `build`; scoring each run; benchmarks re-run when a skill changes; a foreman agent that routes work (the person is the router).

## Tested, and not

Tested on real tickets: `ideate`, `spec` and `build` end to end on a native desktop app and on a multiplatform app, including a run on the person's machine with a tool install and an owner-only permission check; `feature` on a multi-issue feature. Tested in dry runs with fresh agents: the three lanes, the Foundation card, the feature plan against a fixture of four sub-issues, `build` with and without the execution skills.

Not tested yet: `ship` against hosting that deploys on merge; a fast-lane spec going through `build`; the Codex manifest; `feature` continuing from a "Feature run" comment in a later session.

## Known gaps

Found on real runs and not fixed yet. Each has a workaround.

- **Stacked pull requests do not merge themselves.** `feature` opens each step's pull request against the previous step's branch, and `ship` merges a pull request into whatever base it has; neither retargets the next one. Merging the chain through `ship` as it stands lands step 2 in step 1's branch, not in the integration branch, and Linear marks the issue Done anyway, since its GitHub sync counts a merge into any branch. Until a skill owns the retarget: after each merge, retarget the next pull request at the integration branch before shipping it, or turn on "Automatically delete head branches" in the repository so GitHub retargets dependent pull requests on its own. A merged pull request is not proof that a step reached the integration branch; `git merge-base --is-ancestor <commit> <branch>` is.
- **Workers without a subagent tool self-review.** When a worker runs somewhere it cannot start a fresh reviewer, `build`'s whole-branch review is a self-review and its report says so. `feature`'s own reviewer covers the gap; a single `build` run does not have that cover, so read the report harder.
- **The later-step-impact rule can stop on a name.** A field called one thing in a spec and another in the code is a clarification the next worker resolves by reading the code, not a change to the plan. The orchestrator should record it as a decision and continue; v0.1 may stop instead.

Open: whether an orchestrator may run an owner's production step when asked (a migration, a deploy), and under what conditions. The rule today is that agents never touch production data, and it stays absolute until decided otherwise.
