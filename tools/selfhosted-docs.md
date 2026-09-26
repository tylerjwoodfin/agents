# Selfhosted docs (homelab)

"docs" will generally refer to `~/syncthing/notes/docs`.
"notes" will generally refer to `~/syncthing/notes`.

When working on Tyler’s homelab, selfhosted services, network hosts (`rainbow`, `ice`, `icecream`, `cloud`), Syncthing, SSH/SFTP, Pi-hole, Immich, Tailscale, backups, or related ops:

- Treat **`~/syncthing/notes/docs/selfhosted/`** as primary operator docs (start with `README.md`; also in the workspace as `syncthing/notes/docs` when that folder is open).
- Prefer those notes over inventing setup steps. Read the relevant file first (e.g. `cloud services and tunnels.md`, `syncthing.md`, `ssh and sftp for cloud and rainbow.md`).
- Compose READMEs under `~/git/docker/<service>/` win when they disagree with a short note.
- Resolve host access with `which <host>` and [homelab-ssh.md](homelab-ssh.md). Do not hardcode IPs from memory.
