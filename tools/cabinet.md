# Cabinet

Configuration and secrets for these projects live in Cabinet, not in git.

- Read a value with `cabinet --get key` or the life-ops `cabinet_get` tool.
- Write a value with `cabinet put`.
- Never print token, password, or API key values.
- Never commit a Cabinet export.
