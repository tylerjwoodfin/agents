# General

Project-specific instructions live in the repository `AGENTS.md`. When they conflict with a shared pack, follow `AGENTS.md`.

- Make the smallest change that solves the task. Match the style of the surrounding code.
- Do not fix unrelated bugs in the same change. Ask first.
- Do not add a dependency, framework, or tool the repository does not already use.
- Do not commit or print secrets: tokens, passwords, API keys, `.env` files, or credential dumps.
- Files under `.agents/synced/` are generated copies. Change the pack in the agents repo and re-run `sync.sh`. Do not edit the copies.
