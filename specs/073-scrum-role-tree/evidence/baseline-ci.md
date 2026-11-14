# 変更前の CI の実行スクリプトの結果

- 実行日: 2026-11-15
- ブランチ: `feat/scrum-role-tree`。`main`（`e4f2992`）から分けた直後で、`harness/` と `tests/` は変えていない状態。
- 実行者: `check-runner` サブエージェント。Claude Code の Bash サンドボックスの中で実行した。
- 実行したもの: `.github/workflows/ci.yml` が呼ぶ16の実行スクリプトを、この順に1回ずつ実行した。

| # | コマンド | 終了コード | 最後の要約行 |
|---|---|---|---|
| 1 | `bash tests/run-install.sh` | 0 | All installer contract checks passed. |
| 2 | `bash tests/run-config-pyramid.sh` | 0 | Results: 52 passed, 0 failed |
| 3 | `bash tests/run-harness-skills.sh` | 0 | Results: 8 passed, 0 failed |
| 4 | `bash tests/run-removed-guardrails.sh` | 0 | Results: 5 passed, 0 failed |
| 5 | `bash tests/run-sandbox-settings.sh` | 0 | Results: 67 passed, 0 failed |
| 6 | `bash tests/run-commit-tree-hook.sh` | 0 | Results: 18 passed, 0 failed |
| 7 | `bash tests/run-package-safety-bundle.sh` | 0 | Results: 21 passed, 0 failed |
| 8 | `bash tests/run-readme-skill-index.sh` | 0 | Results: 46 passed, 0 failed |
| 9 | `bash tests/run-specify-requirements-skill.sh` | 0 | Results: 5 passed, 0 failed |
| 10 | `bash tests/run-verify-change-skill.sh` | 0 | Results: 8 passed, 0 failed |
| 11 | `bash tests/run-draw-system-diagrams-skill.sh` | 0 | system-diagrams: 4 passed, 0 failed |
| 12 | `bash tests/run-apply-secure-logging-skill.sh` | 0 | Results: 38 passed, 0 failed |
| 13 | `bash tests/run-apply-dads-frontend-skill.sh` | 0 | Results: 75 passed, 0 failed |
| 14 | `bash tests/run-build-dads-slides-skill.sh` | 0 | Results: 122 passed, 0 failed, 3 skipped（Playwright が入っていないため） |
| 15 | `bash tests/run-harness-eval.sh` | 0 | harness-eval: passed |
| 16 | `bash tests/run-mcp-startup.sh` | 1 | MCP startup smoke test failed: 1 package(s). |

## 変更前から失敗していたもの

16 の失敗した箇所の出力（そのまま引用）:

```text
FAIL awslabs.aws-documentation-mcp-server@latest did not start cleanly
error: failed to open file `/Users/taikiogihara/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
MCP startup smoke test failed: 1 package(s).
```

uv のキャッシュ（`~/.cache/uv`）への読み書きを、サンドボックスが拒んだために失敗した。この失敗はリポジトリの内容によるものではなく、この変更の前からある。変更後も同じ理由で失敗するなら、AC-COMPAT-2 の「同じ理由で失敗する」に当たる。

12 の出力には、`api.anthropic.com:443` と `http-intake.logs.us5.datadoghq.com:443` への接続をサンドボックスが拒んだことを示す行も出ていた。それでも、検査はすべて通り、終了コードは 0 だった。
