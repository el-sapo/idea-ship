# tools

## superpowers-skills.py

Copies eight execution skills from [Superpowers](https://github.com/obra/superpowers) (MIT) into a repository's `.claude/skills/` at a pinned release, and tracks the version. `build` uses them when they are present and works without them; this is optional.

The eight: `writing-plans`, `subagent-driven-development`, `executing-plans`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`. The design, worktree and finishing skills are left out on purpose because `ideate`, `spec` and `ship` cover those steps, and `build` answers in advance the questions the copies would ask a person.

Copies rather than the plugin, because the plugin's own workflow runs from brainstorming to a finishing menu, stops for a person in several places, and loads a start-of-session rule that tells the agent to use any skill that might apply; all of that clashes with the loop. Skills in a repository also load in every kind of session, cloud included.

Run it yourself, from the repository root. Agents do not copy third-party skills into a repository.

```sh
cp path/to/sdlc-fede/tools/superpowers-skills.py tools/
python3 tools/superpowers-skills.py init      # copy the eight skills at the pinned release
python3 tools/superpowers-skills.py check     # copies intact? newer release upstream?
python3 tools/superpowers-skills.py diff      # what changed upstream in these eight
python3 tools/superpowers-skills.py update    # adopt a reviewed release; refuses if a copy was edited
```

Needs Python 3.9+ and git. The record is `.claude/superpowers/provenance.json` (source, version, commit, dates, a hash per skill) with the MIT license beside it. Exit codes for `check`: 0 intact and current, 1 newer release available, 2 a local copy differs from the record, 3 both.

The pin is `v7.0.0`. To adopt a newer release, run `diff` (add `--notes` for the release notes), read the changes in the eight skills, then `update` (or `update --to vX.Y.Z` for a specific release), run a build on a small ticket, and commit.

The `executing-plans` scripts call into `subagent-driven-development/scripts`, so the eight folders stay side by side.
