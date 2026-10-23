# Publishing a plugin in the directory

How Idea Ship went into Anthropic's plugin directory, written as the checklist the next plugin from this repository's owner (the Itakua plugin) follows. It is the first run of the process, October 2026. Each step says what to do, then what happened. A line marked "Pending, fill in after step 8" needs the live listing and is filled in once it exists.

## How the directory works

What the steps below are built on, read from the pre-submission checklist, the submit flow and the publish docs:

- Submission is per plugin folder, from a GitHub repository, in the developer portal at claude.ai/directory/manage (**Submit new**, then **Plugin bundle**). A paid plan is required; a Max plan submits from the owner's own account.
- The portal's **Validate** runs the directory checks on one commit. After submitting, every new commit on the tracked branch or tag is scanned again: validation plus a security scan. A first submission that fails the security scan is rejected.
- The README in the plugin folder is the listing's description.
- The icon is fixed the first time the plugin is saved or submitted in the portal. Changing the file later does not change the listing.
- The name is permanent. A generic word is held for a reviewer ("Name may be confused with an existing listing").
- A passing version is not live until **Publish** is selected and a reviewer publishes it (the default setting). Later versions can auto-publish once a reviewer allows it.
- Limits: 10 submissions per organization per 24 hours, saved drafts and withdrawn submissions included; one submission per repository and folder, reopened from **Submissions** rather than created again.
- Inside the plugin folder, a bundled image appears only as Markdown image syntax. Writing its path in backticks or a code block, or referring to it from a command, hook or script, holds the version for a reviewer.

Local check, from the repository root: `claude plugin validate plugins/<name> --strict`.

## Timeline

| Date | What happened |
|---|---|
| 22 Oct 2026 | Portal Validate on the old name; rename decided. Plan approved; rename, listing README, folder checks and local surface runs built. Icon direction picked |
| 23 Oct 2026 | Icon palette picked, icon committed, release 0.5.0 prepared, portal visited read-only, docs updated |
| Pending, fill in after step 8 | Submitted, review started |
| Pending, fill in after step 8 | Review finished, published, listing live |

## 1. Settle the name

**Do.** Run the portal's Validate on the folder before anything else. It is the only check that tells you whether the name will be held. Pick the name before the icon, the README and the first portal save, because none of them can change it later.

**Happened.** Validate on 22 Oct 2026, on the folder then called `factory` at `main@7b33d0c`: 7 checks, 1 warning (no icon) and 1 policy hold, because `factory` matched the display name "Factory" of a plugin already listed. A search also found an existing Claude Code plugin with a near name in the same category, and a coding-agent company with the same word. The plugin was renamed `idea-ship`, display name "Idea Ship": it names the loop (ideate to ship), had no collision in developer tooling, and gave the mark its subject. The marketplace kept its name, `sdlc-fede`.

The rename moved the folder, set `name` and `displayName` in the three plugin manifests, and added a `renames` map from `factory` to `idea-ship` in all three marketplace files, without which existing installs fail with "not found in marketplace" on their next update. Slash triggers changed to `/idea-ship:<skill>`; plain-word triggers did not. Five of six checks passed. The migration of an existing install is an owner check that runs only after the rename reaches `main`, which the marketplace serves: Pending, fill in after step 8.

**For Itakua.** Decide the name and run Validate on it first; avoid a generic word.

## 2. Draw the mark and the icon

**Do.** Draw the mark as an SVG source and render the listing icon from it. The directory takes PNG or JPEG only, square, 512 to 2048 px, under 2 MB; SVG and WebP are refused. Claude Code finds `.claude-plugin/icon.png` by its place, so the manifest needs no `icon` key. Show the owner renders at listing size and at 48 px before committing, since the first portal save fixes it.

**Happened.** Two directions were refined from mockups and rendered side by side at 1024, 96, 48 and 32 px on light and dark tiles, and at 48 px among placeholder plugin icons: a sailboat and a paper boat. The owner picked the sailboat on 22 Oct 2026, then asked for a better palette than the flow page's colours. Four palettes were rendered, and the owner picked "Harbour Coral, tuned" on 23 Oct 2026: light tile #1d5276, sails #fcf7ec and #d6c6a4, hull #d9502f, hull top #f6a184; dark tile #163a57, hull #de5a39, hull top #f7a78b. The paper boat is kept beside it as the alternative direction.

The spec rules that mattered:

