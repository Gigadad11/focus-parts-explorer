#!/usr/bin/env bash
# Full package loop: verify everything, then deploy only if every stage passed.
cd "$(dirname "$0")" && exec python3 loop.py --deploy "$@"
