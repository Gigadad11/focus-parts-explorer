#!/usr/bin/env bash
# Full package loop (run after ANY edit; never hand-deploy):
#   1. deterministic loops: videos, links, geometry, sheet, stores, systems
#   2. agentic loops (each runs its own `claude -p`, cached on the data it judges; --fresh to force):
#        partnumbers  web-checks changed part numbers        modelqc  judges 3D placement       uiqc  judges usability
#   3. cross-verification of all reports against each other + the page (--apply = safe fixes; --apply-model also moves parts)
#   4. build/verify/deploy loop, gated on cross passing
# Flags: --no-agents (skip step 2), --fresh (re-run agents even if cached), --apply-model, anything else goes to loop.py
set -u; cd "$(dirname "$0")"
agents=1; fresh=""; applymodel=""; rest=()
for a in "$@"; do case "$a" in --no-agents) agents=0;; --fresh) fresh="--fresh";; --apply-model) applymodel="--apply-model";; *) rest+=("$a");; esac; done
fail=0
for l in loop_videos loop_links loop_geometry loop_sheet loop_stores loop_systems; do echo "== $l"; python3 loops/$l.py || fail=1; done
if [ $agents -eq 1 ]; then
  for l in loop_partnumbers loop_modelqc loop_uiqc; do echo "== $l"; python3 loops/$l.py $fresh || { echo "$l failed (non-blocking)"; }; done
fi
echo "== loop_cross"; python3 loops/loop_cross.py --apply $applymodel || fail=1
if [ $fail -ne 0 ]; then echo "CROSS-VERIFY FAILED — see CROSS-REPORT.md; not deploying"; exit 1; fi
exec python3 loop.py --deploy "${rest[@]}"
