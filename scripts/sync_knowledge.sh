#!/usr/bin/env bash
# Sync workflow: AnyType ↔ Markdown ↔ Git
# Run periodically or before/after editing in AnyType or markdown files.
#
# Usage:
#   ./sync_knowledge.sh          # Full sync (export → git commit)
#   ./sync_knowledge.sh --import # Import markdown changes to AnyType first
#   ./sync_knowledge.sh --export # Export only (no import)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIDGE="$SCRIPT_DIR/anytype_bridge.py"
KNOWLEDGE_DIR="${KNOWLEDGE_DIR:-$HOME/knowledge}"
SPACE="${ANYTYPE_SPACE:-Research}"
PYTHON_DEPS="--with requests --with pyyaml"
AGENTS_DIR="$HOME/repos/cytognosis/agents"

cd "$AGENTS_DIR"

echo "📚 Knowledge sync: space=$SPACE dir=$KNOWLEDGE_DIR"
echo "────────────────────────────────────────"

# Parse args
MODE="sync"
case "${1:-}" in
    --import) MODE="import" ;;
    --export) MODE="export" ;;
esac

# Step 1: Import markdown → AnyType (if --import or default sync)
if [[ "$MODE" == "import" || "$MODE" == "sync" ]]; then
    echo "⬆️  Importing markdown → AnyType..."
    uv run $PYTHON_DEPS python3 "$BRIDGE" import --space "$SPACE" 2>&1
fi

# Step 2: Export AnyType → markdown
echo "⬇️  Exporting AnyType → markdown..."
uv run $PYTHON_DEPS python3 "$BRIDGE" export --space "$SPACE" 2>&1

# Step 3: Git commit if changes
echo "📦 Checking for changes..."
cd "$KNOWLEDGE_DIR"

if [ ! -d ".git" ]; then
    echo "Initializing git repo in $KNOWLEDGE_DIR"
    git init
    echo ".bridge/" > .gitignore
    git add .gitignore
    git commit -m "chore: initialize knowledge repo"
fi

if git diff --quiet && git diff --cached --quiet; then
    echo "✅ No changes to commit"
else
    git add -A
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
    CHANGED=$(git diff --cached --stat | tail -1)
    git commit -m "sync: $TIMESTAMP

$CHANGED"
    echo "✅ Committed: $CHANGED"
fi

# Step 4: Show status
echo "────────────────────────────────────────"
uv run $PYTHON_DEPS python3 "$BRIDGE" status 2>&1
echo "────────────────────────────────────────"
echo "📚 Sync complete!"
