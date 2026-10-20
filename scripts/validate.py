#!/usr/bin/env python3
"""Check this marketplace repository before a commit.

Verifies the marketplace and plugin manifests, every skill's front matter,
the links between them, and a few house rules for the written text. Prints one
line per problem and exits 1 when there is any. Needs only Python 3.9+.

  python3 scripts/validate.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CURSOR_MARKETPLACE = ROOT / ".cursor-plugin" / "marketplace.json"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
EM_DASH = "—"
PROSE_GLOBS = ["*.md", "docs/*.md", "plugins/*/README.md", "plugins/*/skills/*/SKILL.md"]

problems = []


def problem(path, message):
    problems.append(f"{path.relative_to(ROOT) if isinstance(path, Path) else path}: {message}")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problem(path, "missing")
    except json.JSONDecodeError as error:
        problem(path, f"invalid JSON: {error}")
    return None


def front_matter(text):
    """Return the YAML front matter as a dict of top-level scalar keys, or None."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip("\"'")
    return fields


def check_marketplace():
    data = load_json(MARKETPLACE)
    if data is None:
        return []
    for key in ("name", "owner", "plugins"):
        if key not in data:
            problem(MARKETPLACE, f"missing '{key}'")
    if "name" in data and not KEBAB.match(data["name"]):
        problem(MARKETPLACE, f"name '{data['name']}' is not kebab-case")
    if isinstance(data.get("owner"), dict) and "name" not in data["owner"]:
        problem(MARKETPLACE, "owner has no name")
    plugins = data.get("plugins") or []
    if not plugins:
        problem(MARKETPLACE, "no plugins listed")
    sources = []
    for entry in plugins:
        name = entry.get("name", "?")
        if not KEBAB.match(name):
            problem(MARKETPLACE, f"plugin name '{name}' is not kebab-case")
        source = entry.get("source")
        if not isinstance(source, str) or not source.startswith("./"):
            problem(MARKETPLACE, f"plugin '{name}' needs a relative source such as ./plugins/{name}")
            continue
        folder = (ROOT / source).resolve()
        if not folder.is_dir():
            problem(MARKETPLACE, f"plugin '{name}' points at a missing folder {source}")
            continue
        sources.append((name, folder))
    return sources


def check_codex_marketplace(expected):
    data = load_json(CODEX_MARKETPLACE)
    if data is None:
        return
    listed = {}
    for entry in data.get("plugins") or []:
        source = entry.get("source") or {}
        listed[entry.get("name")] = source.get("path") if isinstance(source, dict) else source
    for name, folder in expected:
        path = listed.get(name)
        if path is None:
            problem(CODEX_MARKETPLACE, f"plugin '{name}' is not listed")
        elif (ROOT / path).resolve() != folder:
            problem(CODEX_MARKETPLACE, f"plugin '{name}' points at {path}, Claude manifest points at {folder.relative_to(ROOT)}")


def check_cursor_marketplace(expected):
    data = load_json(CURSOR_MARKETPLACE)
    if data is None:
        return
    for key in ("name", "owner", "plugins"):
        if key not in data:
            problem(CURSOR_MARKETPLACE, f"missing '{key}'")
    listed = {}
    for entry in data.get("plugins") or []:
        source = entry.get("source")
        listed[entry.get("name")] = source.get("path") if isinstance(source, dict) else source
    for name, folder in expected:
        path = listed.get(name)
        if path is None:
            problem(CURSOR_MARKETPLACE, f"plugin '{name}' is not listed")
        elif (ROOT / path).resolve() != folder:
            problem(CURSOR_MARKETPLACE, f"plugin '{name}' points at {path}, Claude manifest points at {folder.relative_to(ROOT)}")


def check_plugin(name, folder):
    manifest = folder / ".claude-plugin" / "plugin.json"
    data = load_json(manifest)
    if data is not None:
        if data.get("name") != name:
            problem(manifest, f"name '{data.get('name')}' differs from the marketplace entry '{name}'")
        version = data.get("version")
        if version and not SEMVER.match(version):
            problem(manifest, f"version '{version}' is not major.minor.patch")
        if not data.get("description"):
            problem(manifest, "no description")

    codex = folder / ".codex-plugin" / "plugin.json"
    codex_data = load_json(codex)
    if codex_data is not None and data is not None:
        if codex_data.get("name") != name:
            problem(codex, f"name '{codex_data.get('name')}' differs from '{name}'")
        if codex_data.get("version") != data.get("version"):
            problem(codex, f"version {codex_data.get('version')} differs from Claude manifest {data.get('version')}")

    cursor = folder / ".cursor-plugin" / "plugin.json"
    cursor_data = load_json(cursor)
    if cursor_data is not None and data is not None:
        if cursor_data.get("name") != name:
            problem(cursor, f"name '{cursor_data.get('name')}' differs from '{name}'")
        if cursor_data.get("version") != data.get("version"):
            problem(cursor, f"version {cursor_data.get('version')} differs from Claude manifest {data.get('version')}")

    skills = folder / "skills"
    if not skills.is_dir():
        problem(folder, "no skills/ folder")
        return
    found = sorted(p for p in skills.iterdir() if p.is_dir())
    if not found:
        problem(skills, "empty")
    for skill_dir in found:
        check_skill(skill_dir)


def check_skill(skill_dir):
    skill = skill_dir / "SKILL.md"
    if not skill.is_file():
        problem(skill_dir, "no SKILL.md")
        return
    text = skill.read_text(encoding="utf-8")
    fields = front_matter(text)
    if fields is None:
        problem(skill, "no front matter")
        return
    if fields.get("name") != skill_dir.name:
        problem(skill, f"front matter name '{fields.get('name')}' differs from folder '{skill_dir.name}'")
    description = fields.get("description", "")
    if len(description) < 20:
        problem(skill, "description is missing or too short")
    if len(description) > 1024:
        problem(skill, f"description is {len(description)} characters, keep it under 1024")
    body = text[text.find("\n---", 4) + 4:]
    if not body.strip():
        problem(skill, "empty body")
    lines = body.count("\n")
    if lines > 500:
        problem(skill, f"body is {lines} lines; the budget is 500")


def check_prose():
    seen = set()
    for pattern in PROSE_GLOBS:
        for path in ROOT.glob(pattern):
            if path in seen or ".git" in path.parts:
                continue
            seen.add(path)
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                if EM_DASH in line:
                    problem(path, f"line {number}: em dash")
                if "\t" in line and path.suffix == ".md":
                    problem(path, f"line {number}: tab character")
            if text and not text.endswith("\n"):
                problem(path, "no newline at end of file")


def check_root_files():
    for name in ("README.md", "LICENSE", "CHANGELOG.md"):
        if not (ROOT / name).is_file():
            problem(ROOT / name, "missing")


def main():
    sources = check_marketplace()
    check_codex_marketplace(sources)
    check_cursor_marketplace(sources)
    for name, folder in sources:
        check_plugin(name, folder)
    check_prose()
    check_root_files()
    if problems:
        for line in problems:
            print(line)
        print(f"{len(problems)} problem(s)")
        return 1
    count = sum(1 for _, folder in sources for p in (folder / "skills").iterdir() if p.is_dir())
    print(f"ok: {len(sources)} plugin(s), {count} skill(s), manifests and prose checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
