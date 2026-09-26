# Ticket workflow (Vikunja)

Vikunja at `https://v.tyler.cloud` is the TJW board. Implement the ticket
directly in the repo. Use `~/git/tools/vikunja/ticket.py`. `v` creates a ticket;
this workflow loads and finishes existing ones.

## When to use

- `implement TJW-242` / `fix tjw-242`
- Any request to implement a ticket by ref
- `v new …` creates a ticket on the TJW board

## Configuration (Cabinet)

Read via `cabinet --get` / life-ops `cabinet_get` (never print secrets):

| Key | Purpose |
|-----|---------|
| `vikunja.api_root` | Direct API, `http://127.0.0.1:3456/api/v1` (bypasses Authentik) |
| `vikunja.api_token` | Bearer token for the CLI user |
| `vikunja.base_url` | Public UI, `https://v.tyler.cloud` |
| `backloggist.github_token` | GitHub PAT with `repo` (also used by `gh auth`) |

After a fix, move the card to **Testing** unless the user names another column.

Do not call `https://v.tyler.cloud/api/v1` from scripts. Authentik sits in front
of that host. The loopback root above is the stable one.

## Workflow

### 1. Load the ticket

```bash
python3 ~/git/tools/vikunja/ticket.py get TJW-242
```

### 2. Choose repository

- If the ticket **explicitly names** a path (`~/git/tyler.cloud`, `github.com/.../repo`), work **only** in that repo.
- Otherwise explore `~/git` and touch only repos the ticket requires.
- Default workspace root: `~/git`.
- If the repo has `AGENTS.md`, follow its branch/PR conventions over the defaults below.

### 3. Branch

Default format: `{prefix}/TJW-###-{short-slug}`

Infer prefix from ticket text: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, or `task`.

```bash
cd <repo> && git checkout -b feat/TJW-242-short-slug
```

### 4. Implement

Follow [vikunja-ticket-template.md](vikunja-ticket-template.md).

- Match existing code style in the target repo.
- Run tests and linting defined by that project.
- Do not scope-creep beyond the ticket.

### 5. Commit

Message format: `TJW-###: short summary` (ticket ref required).

### 6. Push and open PR

`gh` lives at `~/.local/bin/gh` (PATH must include `~/.local/bin`).

If `gh auth status` fails or warns about login, sync the Cabinet PAT first
(token may lack `read:org`; **repo** scope is enough for PRs):

```bash
python3 ~/git/tools/github/ensure_gh_auth.py
```

```bash
cd <repo>
git push -u origin HEAD
gh pr create --title "TJW-###: title" --body "$(cat <<'EOF'
## Summary
- ...

## Test plan
- [ ] ...
EOF
)"
```

If the repo's `AGENTS.md` says to target a release branch, set `--base` accordingly.

GitHub owner default: `tylerjwoodfin`.

### 7. Update the ticket

Move the ticket to **Testing** and comment with PR link(s):

```bash
python3 ~/git/tools/vikunja/ticket.py finish TJW-242 --comment "$(cat <<'EOF'
Fixed by the implementing agent.

Pull requests:
- https://github.com/...
EOF
)"
```

## Dry-run / plan-only

If the user says "plan" or "dry-run", fetch the ticket and outline the approach
without pushing or updating the ticket unless they ask to proceed.

## Do not

- Import `backloggist` / `automation` (removed).
- Shell out to `codex exec`.
- Print `vikunja.api_token` or other Cabinet secrets.
- Skip tests when the repo has them.
- Push or update the ticket without user approval on ambiguous tickets.
