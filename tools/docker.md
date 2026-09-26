# Docker

- Keep Compose and the service README next to the service. The service README is the operator doc.
- Commit `.env.example` with placeholders. Keep real `.env` files untracked.
- Do not bake secrets into images or Compose files.
- Use `docker compose` (Compose v2). Bind published ports to localhost when a tunnel or reverse proxy is what exposes the service.
