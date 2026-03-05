#!/usr/bin/env bash
set -euo pipefail
# Block committing files larger than 25MB unless explicitly allowlisted.
# Allowlist: experiments/**/(config|configs|scripts|docs)/, docs/**, README.md
MAX_BYTES=26214400
ALLOW_RE='^(experiments/.*/(config|configs|scripts|docs)/|docs/|README.md$)'

# Get staged files
mapfile -t files < <(git diff --cached --name-only)

failed=0
for f in "${files[@]}"; do
  [[ -e "$f" ]] || continue
  size=$(wc -c < "$f" 2>/dev/null || echo 0)
  if [[ "$size" =~ ^[0-9]+$ ]] && (( size > MAX_BYTES )); then
    if echo "$f" | grep -Eq "$ALLOW_RE"; then
      echo "[block-giant-files] ALLOWLISTED: $f ($(numfmt --to=iec $size))"
    else
      echo "[block-giant-files] ERROR: $f is $(numfmt --to=iec $size), exceeds 25MB limit"
      failed=1
    fi
  fi
done

exit $failed
