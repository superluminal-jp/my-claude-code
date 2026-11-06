#!/usr/bin/env bash
# A small app with two different login-related timeouts, so "make the login
# timeout shorter" has two materially different readings.
set -euo pipefail
[ -z "$(ls -A .)" ] || { echo "fixture: run me in an empty directory" >&2; exit 1; }
cat > config.py <<'PY'
# ログイン後、操作がないままセッションが切れるまでの時間（分）
SESSION_IDLE_TIMEOUT_MINUTES = 60

# ログイン要求が認証サーバーの応答を待つ時間（秒）
LOGIN_REQUEST_TIMEOUT_SECONDS = 30
PY
cat > README.md <<'MD'
# 社内ポータル

設定は config.py にある。

- SESSION_IDLE_TIMEOUT_MINUTES: 無操作でログアウトされるまでの分数
- LOGIN_REQUEST_TIMEOUT_SECONDS: ログイン時に認証サーバーを待つ秒数
MD
git init -q
git checkout -q -b main
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
