# Home Assistant

HA runs on a **separate LAN node**, not on `cloud`. Edit it through the API;
there is no SSH to the box from here.

## Reachability

| URL | Notes |
|-----|--------|
| `http://192.168.1.25:8123` | Use this from `cloud` and over WireGuard |
| `http://homeassistant.local:8123` | mDNS only — **fails over VPN** and often on `cloud` |
| `https://…:8123` | Wrong — HA serves **HTTP** on 8123 |

Compose stub on this machine (`~/git/docker/homeassistant`) is not the running
instance; config lives on the HA host.

## Auth (Cabinet)

| Key | Purpose |
|-----|---------|
| `keys.homeassistant` | Long-lived access token |

Read the token with system Python/`cabinet` (life-ops `cabinet_get` **redacts**
secrets). Never print the token in chat.

```bash
export HA_TOKEN="$(python3 -c "from cabinet import Cabinet; print(Cabinet().get('keys','homeassistant'))")"
export HA_URL="http://192.168.1.25:8123"
```

Smoke test: `GET $HA_URL/api/` with `Authorization: Bearer $HA_TOKEN` → 200.

System Python often lacks `websockets`. Use a venv when you need the WebSocket
API (`python3 -m venv /tmp/ha-venv && /tmp/ha-venv/bin/pip install websockets`).

## REST vs WebSocket

| Task | How |
|------|-----|
| States, history, logbook | REST `/api/states`, `/api/history/period/{iso_start}`, `/api/logbook/{iso_start}` |
| Automation config | REST `/api/config/automation/config/{id}` — `{id}` is `attributes.id`, **not** the entity_id |
| Lovelace | WebSocket only (`/api/lovelace/*` REST is 404) |
| Helpers (`timer`, `input_boolean`) | WebSocket `timer/create`, `input_boolean/create` |
| Automation traces | WebSocket `trace/list` (`item_id` = automation unique id). REST `/api/trace/list/…` is 404 |

## Automations

The config key is `attributes.id` on `GET /api/states/automation.<slug>` (a
numeric timestamp like `1763529213229`, or a string like
`dehumidifier_max_runtime`). Using the entity slug (`dehumidifier`) returns
**404**.

```bash
GET  $HA_URL/api/config/automation/config/{id}
POST $HA_URL/api/config/automation/config/{id}   # full JSON body → {"result":"ok"}, reloads
```

This install uses the 2024.8+ schema: `triggers` / `conditions` / `actions`.

## Helpers

WebSocket after auth:

- Create: `timer/create` (`name`, `duration` e.g. `"0:30:00"`, optional `icon`,
  `restore`) or `input_boolean/create` (`name`, optional `icon`)
- Delete: `timer/delete` with **`timer_id`**, `input_boolean/delete` with
  **`input_boolean_id`** (the helper unique_id / slug). `item_id` is rejected.

## Traces

```json
{"type": "trace/list", "domain": "automation", "item_id": "<attributes.id>"}
```

`item_id` is the same config id as automations above, not `automation.foo`.

## Editing Lovelace dashboards

REST `/api/lovelace/*` returns 404 on this install. Use the **WebSocket** API:

1. Connect to `ws://192.168.1.25:8123/api/websocket`
2. Auth with the token
3. `lovelace/dashboards/list` → dashboards
4. `lovelace/config` (optional `url_path`) → full config
5. Mutate JSON → `lovelace/config/save` with `config`

Overview dashboard is storage-mode (`url_path` `lovelace` / default).

### PoC note

**Humidity Over Time** (`statistics-graph` on the Home view) supports per-entity
`color` (e.g. `yellow` / `white`). Entity entries can be strings or
`{entity, color, name}` objects.

## Rules

- Prefer IP over `.local` unless the user is on the LAN with working mDNS.
- Do not invent SSH/Samba access; API only unless the user opens another path.
- Keep dashboard and automation edits minimal; confirm after
  `lovelace/config/save` or the automation POST.
