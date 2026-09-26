# Life-ops

Prefer the life-ops tools (Cabinet, RemindMail, foodlog, milestone, Immich) over inventing `python ~/git/tools/...` or `cabinet` one-liners.

## Tools

| Tool | When |
|------|------|
| `cabinet_get` | Read config/data by path (`quality.cloud`, `vikunja api_root`, …). Secrets are redacted. |
| `cabinet_put` | Write a string value. Do **not** put secrets unless the user explicitly provides them. |
| `remind_save` | Schedule a reminder (`title`, `when`, optional `notes`/`tags`). |
| `foodlog_add` | Log food with known calories (`food`, `calories`). Do not prompt interactively. |
| `milestone_add` | Append to `milestones.md` for current year/month. |
| `immich_search` | Search photos. Requires Cabinet `immich.api_url` + `immich.api_key`. |

## Rules

- Never print Cabinet tokens, passwords, or API keys into chat.
- If Immich is unconfigured, tell the user to set the two Cabinet keys (see `~/git/tools/lifeops-mcp/README.md`) instead of guessing URLs.
- For ticket implementation, follow [vikunja-ticket.md](vikunja-ticket.md). These tools do not replace that workflow.
- Foodlog without calories: ask the user for a calorie number (or look up from conversation) — do not run the interactive foodlog CLI.