- One bold silhouette that reads at 48 px and at 512 px. No outlines, thin lines, gradients, text or water; the tile is the water.
- Two colour families plus the tile.
- Every horizontal edge on the 48 px grid, so no row blurs at the small size; the mast gap is exactly 1 px at 48.
- Each part is its own path with a fixed id (sheet, sails, hull, hull top, crease), so a later folding animation can use the same geometry.

The icon is 1024 by 1024, 53,189 bytes, rendered by `scripts/render-icon.py` with resvg-py 0.2.0, and a second run gives an identical file. Claude Code 2.1.303's strict validation never reported a missing icon, with or without the file, so `scripts/validate.py` checks the icon itself: a square PNG of 512 to 2048 px under 2 MB. The owner's look at the 48 px render is the last check.

**For Itakua.** Its own mark and icon decision comes first, with the name. Reuse the render script and the validator check.

## 3. Write the folder README as the listing

**Do.** Rewrite the plugin folder's README for someone who has never seen the repository: what it is, what it needs, what it runs and sends, where it works, and links. Every link absolute. Images only as Markdown image syntax pointing at absolute URLs.

**Happened.** The README became the listing on 22 Oct 2026: a one-line pitch, the loop table, what you need, "What it runs and sends", "Where it works" and absolute links, with the git-marketplace install moved to the end. Reading all six skills in full turned up more than the spec's disclosure list, and all of it went in: `build` and `ship` watch previews and deploys and load the live URL, read-only; briefs and reports go out through the session's visual or page tool; `build` may use the session's browser; `ideate` may read notes through a knowledge base connector; `setup` may create a Linear project on a yes; `build` writes notes to the self-ignoring `.factory/plans/`; `feature` may create a git worktree; a secret pasted in chat is moved into a file. "Stores nothing" became "nothing outside that ignored scratch folder". All five checks passed.

**For Itakua.** Write the disclosure from the skill text, not from memory; it is what the security scan and the reviewer compare against.

## 4. Make the folder pass every directory check

**Do.** Make the plugin folder self-contained and make the repository's validator enforce the directory's folder rules, so a later commit cannot break the listing.

**Happened.** A copy of `LICENSE` went into the folder, and `scripts/validate.py` now fails on system files, unsafe or case-colliding names, symbolic links, anything but text, complete images and fonts, files over 256 KiB (raster images exempt), more than 512 files, and package manifests, lockfiles or package runners. All six checks passed; strict validation passed with the Codex and Cursor manifests in the folder. A file with an unknown suffix fails even when it is text, so a new text type needs its suffix added.

**For Itakua.** The validator already covers every folder under `plugins/`.

## 5. Record what each skill does on each surface

**Do.** A directory install reaches claude.ai chat, Cowork and Claude Code local and cloud, so run every skill on each and write the result in the README's "Where it works" table. A skill that cannot run somewhere must stop cleanly in one line.

**Happened.** All six skills ran end to end in Claude Code local on 22 Oct 2026, one fresh headless session each, on a private fixture repository and a fixture Linear project: all yes, `feature` up to its plan approval. A Claude Code session with no shell, no checkout and no subagents stood in for chat, and found two problems: `build` moved the issue to In Progress and posted a Handoff it could not act on, and `ship` read the pull request through Linear's link to the code host, which also offers a merge. Both skills gained a one-line preflight, and after it each stopped in one line with no tool call. `setup` and `feature` already stopped cleanly.

Every session loaded two copies of the skills: the branch's `idea-ship` and an older `factory` plugin synced from the owner's account. Without a checkout the older copy answered every plain phrase, so the stops were re-run as `/idea-ship:<skill>` to test the new text. Three of five checks passed. The cloud column stays open work for the owner, because `claude --cloud` needs an interactive terminal; the chat and Cowork cells are the owner's, with a test script on the issue. Cloud, chat and Cowork results: Pending, fill in after step 8.

**For Itakua.** Remove older copies before testing, or invoke every skill by its namespaced name; otherwise you may be testing the wrong text.

## 6. Release and decide what the directory tracks

**Do.** Bump the version in every manifest, date the changelog entry, and decide what the directory tracks before submitting.

**Happened.** Version 0.5.0 in the three plugin manifests, changelog dated 23 Oct 2026 with one line per change; both validators passed on the release commit. The directory tracks `main` and auto-publish stays off, so every merge to `main` shows up as a scanned version and goes live only on a Publish click. The tag `idea-ship--v0.5.0` is pushed once the release commit is on `main`. If auto-publish is turned on later, switch the directory to a tag first.

