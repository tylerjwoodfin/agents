#!/usr/bin/env bash
# Copy selected instruction packs into the current project repository.
#
# Usage:
#   ~/git/agents/sync.sh              # repo is $PWD
#   ~/git/agents/sync.sh --repo PATH
#   ~/git/agents/sync.sh --check
#   ~/git/agents/sync.sh --dry-run
#
# The project must contain agents.sync.json. Commit the files this writes
# (.agents/synced/ and the shared block in AGENTS.md). Do not fetch this
# repo while an agent is working in the project.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$ROOT/sync.py" "$@"
