# factory

Five skills that carry a Linear ticket from a spoken idea to a merged pull request. Install the plugin, connect Linear and GitHub in the session, and speak four times per ticket.

```sh
claude plugin install factory --marketplace el-sapo/sdlc-fede --scope user
```

One step on Claude Code 2.1.275 or later; older versions add the marketplace first (see the [repository README](../../README.md#install)).

| Skill | You say | It leaves on the issue | Status after |
|---|---|---|---|
| `ideate` | an idea, even half-formed or by voice | options with a visual brief, or a ready spec on the fast lane | Backlog, or Todo |
| `spec` | "1 B, 2 ok, option A. Spec it" | a lean, buildable spec; sub-issues when it is larger than one pull request | Todo |
| `build` | "code ABC-12" | a pull request and a report with evidence per check | In Review |
| `ship` | "ship ABC-12" | a merge, a live check, a close-out with factory notes | Done |
| `feature` | "build the feature ABC-47" | a plan you approve, then a feature branch with each verified step merged in, a run comment, and one final pull request with its report | In Review |

Every skill ends with a message short enough for a phone notification that says what to do next. The skills answer to plain words; `/factory:ideate` and friends work too.

## Three things to know

- **Everything is on the issue.** A later session continues from the issue and the branch alone. If Linear is not connected, each skill gives you the text to paste and says that nothing was saved.
- **Agents verify, you approve.** `build` opens the pull request and never merges. `ship` merges only on your word and refuses an approval that carries a code change. `feature` builds nothing before you approve its plan, merges verified steps only into its own feature branch, and leaves the final merge to you.
- **Checks only you can run are marked.** A permission, a device, a real account: the spec marks those checks `Owner:` and the build counts them apart from the ones it verified.

## Examples in the skills

The skills use `ABC-12` and `ABC-47` as example identifiers and `main` as the default branch. Your team key and branch names come from Linear and the repository at run time.

See the [repository README](../../README.md) for installation, requirements and where the skills load, and [docs/design.md](../../docs/design.md) for the design.
