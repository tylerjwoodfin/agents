# agents

This repository is the source for shared instruction packs. Project repositories keep their own `AGENTS.md` and commit copies produced by `sync.sh`.

## Editing

- Put reusable instructions in `base/`, `languages/`, `frameworks/`, or `tooling/`. One pack is one markdown file, one directory deep (`tooling/git.md`).
- Do not put project-specific facts, secrets, or host inventories in a pack.
- Do not sync this repository into itself.

## Checks

```bash
bash tests/sync_test.sh
```
