# Quickstart: secure-logging の検証

実装後に、仕様の成功基準を確かめる手順。自動で確かめられるものと、手動のものを分ける。

## 自動

前提: リポジトリのルートで実行する。

```bash
bash tests/run-secure-logging-skill.sh
bash tests/run-config-pyramid.sh
python3 /Users/taikiogihara/.claude/skills/maintaining-living-documentation/scripts/check_links.py --changed
```

期待: 全件合格、リンク検査のエラー 0 件(SC-003、SC-006、SC-007)。契約テストは構造と出典の規則を確かめるだけで、検査の挙動は確かめない。

## 手動(検査の挙動)

前提: スキルを `~/.claude/` に同期済み(`bash install.sh`)。検証用サンプルは `tests/fixtures/secure-logging/defective_auth.py`、期待は同ディレクトリの `expected.md`。

1. 新しいセッションで、サンプルに対して「このコードのログが良い慣行に沿っているか検査して」と依頼する。
2. 報告が [検査報告の契約](contracts/inspection-report.md) の順序であること、`expected.md` の不合格項目がすべて場所付きで報告されること、group B が Pass になっていないことを確認する(SC-001、SC-002)。
3. 同じサンプルで「認証失敗のログを足して」と依頼する。完了報告に、実装より先に失敗していたテストが示されること、秘密情報の見本値がログ出力に現れないことを確認する(SC-004、SC-005)。

手動の結果は自動検査ではなく、実行した日付と結果をこのファイルの末尾に追記して残す。未実行の間は未検証として扱う。

## 手動確認の状況

未検証: 手動手順 1〜3 はまだ実行していない(SC-001、SC-004、SC-005 は未検証)。実行したら日付と結果に置き換える。
