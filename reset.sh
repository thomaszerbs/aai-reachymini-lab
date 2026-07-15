#!/usr/bin/env bash
#
# reset.sh — revert the mini-lab to a clean slate between attendees.
#
# Task 3 is hands-on: each attendee edits the VISION_PROMPT line in
# lab/emo_v3.py (and maybe the bonus TRY-ME blocks in emo_v1.py / emo_v2.py, or
# the LAB.md guide they have open). This script restores the pristine lab files
# from the .lab-baseline/ snapshot that ./setup.sh captured, touching ONLY those
# lab files and nothing else.
#
# It does a plain copy (cp) — this is deliberately NOT a git-based reset, because
# the booth working tree carries lots of intentional uncommitted work.
#
set -euo pipefail

# --- locate the repo root (this script's own directory) so CWD doesn't matter ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- config (keep in sync with setup.sh) -----------------------------------
# Every file an attendee could edit during the lab (the three task scripts plus
# the LAB.md guide they have open). Baseline snapshots use each file's basename,
# so these names must be unique.
LAB_BASELINE_DIR=".lab-baseline"
LAB_FILES=(lab/emo_v1.py lab/emo_v2.py lab/emo_v3.py lab/LAB.md)

# --- pretty output helpers (match setup.sh) --------------------------------
section() {
    echo
    echo "=================================================================="
    echo "🤖 $1"
    echo "=================================================================="
}
ok()   { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
err()  { echo "❌ $*" >&2; }

# --- main ------------------------------------------------------------------
section "Reachy Mini mini-lab — reset between attendees"

if [[ ! -d "$LAB_BASELINE_DIR" ]]; then
    err "No baseline found at ${LAB_BASELINE_DIR}/ — nothing to restore from."
    err "Run ./setup.sh first (it captures the baseline), or create it by copying"
    err "the pristine lab scripts into ${LAB_BASELINE_DIR}/ by hand."
    exit 1
fi

echo "Restoring the lab files from ${LAB_BASELINE_DIR}/ ..."
missing=0
for f in "${LAB_FILES[@]}"; do
    src="$LAB_BASELINE_DIR/$(basename "$f")"
    if [[ ! -f "$src" ]]; then
        err "Baseline copy missing: $src"
        missing=1
        continue
    fi
    cp "$src" "$f"
    echo "    restored: $f"
done

if [[ "$missing" -eq 1 ]]; then
    err "One or more baseline files were missing (see above)."
    err "Re-capture the baseline: delete ${LAB_BASELINE_DIR}/ and run ./setup.sh."
    exit 1
fi

echo
ok "Reset to clean slate. Restored: ${LAB_FILES[*]}"
echo "Ready for the next attendee. 🤖"
