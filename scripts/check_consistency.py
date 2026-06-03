#!/usr/bin/env python3
"""Structural consistency checks for the Capsa agent cookbook.

Deterministic, stdlib-only. Asserts the docs, skills, reference layer, and
machine-readable index stay in sync as the cookbook grows. CI runs this on every
pull request; run it locally before opening one:

    python3 scripts/check_consistency.py

It does NOT contact the live connector — the connector's own
`capsa_describe_capability` is the source of truth for what exists. This script
only checks that the cookbook is internally consistent.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HTML_BASE = "https://github.com/capsa-analytics/capsa-agent-cookbook/blob/main/"
RAW_BASE = "https://raw.githubusercontent.com/capsa-analytics/capsa-agent-cookbook/main/"

TOOL_RE = re.compile(r"capsa_[a-z_]+")
# Bare artifact left when `capsa_list_*_filter_options` is split on the wildcard.
TOOL_WILDCARD = "capsa_list_"

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def docs(*patterns: str) -> list[str]:
    out: set[str] = set()
    for pat in patterns:
        for p in glob.glob(os.path.join(ROOT, pat), recursive=True):
            if f"{os.sep}.git{os.sep}" not in p:
                out.add(p)
    return sorted(out)


# --- load index.json (fatal if unparseable) --------------------------------
try:
    index = json.loads(read("index.json"))
except Exception as exc:  # noqa: BLE001
    print(f"FATAL: cannot parse index.json: {exc}")
    sys.exit(1)


# 1. All JSON parses.
for jf in ("index.json", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
    try:
        json.loads(read(jf))
    except Exception as exc:  # noqa: BLE001
        err(f"invalid JSON: {jf}: {exc}")


# 2. Every capsa_* tool referenced anywhere is listed in README (the CI rule the
#    public-safety review states in prose, enforced here).
readme_tools = {t for t in TOOL_RE.findall(read("README.md")) if t != TOOL_WILDCARD}
for f in docs("**/*.md", "*.txt", "**/*.json"):
    if rel(f) == "README.md":
        continue
    for tool in TOOL_RE.findall(open(f, encoding="utf-8").read()):
        if tool == TOOL_WILDCARD:
            continue
        if tool not in readme_tools:
            err(f"{rel(f)}: references tool not listed in README.md: {tool}")


# 3. index.json paths exist on disk.
index_paths = [index["start_here"]["path"]]
for key in ("skills", "capabilities", "patterns"):
    index_paths += [e["path"] for e in index.get(key, [])]
for p in index_paths:
    if not os.path.exists(os.path.join(ROOT, p)):
        err(f"index.json lists a path that does not exist: {p}")


# 4. Bidirectional sync: every skill / capability / pattern file on disk has an
#    index.json entry, and vice-versa.
def sync(disk_glob: str, index_key: str, label: str) -> None:
    on_disk = {rel(p) for p in docs(disk_glob)}
    in_index = {e["path"] for e in index.get(index_key, [])}
    for missing in sorted(on_disk - in_index):
        err(f"{label} on disk but missing from index.json: {missing}")
    for extra in sorted(in_index - on_disk):
        err(f"index.json lists a {label} not on disk: {extra}")


sync("skills/*/SKILL.md", "skills", "skill")
sync("reference/capabilities/*.md", "capabilities", "capability page")
sync("reference/patterns/*.md", "patterns", "pattern page")


# 5. Every SKILL.md carries a non-empty `description` in its frontmatter.
for s in docs("skills/*/SKILL.md"):
    text = open(s, encoding="utf-8").read()
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        err(f"{rel(s)}: missing YAML frontmatter")
    elif not re.search(r"^description:\s*\S", fm.group(1), re.M):
        err(f"{rel(s)}: frontmatter missing a non-empty 'description'")


# 6. Relative markdown links resolve to real files.
link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
for md in docs("**/*.md"):
    base = os.path.dirname(md)
    for m in link_re.finditer(open(md, encoding="utf-8").read()):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path = target.split("#", 1)[0]
        if path and not os.path.exists(os.path.normpath(os.path.join(base, path))):
            err(f"{rel(md)}: broken relative link -> {target}")


# 7. GitHub blob/raw URLs in the index + landing pages map to real files.
url_re = re.compile(r'https://[^\s)"]+')
for f in ("llms.txt", "README.md", "index.json"):
    for url in url_re.findall(read(f)):
        for base in (HTML_BASE, RAW_BASE):
            if url.startswith(base):
                target = url[len(base):].rstrip("/")
                if target and not os.path.exists(os.path.join(ROOT, target)):
                    err(f"{f}: URL points at a missing file: {target}")


# 8. llms.txt links each skill / capability / pattern the index lists.
llms = read("llms.txt")
for key in ("skills", "capabilities", "patterns"):
    for e in index.get(key, []):
        if e["path"] not in llms:
            err(f"llms.txt is missing a link to {key[:-1]}: {e['path']}")


# --- report ----------------------------------------------------------------
if errors:
    print(f"FAIL: {len(errors)} consistency problem(s):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(
    "OK: cookbook structure is consistent "
    f"({len(index.get('skills', []))} skills, "
    f"{len(index.get('capabilities', []))} capabilities, "
    f"{len(index.get('patterns', []))} patterns; "
    f"{len(readme_tools)} public tools)."
)
