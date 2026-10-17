---
name: ship
description: Use when the user approves work in review and says "ship it", "ship ABC-12", "merge it" or "go ahead": merge the pull request, confirm the deploy, close the Linear issue and say what comes next.
---

# Ship

The user reviewed the pull request and the report on the Linear issue and said yes. Merge it, make sure what was merged is live and working, close the issue, and tell them what comes next.

Four principles explain the rules below:

- **The approval covers one pull request.** It does not cover other pull requests, and it never covers going around the repo's protections.
- **Merging is the deploy.** If the repo deploys on merge, you watch it happen. You never deploy by hand, run a migration by hand or touch production data, so you need no production credentials.
- **Evidence, not claims.** "Live" means you saw the deploy succeed and looked at the result.
- **The Linear issue is the thread.** What shipped, and what comes next, is written on the issue.

## 1. Find the work

Open the issue, its build report and its pull request. If the issue has more than one open pull request and the user did not say which, ask.

The identifier may be a parent issue whose feature was built by `feature`. Then the pull request is the final one, from the feature branch into the integration branch, its report is the "Feature built" comment, and the sub-issues' pull requests are already merged into the feature branch. Ship it like any other: one approval, one pull request.

The user's message may also answer numbered decisions from the build report. Sort each answer:

- An answer that matches what was built is just an answer. Record it in the close-out comment.
- An answer that needs the code to change ("2: loosen it", "fix the label, then ship") is a change request. The change comes first and belongs to the build step. Tell the user so in your reply, name what has to change, and do not merge.

## 2. Check that it is ready

Merge only when all of these hold:

- The pull request is open, not a draft, and has no conflicts.
- Its base is the branch the user expects: the integration branch, or a feature branch when the user ships a step of a feature under "steps on my word". A pull request whose base is another step's branch that has not merged is not ready: name the step to ship first.
- Every required check is green.
- If the hosting built a preview for the pull request, that build succeeded.
- No change request or review thread from a person is unresolved.
- Every check in the build report passed, or the user's message accepts the ones that did not ("ship it anyway").
- Every decision the build report left as a question has an answer. Decisions where the build took a default need none.

If one does not hold, do not merge. Say which one and what would fix it. Two cases you can handle yourself: when the branch is only behind its base, update it by merging the base in, never by rebasing, and wait for the checks; when a check is still running, wait for it.

## 3. Merge

Merge with the method the repo uses, and squash when the repo allows it and has no convention. Never force a merge, never use admin rights to skip a protection, and never merge into anything but the pull request's base branch. Delete the branch if that is the repo's habit.

Then confirm the commits reached the base: `git merge-base --is-ancestor <head> <base>`. The pull request's merged state is not proof, and neither is Linear moving the issue to Done, since its GitHub sync counts a merge into any branch.

## 4. Watch it go live

If the repo deploys on merge, through a workflow on the default branch or a hosting integration, watch the deploy until it finishes. When it succeeds, check the result without changing anything: load the live URL or health endpoint, and repeat any Done when check that can be observed on the live site.

If the repo has no automatic deploy, say so plainly: merged, not deployed, and what a release would take.

If the base is a feature branch, this merge is integration, not a release. Say "merged into <feature branch>, not deployed", skip the deploy watch and the live check, and name what still waits: the feature's final pull request.

## 5. If it goes wrong

A failed deploy or a failed live check is the one thing to be loud about here. In this order:

1. Find out what users are seeing: is the live site still serving the previous version, or is it broken?
2. Read the deploy log far enough to say what failed. Do not try to fix it, and do not fix forward on the default branch.
3. Open a pull request that reverts the merge, titled "Revert" plus the original title, with the failure and a link to the issue in its body. Do not merge it: reverting is the user's call.
4. Post the close-out comment in its failed form (below) and leave the issue In Review. If the integration already moved it to Done, move it back. Do not announce the next sub-issue as unblocked.
5. Ping right away with what failed, what users see, and the revert pull request.

## 6. Close out on Linear

Post one comment from this template and set the issue to Done if the integration has not already. Drop a section that has nothing in it.

````markdown
## Shipped
Merged: <pull request or commit link> · Live: <link> · Deploy: succeeded

## Checked live
- What you looked at and what you saw.

## Answers
- Any numbered decisions the user answered when approving.

## Next
- The next sub-issue that is now unblocked, or the follow-ups listed in the build report.

## Factory notes
- Anything that made this harder than it should have been, from idea to ship: an unclear spec, a missing command, a flaky test, a question that should have had a default. One line each.
````

When shipping failed, the first section becomes:

````markdown
## Not live
Merged: <link> · Deploy: failed · Users see: <the previous version, or what is broken>
What failed: the error, in a line. Revert ready: <pull request link>
````

For a sub-issue, name the next one that is now unblocked, and close the parent only when every sub-issue is Done. For a parent whose feature branch just merged, set it and any sub-issue still open to Done together. For a step merged into a feature branch, the first line reads "Merged into <feature branch> · Live: not yet", and Next names the final pull request.

Factory notes are how the process improves. Write them whenever something cost time, even if the ticket went fine, and leave the section out when there is nothing to say.

## 7. Ping

End with a message short enough for a phone notification: what shipped, the live link, and what comes next, for example that the next sub-issue is unblocked and they can say "code" with its identifier.

If Linear is not connected, the chat replaces the issue: give the close-out ready to paste and say so in the ping.
