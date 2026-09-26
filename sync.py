#!/usr/bin/env python3
"""Copy selected instruction packs into a project repository.

The project commits the copies. At runtime, agents read those files and do not
clone this repo or follow a live filesystem path back to it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

BEGIN = "<!-- agents-sync:begin -->"
END = "<!-- agents-sync:end -->"
PACK_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*/[a-z0-9][a-z0-9_-]*$")
DEFAULT_SOURCE = "https://github.com/tylerjwoodfin/agents"
SYNCED_ROOT = Path(".agents") / "synced"


class SyncError(Exception):
    """The selection or the agents checkout cannot be synced."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Copy selected agents packs into a project repository."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Project repository to update (default: cwd)",
    )
    parser.add_argument(
        "--agents-repo",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Checkout of the agents repo (default: directory of sync.py)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the files that would change and write nothing",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if committed copies differ from a fresh sync",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Sync even if the agents checkout has uncommitted changes",
    )
    args = parser.parse_args(argv)

    try:
        repo = args.repo.resolve()
        agents_repo = args.agents_repo.resolve()
        files = build_outputs(repo, agents_repo, allow_dirty=args.allow_dirty)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        for rel in files:
            print(f"would write {rel}")
        return 0

    if args.check:
        drifted = drifted_paths(repo, files)
        if drifted:
            print("synced copies are out of date:", file=sys.stderr)
            for rel in drifted:
                print(f"  {rel}", file=sys.stderr)
            return 1
        print(f"up to date ({files_version(files)})")
        return 0

    write_outputs(repo, files)
    version = files_version(files)
    count = pack_count(files)
    label = "pack" if count == 1 else "packs"
    print(f"synced {count} {label} into {repo} ({version})")
    return 0


