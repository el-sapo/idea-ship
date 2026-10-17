#!/usr/bin/env python3
"""Copy a chosen set of Superpowers skills into this repo and track their version.

The skills are copied unmodified from https://github.com/obra/superpowers (MIT)
into .claude/skills/, so they load in every kind of agent session without
installing the whole plugin. A record of the pinned version and a content hash
per skill is kept in .claude/superpowers/provenance.json, which is what lets
`check` tell you two things: whether a newer release exists upstream, and
whether a local copy was edited.

Run from the repository root. Needs Python 3.9+ and git. No other dependencies.

  python3 tools/superpowers-skills.py init            copy the skills at the pinned version
  python3 tools/superpowers-skills.py check           local copies intact? newer release upstream?
  python3 tools/superpowers-skills.py diff            what changed upstream in these skills
  python3 tools/superpowers-skills.py update          replace the copies with the reviewed release

Exit codes for `check`: 0 intact and current, 1 newer release available,
2 a local copy differs from the record, 3 both.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

UPSTREAM = "https://github.com/obra/superpowers.git"
DEFAULT_REF = "v7.0.0"  # the newest release reviewed for this workflow

# The execution half of Superpowers. Its design, worktree and finishing skills
# are left out on purpose: the workflow in this repo covers those steps itself.
SKILLS = [
    "writing-plans",
    "subagent-driven-development",
    "executing-plans",
    "test-driven-development",
    "systematic-debugging",
    "verification-before-completion",
    "requesting-code-review",
    "receiving-code-review",
]

DEST = Path(".claude/skills")
RECORD_DIR = Path(".claude/superpowers")
RECORD = RECORD_DIR / "provenance.json"
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(64)


def git(*args, cwd=None, capture=True):
    result = subprocess.run(
        ["git", *args], cwd=cwd, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if result.returncode != 0:
        detail = (result.stderr or "").strip().splitlines()[-1:] or ["no detail"]
        fail(f"git {' '.join(args[:2])} failed: {detail[0]}")
    return (result.stdout or "").strip()


def tree_hash(folder):
    """One hash for a folder: every file's path, executable bit and bytes."""
    digest = hashlib.sha256()
    files = sorted(p for p in Path(folder).rglob("*") if p.is_file())
    for path in files:
        relative = path.relative_to(folder).as_posix()
        executable = "x" if os.access(path, os.X_OK) else "-"
        digest.update(f"{relative}\0{executable}\0".encode())
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), len(files)


def version_key(tag):
    match = TAG_RE.match(tag)
    return tuple(int(part) for part in match.groups()) if match else None


def latest_release():
    lines = git("ls-remote", "--tags", "--refs", UPSTREAM).splitlines()
    tags = [line.split("refs/tags/")[-1] for line in lines if "refs/tags/" in line]
    releases = [tag for tag in tags if version_key(tag)]
    if not releases:
        fail("no release tags found upstream")
    return max(releases, key=version_key)


def fetch(ref, into):
    """Shallow-clone one upstream tag into a folder."""
    git("clone", "--quiet", "--depth", "1", "--branch", ref, UPSTREAM, str(into))
    plugin = Path(into) / ".claude-plugin" / "plugin.json"
    version = json.loads(plugin.read_text()).get("version") if plugin.exists() else None
    return {
        "ref": ref,
        "version": version or ref.lstrip("v"),
        "commit": git("rev-parse", "HEAD", cwd=into),
        "committed": git("log", "-1", "--format=%cs", cwd=into),
    }


def upstream_hashes(clone):
    hashes = {}
    for name in SKILLS:
        folder = Path(clone) / "skills" / name
        hashes[name] = tree_hash(folder)[0] if folder.is_dir() else None
    return hashes


def load_record():
    if not RECORD.exists():
        fail(f"{RECORD} not found. Run `init` first, from the repository root.")
    return json.loads(RECORD.read_text())


def local_state(record):
    """Compare each local copy with the hash in the record."""
    state = {}
    for name, entry in record["skills"].items():
        folder = DEST / name
        if not folder.is_dir():
            state[name] = "missing"
        elif tree_hash(folder)[0] != entry["hash"]:
            state[name] = "modified"
        else:
            state[name] = "intact"
    return state


def copy_skills(clone, info):
    missing = [n for n in SKILLS if not (Path(clone) / "skills" / n).is_dir()]
    if missing:
        fail(f"{info['ref']} has no skill named: {', '.join(missing)}. "
             "Upstream may have renamed or removed it; review before updating.")
    DEST.mkdir(parents=True, exist_ok=True)
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    skills = {}
    for name in SKILLS:
        target = DEST / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(Path(clone) / "skills" / name, target)
        digest, count = tree_hash(target)
        skills[name] = {"files": count, "hash": digest}
    license_file = Path(clone) / "LICENSE"
    if license_file.exists():
        shutil.copyfile(license_file, RECORD_DIR / "LICENSE")
    record = {
        "source": UPSTREAM.removesuffix(".git"),
        "license": "MIT, see LICENSE in this folder",
        "note": "Copied unmodified. Do not edit the copies; change them only "
                "with tools/superpowers-skills.py so the hashes stay true.",
        **info,
        "copied": datetime.date.today().isoformat(),
        "skills": skills,
    }
    RECORD.write_text(json.dumps(record, indent=2) + "\n")
    return record


