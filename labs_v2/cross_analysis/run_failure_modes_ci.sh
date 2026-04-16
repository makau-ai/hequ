#!/usr/bin/env bash
# run_failure_modes_ci.sh — end-to-end CI runner for the
# failure_modes + unity_map pipeline.
#
# Invokes, in order:
#   1. framework/test_dov_dsl.py              (parser + evaluator unit tests)
#   2. cross_analysis/test_validate_failure_modes.py   (validator negative tests)
#   3. cross_analysis/validate_failure_modes.py        (validator positive path
#                                                       on the real live corpus)
#   4. cross_analysis/build_unity_map.py               (regenerate unity_map.yaml)
#
# Exits nonzero on the first failure. Designed to be dropped into a
# pre-commit hook, a Makefile target, or any CI runner — no external
# state, only needs the pinned python venv.
#
# Usage:
#   bash labs_v2/cross_analysis/run_failure_modes_ci.sh
set -euo pipefail

PY="${PY:-/tmp/hequ_venv/bin/python}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

step() { printf '\n\033[1;36m▸ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✔ %s\033[0m\n' "$*"; }
fail() { printf '\033[1;31m✘ %s\033[0m\n' "$*"; exit 1; }

step "1/4 DOV-DSL parser + evaluator tests"
"$PY" labs_v2/framework/test_dov_dsl.py \
  && ok "dov_dsl tests passed" \
  || fail "dov_dsl tests failed"

step "2/4 Validator negative-test fixtures"
"$PY" labs_v2/cross_analysis/test_validate_failure_modes.py \
  && ok "validator negative tests passed" \
  || fail "validator negative tests failed"

step "3/4 Referential integrity on the live corpus"
"$PY" labs_v2/cross_analysis/validate_failure_modes.py \
  && ok "live corpus referential integrity OK" \
  || fail "live corpus has referential errors — fix equation.yaml or unbound DOV-DSL vars"

step "4/4 Regenerate unity_map.yaml from descriptors"
"$PY" labs_v2/cross_analysis/build_unity_map.py \
  && ok "unity_map.yaml regenerated" \
  || fail "unity map generation failed"

printf '\n\033[1;32mAll failure_modes CI checks passed.\033[0m\n'
