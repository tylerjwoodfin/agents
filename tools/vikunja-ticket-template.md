# Ticket implementation template

Use this checklist for every ticket implementation.

## Understand

- [ ] Read title, description, and attachments
- [ ] Confirm target repo(s) — prefer explicit `~/git/<name>` mentions in the ticket
- [ ] Scan README / nearby code for conventions

## Implement

- [ ] Create branch `{prefix}/{TJW-###}-{slug}` before first edit
- [ ] Smallest correct diff; no drive-by refactors
- [ ] Handle loading/error/empty states when the ticket is UI work
- [ ] Wire to existing backend patterns (do not invent parallel APIs unless required)

## Verify

- [ ] Run project tests (`npm test`, `pytest`, etc.) for each changed repo
- [ ] Run lint/format if the repo defines it
- [ ] Manual smoke test when behavior is user-visible

## Ship

- [ ] Commit: `TJW-###: <summary>`
- [ ] Push branch
- [ ] Open GitHub PR with Summary + Test plan
- [ ] Comment on the ticket with the PR link; move it to `Testing` (or the column the user named)

## PR body template

```markdown
## Summary
<what changed and why — 1–3 bullets>

## Test plan
- [ ] <concrete check the reviewer can run>
```