## 7. Submit in the developer portal

**Do.** Before opening the portal: read the directory policy and terms once (a reviewer checks policy, the automated checks do not); connect GitHub on claude.ai in the same organization as the paid plan, with an account that can push to the repository; have the contact email ready, since review decisions arrive there. Then:

1. **Submit new**, **Plugin bundle**.
2. **Source**: the repository, the plugin path, and the branch or tag (empty for `main`). **Validate**. Fix anything **Blocking**, push, **Re-validate**: the report is per commit. Note any **Policy hold**; it does not block submitting.
3. **Listing details** are read-only, built from `plugin.json` and the README. If something reads wrong, fix it in the repository and validate again.
4. **Data handling**, answered plainly.
5. **Compliance**: confirm the contact email and the four acknowledgements.
6. **Review and submit**: keep the GitHub push webhook, leave **Auto-publish passing versions** off for the first version, **Submit for review**.

**Observed before submitting, 23 Oct 2026, read-only.** The portal showed 0 submissions. Opening it forces a fresh claude.ai sign-in: it redirects through a logout with a re-authentication flag. The GitHub integration was connected as the repository owner with the Claude GitHub App installed. On claude.ai, the skills reached cloud sessions through the old `factory` plugin installed on the account from the `sdlc-fede` marketplace the owner had added (Customize, Plugins, Yours, "From marketplaces you added"); its six skills appear under Skills with the same label. A second organization on the same account still synced `factory` 0.3.1.

**Data handling answers planned.** Reads or stores personal data: no; the plugin stores nothing and writes only to the user's own Linear and GitHub. Sends data to services other than the declared connectors: no. Retention: none. Directed at people under 18: no.

- Validate report on the submitted commit, and any policy hold on `idea-ship` with its reason: Pending, fill in after step 8.
- Date submitted, and the first scanned version in the Versions tab: Pending, fill in after step 8.
- Push webhook set up, and a test push shown as a scanned version: Pending, fill in after step 8.

## 8. Follow the review, publish, verify

**Do.** Each scanned commit shows in the Versions tab as passing, held for a reviewer, or not passing. Passing: select **Publish**. Held: wait; a hold is not a rejection, and requested changes appear on the Review tab. Not passing: fix, push, and **Check for new commits**, or **Resubmit for review** if the submission was rejected. Once live, check the listing's icon, name, description and README; add it from the directory on an account with no older copies; confirm `idea-ship@synced` in a local and a cloud Claude Code session and `ideate` in a claude.ai chat; note where the usage tab is.

**Happened.**

- How long review took: Pending, fill in after step 8.
- Security scan result and the findings that appeared: Pending, fill in after step 8.
- What the reviewer asked, and what changed in answer: Pending, fill in after step 8.
- The listing as published (icon, name, description, README rendering): Pending, fill in after step 8.
- `idea-ship@synced` in a local session, a cloud session running `setup`, and `ideate` in chat: Pending, fill in after step 8.
- The publish setting for later versions, and where the usage tab is: Pending, fill in after step 8.

## 9. Afterwards

**Do.** Remove the older copies on every organization the account belongs to, update the repository's docs to point at the directory, and file the next plugin's parent issue from this file.

**Happened.** The root README, `CONTRIBUTING.md`, `docs/setup.md`, `docs/design.md` and the plugin README now send Claude surfaces to the directory and keep the git marketplace for Codex, Cursor and following `main`; the mirror rule is kept only for a repository that commits the skills into its `.claude/skills/`. Removing the old `factory` installs on the account, in both organizations: Pending, fill in after step 8. The Itakua parent issue: Pending, fill in after step 8.

## The order for the next plugin

1. Name: run Validate on the candidate in the portal; avoid a generic word. Permanent.
2. Icon: SVG source, PNG render, the owner's pick at 48 px. Fixed at the first portal save.
3. Folder README as the listing, with the disclosure written from the skill text.
4. Folder checks in the validator, so the listing cannot regress.
5. Every skill on every surface, older copies removed first; a one-line stop where a skill cannot run.
6. Release, and decide what the directory tracks and whether it auto-publishes.
7. Submit in the portal; record the data handling answers and every policy hold.
8. Follow the review, publish, verify the listing on each surface, and fill in the lines above.
9. Remove the older copies, update the docs, and start the next plugin from this file.
