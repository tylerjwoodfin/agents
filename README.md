# agents

Shared AI coding instructions for project repositories.

Project-specific behavior stays in each repository's `AGENTS.md`. Reusable packs live here. `sync.sh` copies the packs a project selects into that project. Commit the copies. Agents then read the committed files. They do not clone this repo and they do not follow a live path to a checkout of it.

Cursor skills and rules still live in [dotfiles](https://github.com/tylerjwoodfin/dotfiles) and are symlinked onto a machine. This repo is the part that must travel inside each project.

## Layout

```text
base/            behavior that applies to any project
languages/       python, javascript, bash
frameworks/      react
tooling/         git, testing, docker, cabinet
examples/        sample agents.sync.json
sync.sh          write committed copies into a project
```

A pack is one markdown file, one directory deep: `languages/python.md`.

## Opt in a project

From the project root, add `agents.sync.json` (start from `examples/agents.sync.json`):

```json
{
  "packs": [
    "base/general",
    "languages/python",
    "tooling/git",
    "tooling/testing"
  ]
}
```

Sync, then commit the result:

```bash
~/git/agents/sync.sh
git add agents.sync.json AGENTS.md .agents
```

`sync.sh` writes:

| Path | Role |
|------|------|
| `.agents/synced/<pack>.md` | Pack copy, with source URL, source path, and git revision |
| `.agents/synced/manifest.json` | Same revision plus a sha256 of each copy |
| `AGENTS.md` | Project instructions, plus a `agents-sync` block that links the copies |

An existing `AGENTS.md` is left in place. Only the block between `<!-- agents-sync:begin -->` and `<!-- agents-sync:end -->` is replaced. If the file is missing, sync creates a short project stub above that block.

```bash
~/git/agents/sync.sh --dry-run   # list files, write nothing
~/git/agents/sync.sh --check     # fail if committed copies would change
```

The agents checkout must be clean. The version recorded in the copies is `git rev-parse HEAD`. Commit pack edits here before syncing them out. `--allow-dirty` records `<sha>-dirty` and is for local experiments.

## Adding a pack

1. Add `category/name.md` under `base/`, `languages/`, `frameworks/`, or `tooling/`.
2. Keep project facts, secrets, and host inventories out of packs. Those belong in the project `AGENTS.md`.
3. Run `bash tests/sync_test.sh`.
4. In each project that should receive it, add the pack id to `agents.sync.json` and re-run `sync.sh`.