def build_outputs(repo: Path, agents_repo: Path, *, allow_dirty: bool) -> dict[str, str]:
    packs = load_packs(repo)
    version = git_version(agents_repo, allow_dirty=allow_dirty)
    source = source_url(agents_repo)
    bodies = read_pack_bodies(agents_repo, packs)

    files: dict[str, str] = {}
    manifest_packs = []
    for pack_id in packs:
        rel = SYNCED_ROOT / f"{pack_id}.md"
        content = render_pack(source, pack_id, version, bodies[pack_id])
        files[rel.as_posix()] = content
        manifest_packs.append(
            {
                "id": pack_id,
                "file": rel.as_posix(),
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
        )

    manifest = {
        "source": source,
        "version": version,
        "packs": manifest_packs,
    }
    files[(SYNCED_ROOT / "manifest.json").as_posix()] = (
        json.dumps(manifest, indent=2) + "\n"
    )

    existing = read_text(repo / "AGENTS.md")
    files["AGENTS.md"] = upsert_agents_md(
        existing, render_block(source, version, packs)
    )
    return files


def load_packs(repo: Path) -> list[str]:
    path = repo / "agents.sync.json"
    if not path.is_file():
        raise SyncError(
            f"missing {path}. Copy examples/agents.sync.json from the agents repo "
            "and list the packs this project wants."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SyncError(f"{path} is not valid JSON: {exc}") from exc
    packs = data.get("packs") if isinstance(data, dict) else None
    if not isinstance(packs, list) or not packs or not all(isinstance(p, str) for p in packs):
        raise SyncError(f"{path} must contain a non-empty packs array of strings")
    seen: set[str] = set()
    for pack_id in packs:
        if not PACK_ID.fullmatch(pack_id):
            raise SyncError(
                f"invalid pack id {pack_id!r}. Use one directory and a file stem, "
                "such as languages/python."
            )
        if pack_id in seen:
            raise SyncError(f"duplicate pack id {pack_id!r}")
        seen.add(pack_id)
    return packs


def git_version(agents_repo: Path, *, allow_dirty: bool) -> str:
    if not (agents_repo / ".git").exists():
        raise SyncError(f"{agents_repo} is not a git checkout")
    sha = git(agents_repo, "rev-parse", "HEAD")
    if sha is None:
        raise SyncError(f"{agents_repo} has no commits to use as a version")
    dirty = git(agents_repo, "status", "--porcelain") or ""
    if dirty.strip():
        if not allow_dirty:
            raise SyncError(
                "agents checkout has uncommitted changes. Commit them so the "
                "synced version matches a revision, or pass --allow-dirty."
            )
        return f"{sha}-dirty"
    return sha


def source_url(agents_repo: Path) -> str:
    remote = git(agents_repo, "remote", "get-url", "origin")
    if not remote:
        return DEFAULT_SOURCE
    remote = remote.strip()
    ssh = re.fullmatch(r"git@github\.com:(.+?)(?:\.git)?", remote)
    if ssh:
        return f"https://github.com/{ssh.group(1)}"
    https = re.fullmatch(r"https://github\.com/(.+?)(?:\.git)?/?", remote)
    if https:
        return f"https://github.com/{https.group(1)}"
    return DEFAULT_SOURCE


def read_pack_bodies(agents_repo: Path, packs: list[str]) -> dict[str, str]:
    bodies: dict[str, str] = {}
    for pack_id in packs:
        path = agents_repo / f"{pack_id}.md"
        if not path.is_file():
            raise SyncError(f"unknown pack {pack_id}: {path} does not exist")
        # Pack ids are a single path segment plus a stem, so this cannot escape
        # agents_repo. Resolve and check anyway.
        resolved = path.resolve()
        if agents_repo not in resolved.parents:
            raise SyncError(f"pack path escapes the agents repo: {pack_id}")
        text = path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        bodies[pack_id] = text
    return bodies


def render_pack(source: str, pack_id: str, version: str, body: str) -> str:
    rel = f"{pack_id}.md"
    return (
        f"<!-- source: {source} path: {rel} version: {version} -->\n"
        "\n"
        f"Synced copy of `{rel}` from {source} at `{version}`. Do not edit.\n"
        "\n"
        f"{body}"
    )


def render_block(source: str, version: str, packs: list[str]) -> str:
    lines = [
        BEGIN,
        "## Shared instructions",
        "",
        "These copies are committed in this repository. Read them here.",
        "Do not clone the agents repo and do not follow a live path to it while working.",
        "Do not edit the copies. Change the pack in the agents repo, then re-run `sync.sh`.",
        "",
        f"- source: {source}",
        f"- version: `{version}`",
        "",
        "| Pack | File |",
        "|------|------|",
    ]
    for pack_id in packs:
        rel = f".agents/synced/{pack_id}.md"
        lines.append(f"| `{pack_id}` | [{pack_id}]({rel}) |")
    lines.append(END)
    return "\n".join(lines) + "\n"


def upsert_agents_md(existing: str | None, block: str) -> str:
    if existing is None:
        return (
            "# Agent instructions\n"
            "\n"
            "Project-specific instructions go here. They override the shared "
            "packs below when they conflict.\n"
            "\n"
            f"{block}"
        )
    if BEGIN in existing or END in existing:
        if BEGIN not in existing or END not in existing:
            raise SyncError(
                "AGENTS.md has only one of the agents-sync markers. "
                "Restore both or remove them, then sync again."
            )
        pattern = re.compile(
            re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?",
            re.DOTALL,
        )
        updated, count = pattern.subn(block, existing, count=1)
        if count != 1:
            raise SyncError("could not replace the agents-sync block in AGENTS.md")
        return updated
    text = existing if existing.endswith("\n") else existing + "\n"
    return text + "\n" + block


def write_outputs(repo: Path, files: dict[str, str]) -> None:
    synced_dir = repo / SYNCED_ROOT
    synced_dir.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    keep = {repo / rel for rel in files if rel.startswith(SYNCED_ROOT.as_posix())}
    for path in synced_dir.rglob("*"):
        if path.is_file() and path not in keep:
            path.unlink()
    for path in sorted(synced_dir.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def drifted_paths(repo: Path, files: dict[str, str]) -> list[str]:
    drifted: list[str] = []
    for rel, content in files.items():
        current = read_text(repo / rel)
        if current != content:
            drifted.append(rel)
    synced_dir = repo / SYNCED_ROOT
    if synced_dir.is_dir():
        expected = {rel for rel in files if rel.startswith(SYNCED_ROOT.as_posix())}
        for path in synced_dir.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(repo).as_posix()
            if rel not in expected:
                drifted.append(rel)
    return drifted


def files_version(files: dict[str, str]) -> str:
    manifest = json.loads(files[(SYNCED_ROOT / "manifest.json").as_posix()])
    return str(manifest["version"])


def pack_count(files: dict[str, str]) -> int:
    manifest = json.loads(files[(SYNCED_ROOT / "manifest.json").as_posix()])
    return len(manifest["packs"])


def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def git(repo: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


if __name__ == "__main__":
    sys.exit(main())
