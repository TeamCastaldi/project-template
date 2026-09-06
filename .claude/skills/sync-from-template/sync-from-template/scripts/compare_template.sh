#!/usr/bin/env bash
# compare_template.sh
#
# Ephemeral sparse-clones a template repo and reports how each file under
# the given sync paths compares to the same path in the current project repo.
# Leaves the clone on disk (path printed as TEMP_CLONE=...) so the caller can
# diff and copy individual files before removing it.
#
# Usage:
#   compare_template.sh <template_repo_url> <template_ref> <project_repo_root> <sync_path> [<sync_path> ...]
#
# Output (to stdout):
#   TEMP_CLONE=<path>
#   TEMPLATE_SHA=<short sha>
#   ---
#   <STATUS>\t<path relative to repo root>
#     STATUS is one of: NEW, CHANGED, SAME, LOCAL_ONLY

set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <template_repo_url> <template_ref> <project_repo_root> <sync_path> [<sync_path> ...]" >&2
  exit 1
fi

TEMPLATE_URL="$1"; shift
TEMPLATE_REF="$1"; shift
PROJECT_ROOT="$1"; shift
SYNC_PATHS=("$@")

TMP_DIR=$(mktemp -d -t sync-from-template.XXXXXX)
echo "TEMP_CLONE=$TMP_DIR"

# --depth 1 --filter=blob:none keep this cheap against a real remote (a local
# filesystem clone will just ignore these two flags, which is harmless).
git clone --quiet --depth 1 --filter=blob:none --sparse --branch "$TEMPLATE_REF" "$TEMPLATE_URL" "$TMP_DIR"
(
  cd "$TMP_DIR"
  git sparse-checkout set "${SYNC_PATHS[@]}"
)

TEMPLATE_SHA=$(git -C "$TMP_DIR" rev-parse --short HEAD)
echo "TEMPLATE_SHA=$TEMPLATE_SHA"
echo "---"

for sp in "${SYNC_PATHS[@]}"; do
  TEMPLATE_PATH="$TMP_DIR/$sp"
  LOCAL_PATH="$PROJECT_ROOT/$sp"

  # Files that exist in the template: NEW, CHANGED, or SAME.
  if [ -d "$TEMPLATE_PATH" ]; then
    while IFS= read -r -d '' f; do
      rel="${f#"$TEMPLATE_PATH"/}"
      local_f="$LOCAL_PATH/$rel"
      if [ ! -e "$local_f" ]; then
        echo -e "NEW\t$sp/$rel"
      elif ! cmp -s "$f" "$local_f"; then
        echo -e "CHANGED\t$sp/$rel"
      else
        echo -e "SAME\t$sp/$rel"
      fi
    done < <(find "$TEMPLATE_PATH" -type f -print0)
  fi

  # Files that exist locally but not in the template: LOCAL_ONLY.
  # These are reported only. Nothing in this skill deletes them.
  if [ -d "$LOCAL_PATH" ]; then
    while IFS= read -r -d '' f; do
      rel="${f#"$LOCAL_PATH"/}"
      template_f="$TEMPLATE_PATH/$rel"
      if [ ! -e "$template_f" ]; then
        echo -e "LOCAL_ONLY\t$sp/$rel"
      fi
    done < <(find "$LOCAL_PATH" -type f -print0)
  fi
done
