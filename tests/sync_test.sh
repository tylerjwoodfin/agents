#!/usr/bin/env bash
# Exercise sync.sh against a temporary agents checkout and a temporary project.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

AGENTS="$TMP/agents-src"
PROJECT="$TMP/project"

git_commit() {
  git -C "$1" -c user.email="sync-test@example.com" -c user.name="sync-test" commit -m "$2"
}

mkdir -p "$AGENTS/base" "$AGENTS/languages" "$PROJECT"
cp "$ROOT/sync.py" "$ROOT/sync.sh" "$AGENTS/"
printf '# General\n\nBe brief.\n' > "$AGENTS/base/general.md"
printf '# Python\n\nUse python3.\n' > "$AGENTS/languages/python.md"

git -C "$AGENTS" init -b main >/dev/null
git -C "$AGENTS" add sync.py sync.sh base/general.md languages/python.md
git_commit "$AGENTS" "packs"
SHA="$(git -C "$AGENTS" rev-parse HEAD)"

cat > "$PROJECT/agents.sync.json" <<'EOF'
{
  "packs": ["base/general", "languages/python"]
}
EOF
cat > "$PROJECT/AGENTS.md" <<'EOF'
# Project

PROJECT SPECIFIC TOKEN

EOF

"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS"

GENERAL="$PROJECT/.agents/synced/base/general.md"
PYTHON="$PROJECT/.agents/synced/languages/python.md"
MANIFEST="$PROJECT/.agents/synced/manifest.json"

grep -q "source: https://github.com/tylerjwoodfin/agents path: base/general.md version: $SHA" "$GENERAL"
grep -q "Do not edit." "$GENERAL"
grep -q "Be brief." "$GENERAL"
grep -q "version: $SHA" "$PYTHON"
grep -q "PROJECT SPECIFIC TOKEN" "$PROJECT/AGENTS.md"
grep -q "agents-sync:begin" "$PROJECT/AGENTS.md"
grep -q "languages/python" "$PROJECT/AGENTS.md"
python3 - "$MANIFEST" "$SHA" <<'PY'
import json, sys
manifest = json.loads(open(sys.argv[1], encoding="utf-8").read())
assert manifest["version"] == sys.argv[2], manifest["version"]
assert manifest["source"] == "https://github.com/tylerjwoodfin/agents"
assert [p["id"] for p in manifest["packs"]] == ["base/general", "languages/python"]
assert all(len(p["sha256"]) == 64 for p in manifest["packs"])
PY

cp "$PROJECT/AGENTS.md" "$TMP/agents.before"
cp "$GENERAL" "$TMP/general.before"
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS"
cmp "$TMP/agents.before" "$PROJECT/AGENTS.md"
cmp "$TMP/general.before" "$GENERAL"
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS" --check >/dev/null

printf '# General\n\nBe brief.\n' > "$AGENTS/base/general.md"
echo "local edit" >> "$AGENTS/base/general.md"
set +e
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS" >/dev/null 2>"$TMP/dirty.err"
status=$?
set -e
test "$status" -ne 0
grep -q "uncommitted" "$TMP/dirty.err"
git -C "$AGENTS" checkout -- base/general.md

python3 - "$PROJECT/agents.sync.json" <<'PY'
import json, sys
path = sys.argv[1]
json.dump({"packs": ["base/general"]}, open(path, "w"), indent=2)
open(path, "a").write("\n")
PY
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS"
test ! -e "$PYTHON"
grep -q "PROJECT SPECIFIC TOKEN" "$PROJECT/AGENTS.md"
grep -q "base/general" "$PROJECT/AGENTS.md"
if grep -q "languages/python" "$PROJECT/AGENTS.md"; then
  echo "removed pack still linked from AGENTS.md" >&2
  exit 1
fi

python3 - "$PROJECT/agents.sync.json" <<'PY'
import json, sys
path = sys.argv[1]
json.dump({"packs": ["../secrets"]}, open(path, "w"))
PY
set +e
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS" >/dev/null 2>"$TMP/escape.err"
status=$?
set -e
test "$status" -ne 0
grep -q "invalid pack id" "$TMP/escape.err"

python3 - "$PROJECT/agents.sync.json" <<'PY'
import json, sys
path = sys.argv[1]
json.dump({"packs": ["base/missing"]}, open(path, "w"))
PY
set +e
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS" >/dev/null 2>"$TMP/missing.err"
status=$?
set -e
test "$status" -ne 0
grep -q "unknown pack" "$TMP/missing.err"

# Restore a valid selection and confirm --check notices a hand edit.
python3 - "$PROJECT/agents.sync.json" <<'PY'
import json, sys
path = sys.argv[1]
json.dump({"packs": ["base/general"]}, open(path, "w"), indent=2)
open(path, "a").write("\n")
PY
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS"
echo "hand edit" >> "$GENERAL"
set +e
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS" --check >/dev/null 2>"$TMP/check.err"
status=$?
set -e
test "$status" -ne 0
grep -q "out of date" "$TMP/check.err"

rm -rf "$PROJECT/.agents" "$PROJECT/AGENTS.md"
"$AGENTS/sync.sh" --repo "$PROJECT" --agents-repo "$AGENTS" --dry-run >"$TMP/dry.txt"
test ! -e "$PROJECT/.agents"
test ! -e "$PROJECT/AGENTS.md"
grep -q "would write .agents/synced/base/general.md" "$TMP/dry.txt"
grep -q "would write AGENTS.md" "$TMP/dry.txt"

echo "ok"
