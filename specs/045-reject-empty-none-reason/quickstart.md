# Quickstart: 空の「不要」理由を弾く(S3)

実装後に、動作を確認する手順。

## 1. 単体テスト

```bash
python3 -B -m unittest discover -s .claude/skills/maintaining-living-documentation/tests -v
```

期待: 既存の 90 件と、追加した ReportQualityTests・StopGateTests がすべて通る。

## 2. 純粋関数の手動確認

```bash
cd .claude/skills/maintaining-living-documentation/scripts
python3 -B -c "
import stop_gate as g
for r in ('', 'n/a', 'なし。', '<reason>', 'comment only', '内部の変数名のみの変更で公開される挙動は不変'):
    print(repr(r), g.is_boilerplate(r))
print(g.none_declarations('Done.\n\n- **Documentation impact**: none — internal refactor.'))
"
```

期待: 先頭 4 つが `True`、後ろ 2 つが `False`。不要宣言の理由として `['internal refactor.']` が得られる。

## 3. ゲートの動作(単体テストが自動化している)

- 実装系の変更のみ + `Documentation impact: none —`(理由なし)→ `block`
- 同 + `Documentation impact: none — n/a` → `block`
- 同 + 具体的な理由 → 通る
- 同 + 見出しのみ → `block`、`Updated:` または具体的な `No change needed:` を足すと通る
- `LIVING_DOCS_GATE=warn` → 警告のみ、`off` → 何もしない

## 4. リンク検査

```bash
python3 .claude/skills/maintaining-living-documentation/scripts/check_links.py --root . --changed
```

期待: エラー 0。
