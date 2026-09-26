#!/usr/bin/env bash
# Full package loop:
#   1. independent verification loops (videos, links, geometry, sheet, stores; partnumbers is agent-run and read from reports/)
#   2. final cross-verification of all reports against each other + the page (--apply = safe fixes)
#   3. build/verify/deploy loop, gated on cross passing
set -u; cd "$(dirname "$0")"
fail=0
for l in loop_partnumbers loop_videos loop_links loop_geometry loop_sheet loop_stores; do echo "== $l"; python3 loops/$l.py || fail=1; done
echo "== loop_cross"; python3 loops/loop_cross.py --apply || fail=1
if [ $fail -ne 0 ]; then echo "CROSS-VERIFY FAILED — see CROSS-REPORT.md; not deploying"; exit 1; fi
exec python3 loop.py --deploy "$@"
