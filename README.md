# agents

Reusable instructions for coding agents.

This repo owns guidance that should still apply if the editor or agent runtime changes. [dotfiles](https://github.com/tylerjwoodfin/dotfiles) owns machine setup: Cursor and OpenClaw adapters, symlinks, shell config, and bootstrap scripts. Adapters may point here. They do not keep a second copy of the instruction text.

```text
agents
   ↓
dotfiles installs/adapts
   ↓
Cursor / OpenClaw / other local tools
```

Project-specific behavior stays in each repository's `AGENTS.md`.

## Layout

```text
common/          behavior that applies to any task
languages/       python, javascript, bash
frameworks/      react
tools/           git, testing, docker, cabinet, and local workflows
examples/        sample agents.sync.json
sync.sh          write committed copies into a project
```

A pack is one markdown file, one directory deep: `languages/python.md`.

## Opt in a project

From the project root, add `agents.sync.json` (start from `examples/agents.sync.json`):

```json
{
  "packs": [
    "common/general",
    "languages/python",
    "tools/git",
    "tools/testing"
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

Committed copies are what an agent reads inside that project. Do not clone this repo or follow a live path to it during that work. Cursor and OpenClaw on a machine are different: their adapters in dotfiles read this checkout directly.

## Adding a pack

1. Add `category/name.md` under `common/`, `languages/`, `frameworks/`, or `tools/`.
2. Keep project facts, secrets, and host inventories out of packs. Those belong in the project `AGENTS.md`.
3. Run `bash tests/sync_test.sh`.
4. In each project that should receive it, add the pack id to `agents.sync.json` and re-run `sync.sh`.