def cmd_init(args):
    existing = [n for n in SKILLS if (DEST / n).exists()]
    if existing and not args.force:
        fail(f"already present in {DEST}: {', '.join(existing)}. "
             "Use `update` to change version, or `init --force` to overwrite.")
    with tempfile.TemporaryDirectory() as tmp:
        info = fetch(args.ref, Path(tmp) / "upstream")
        record = copy_skills(Path(tmp) / "upstream", info)
    print(f"Copied {len(SKILLS)} skills from Superpowers {record['version']} "
          f"({record['commit'][:7]}, {record['committed']}) into {DEST}/")
    print(f"Record written to {RECORD}. Review with `git status`, then commit.")


def cmd_check(args):
    record = load_record()
    code = 0
    state = local_state(record)
    changed = {n: s for n, s in state.items() if s != "intact"}
    print(f"Pinned: Superpowers {record['version']} ({record['ref']}, "
          f"copied {record['copied']})")
    if changed:
        code |= 2
        print("Local copies that differ from the record:")
        for name, status in changed.items():
            print(f"  {status:9} {name}")
    else:
        print(f"Local copies: all {len(state)} intact")
    if args.offline:
        return code
    latest = latest_release()
    if version_key(latest) <= (version_key(record["ref"]) or (0, 0, 0)):
        print(f"Upstream: {latest} is the newest release. Nothing to review.")
        return code
    code |= 1
    with tempfile.TemporaryDirectory() as tmp:
        info = fetch(latest, Path(tmp) / "upstream")
        theirs = upstream_hashes(Path(tmp) / "upstream")
    print(f"Upstream: {latest} is available (released {info['committed']}).")
    for name in SKILLS:
        ours = record["skills"].get(name, {}).get("hash")
        if theirs[name] is None:
            verdict = "REMOVED upstream"
        elif theirs[name] == ours:
            verdict = "unchanged"
        else:
            verdict = "changed"
        print(f"  {verdict:16} {name}")
    print("Review with:  python3 tools/superpowers-skills.py diff")
    print("Then adopt:   python3 tools/superpowers-skills.py update")
    return code


def cmd_diff(args):
    record = load_record()
    target = args.to or latest_release()
    if target == record["ref"]:
        print(f"{target} is the pinned release. Nothing to compare.")
        return
    names = args.skills or SKILLS
    unknown = [n for n in names if n not in SKILLS]
    if unknown:
        fail(f"not one of the copied skills: {', '.join(unknown)}")
    with tempfile.TemporaryDirectory() as tmp:
        git("init", "--quiet", tmp)
        git("remote", "add", "origin", UPSTREAM, cwd=tmp)
        for ref in (record["ref"], target):
            git("fetch", "--quiet", "--depth", "1", "origin",
                f"refs/tags/{ref}:refs/tags/{ref}", cwd=tmp)
        paths = [f"skills/{n}" for n in names]
        print(f"Superpowers {record['ref']} -> {target}, {len(names)} skill(s)\n")
        print(git("diff", "--stat", record["ref"], target, "--", *paths, cwd=tmp)
              or "No changes in these skills.")
        if args.notes:
            notes = git("diff", "--unified=0", record["ref"], target, "--",
                        "RELEASE-NOTES.md", cwd=tmp)
            added = [l[1:] for l in notes.splitlines()
                     if l.startswith("+") and not l.startswith("+++")]
            print("\nRelease notes added since the pinned release:\n")
            print("\n".join(added) or "(none)")
        if not args.stat:
            print()
            print(git("diff", record["ref"], target, "--", *paths, cwd=tmp))


def cmd_update(args):
    record = load_record()
    changed = {n: s for n, s in local_state(record).items() if s != "intact"}
    if changed and not args.force:
        fail("local copies differ from the record (" + ", ".join(changed) +
             "). Restore them, or pass --force to overwrite.")
    target = args.to or latest_release()
    with tempfile.TemporaryDirectory() as tmp:
        info = fetch(target, Path(tmp) / "upstream")
        new = copy_skills(Path(tmp) / "upstream", info)
    print(f"Updated from Superpowers {record['version']} to {new['version']} "
          f"({new['commit'][:7]}).")
    print("Review with `git diff`, run a build on a small ticket, then commit.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="copy the skills at the pinned release")
    p.add_argument("--ref", default=DEFAULT_REF, help=f"release tag (default {DEFAULT_REF})")
    p.add_argument("--force", action="store_true", help="overwrite existing copies")
    p.set_defaults(run=cmd_init)

    p = sub.add_parser("check", help="verify local copies and look for a newer release")
    p.add_argument("--offline", action="store_true", help="skip the upstream lookup")
    p.set_defaults(run=cmd_check)

    p = sub.add_parser("diff", help="show upstream changes in the copied skills")
    p.add_argument("skills", nargs="*", help="limit to these skills")
    p.add_argument("--to", help="release tag to compare with (default: newest)")
    p.add_argument("--stat", action="store_true", help="summary only")
    p.add_argument("--notes", action="store_true", help="also print new release notes")
    p.set_defaults(run=cmd_diff)

    p = sub.add_parser("update", help="replace the copies with a newer release")
    p.add_argument("--to", help="release tag to adopt (default: newest)")
    p.add_argument("--force", action="store_true", help="overwrite locally edited copies")
    p.set_defaults(run=cmd_update)

    args = parser.parse_args()
    if not Path(".git").exists():
        fail("run this from the root of a git repository")
    sys.exit(args.run(args) or 0)


if __name__ == "__main__":
    main()
