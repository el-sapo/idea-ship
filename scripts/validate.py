#!/usr/bin/env python3
"""Check this marketplace repository before a commit.

Verifies the marketplace and plugin manifests, every skill's front matter,
the links between them, the listing icon, the folder rules a plugin
directory enforces on each plugin folder, and a few house rules for the
written text. Prints one
line per problem and exits 1 when there is any. Needs only Python 3.9+.

  python3 scripts/validate.py
"""

import json
import os
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
# Front matter: one 'key: value' per line, and the characters YAML reserves
# at the start of an unquoted value.
FRONT_MATTER_LINE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?: (.*))?$")
PLAIN_BLOCK = set("|>")
PLAIN_START = set("-?:,[]{}#&*!%@`")
PROSE_GLOBS = ["*.md", "docs/*.md", "plugins/*/README.md", "plugins/*/skills/*/SKILL.md"]
PLUGINS = ROOT / "plugins"

# Folder rules a plugin directory enforces on a submitted plugin folder.
SYSTEM_FILES = {".ds_store", "thumbs.db", "desktop.ini"}
DEVICE_NAMES = {"con", "prn", "aux", "nul"} | {f"com{n}" for n in range(1, 10)} | {f"lpt{n}" for n in range(1, 10)}
PACKAGE_FILES = {
    "package.json", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml",
    "bun.lock", "bun.lockb", "uv.lock", "poetry.lock", "pipfile.lock", "gemfile.lock", "cargo.lock",
    ".npmrc", "bunfig.toml", "uv.toml",
}
RUNNERS = re.compile(r"\b(?:npx|bunx|uvx) |\bpipx run\b|\buv run\b|\bpnpm dlx\b|\byarn dlx\b")
# The file types a directory accepts from any publisher: Markdown, plain text,
# JSON and YAML, and whole raster images. Scripts, programs, fonts and SVG are
# accepted only from publishers the directory has verified, so none ship here.
TEXT_SUFFIXES = {"", ".md", ".markdown", ".txt", ".json", ".yaml", ".yml"}
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_FILE_BYTES = 256 * 1024
MAX_FILES = 512
# The directory's listing icon, found by its place: a square PNG.
ICON_MIN, ICON_MAX = 512, 2048
MAX_ICON_BYTES = 2 * 1024 * 1024

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


def scalar(value):
    """Read one front matter value as a strict YAML parser would.

    Returns (text, None), or (None, why a strict parser refuses it). A plugin
    directory and some agents read front matter with a strict parser, so a
    value a lenient reader accepts can still leave the skill unread.
    """
    if value.startswith("'"):
        inner = value[1:-1]
        if len(value) < 2 or not value.endswith("'") or "'" in inner.replace("''", ""):
            return None, "single-quoted value is not closed, or has a lone ' inside (write it as '')"
        return inner.replace("''", "'"), None
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except ValueError:
            return None, "double-quoted value is not closed, or has a bad escape"
        return decoded, None
    if value[:1] in PLAIN_BLOCK:
        return None, "block value; put the value on one line, in quotes"
    if value[:1] in PLAIN_START:
        return None, f"unquoted value starts with {value[0]}; wrap the value in quotes"
    if ": " in value or value.endswith(":"):
        return None, "unquoted value has a colon followed by a space; wrap the value in quotes"
    if " #" in value:
        return None, "unquoted value has a space followed by #, which starts a comment; wrap the value in quotes"
    return value, None


def front_matter(text):
    """Return (fields, errors) for the YAML front matter, or (None, []) when there is none.

    fields holds the top-level keys with a value on their own line. errors
    lists what a strict YAML parser would refuse. Indented lines belong to
    the key above them and are not read.
    """
    if not text.startswith("---\n"):
        return None, []
    end = text.find("\n---", 4)
    if end < 0:
        return None, []
    fields, errors = {}, []
    for number, line in enumerate(text[4:end].splitlines(), 2):
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        match = FRONT_MATTER_LINE.match(line)
        if not match:
            errors.append(f"line {number}: not a 'key: value' line")
            continue
        key, value = match.group(1), (match.group(2) or "").strip()
        if key in fields:
            errors.append(f"line {number}: '{key}' appears twice")
        if not value:
            fields[key] = ""
            continue
        decoded, why = scalar(value)
        if why:
            errors.append(f"line {number}: '{key}': {why}")
        fields[key] = decoded if decoded is not None else ""
    return fields, errors


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

    check_icon(folder / ".claude-plugin" / "icon.png")

    skills = folder / "skills"
    if not skills.is_dir():
        problem(folder, "no skills/ folder")
        return
    found = sorted(p for p in skills.iterdir() if p.is_dir())
    if not found:
        problem(skills, "empty")
    for skill_dir in found:
        check_skill(skill_dir)


def check_icon(icon):
    """When a plugin ships a listing icon, it is a square PNG the directory accepts."""
    if not icon.is_file():
        return
    data = icon.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        problem(icon, "not a PNG")
        return
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width != height or not ICON_MIN <= width <= ICON_MAX:
        problem(icon, f"{width} by {height} px; the icon is square, {ICON_MIN} to {ICON_MAX} px")
    if len(data) >= MAX_ICON_BYTES:
        problem(icon, f"{len(data)} bytes; the icon stays under {MAX_ICON_BYTES // (1024 * 1024)} MB")


def check_skill(skill_dir):
    skill = skill_dir / "SKILL.md"
    if not skill.is_file():
        problem(skill_dir, "no SKILL.md")
        return
    text = skill.read_text(encoding="utf-8")
    fields, errors = front_matter(text)
    if fields is None:
        problem(skill, "no front matter")
        return
    for error in errors:
        problem(skill, f"front matter {error}")
    if errors:
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


def complete_image(suffix, data):
    """True when data is a whole image of the type its suffix names."""
    if suffix == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n") and data.endswith(b"IEND\xaeB`\x82")
    if suffix in (".jpg", ".jpeg"):
        return data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9")
    if suffix == ".gif":
        return data[:6] in (b"GIF87a", b"GIF89a") and data.endswith(b";")
    if suffix == ".webp":
        return (data[:4] == b"RIFF" and data[8:12] == b"WEBP"
                and int.from_bytes(data[4:8], "little") + 8 == len(data))
    return False


def as_text(data):
    """The file's text when it is UTF-8 without NUL bytes, otherwise None."""
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def check_name(path):
    name = path.name
    lower = name.lower()
    if lower in SYSTEM_FILES or lower == "__macosx":
        problem(path, "system file; remove it")
    if ":" in name:
        problem(path, "file name has a colon")
    if name.endswith((".", " ")):
        problem(path, "file name ends with a dot or a space")
    if lower.split(".")[0] in DEVICE_NAMES:
        problem(path, "file name is a Windows device name")
    if lower in PACKAGE_FILES:
        problem(path, "package manifest, lockfile or package manager config; a plugin folder carries none")


def check_file(path):
    data = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix in RASTER_SUFFIXES:
        if not complete_image(suffix, data):
            problem(path, f"not a complete {suffix[1:].upper()} file")
    elif suffix == ".svg":
        problem(path, "SVG; a plugin directory refuses it in a plugin folder. Keep the source outside plugins/ and ship a PNG")
    else:
        text = as_text(data)
        if text is None or suffix not in TEXT_SUFFIXES:
            problem(path, "file type a plugin directory refuses; only Markdown, plain text, JSON, YAML, PNG, JPEG, GIF and WebP are allowed")
        elif text.startswith("#!"):
            problem(path, "starts with #!; a plugin folder carries no scripts")
        elif RUNNERS.search(text):
            problem(path, f"runs a package with '{RUNNERS.search(text).group(0).strip()}'; a plugin folder must not")
    if suffix not in RASTER_SUFFIXES and len(data) > MAX_FILE_BYTES:
        problem(path, f"{len(data) // 1024} KiB; files other than images stay under {MAX_FILE_BYTES // 1024} KiB")


def check_plugin_folder(folder):
    """Apply the directory's folder rules to every entry under one plugin folder."""
    count = 0
    for current, dirs, files in os.walk(folder):
        here = Path(current)
        seen = {}
        for name in sorted(dirs + files):
            seen.setdefault(name.lower(), []).append(name)
        for names in seen.values():
            if len(names) > 1:
                problem(here / names[0], f"names differ only by case: {', '.join(names)}")
        for name in list(dirs):
            path = here / name
            check_name(path)
            if path.is_symlink():
                problem(path, "symbolic link; copy the content instead")
                dirs.remove(name)
        for name in files:
            path = here / name
            count += 1
            check_name(path)
            if path.is_symlink():
                problem(path, "symbolic link; copy the content instead")
            elif path.is_file():
                check_file(path)
            else:
                problem(path, "not a regular file")
    if count > MAX_FILES:
        problem(folder, f"{count} files; a plugin folder holds at most {MAX_FILES}")


def check_plugins_tree():
    """Every folder under plugins/ follows the folder rules, listed in a marketplace or not."""
    if not PLUGINS.is_dir():
        return
    for entry in sorted(PLUGINS.iterdir()):
        check_name(entry)
        if entry.is_symlink():
            problem(entry, "symbolic link; copy the content instead")
        elif entry.is_dir():
            check_plugin_folder(entry)
        else:
            problem(entry, "loose file; everything under plugins/ belongs to a plugin folder")


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
    check_plugins_tree()
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
