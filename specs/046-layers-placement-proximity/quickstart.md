# Quickstart: 層・配置・近接性の実践を文書化する(S5)

## 1. 単体テスト

```bash
python3 -B -m unittest discover -s .claude/skills/maintaining-living-documentation/tests -v
```

期待: 既存の 109 件と、`PracticesDocumentTests` がすべて通る。

## 2. リンク検査

```bash
python3 .claude/skills/maintaining-living-documentation/scripts/check_links.py --root . --changed
```

期待: エラー 0。

## 3. 目視確認

`references/practices.md` の「Layers, placement, and proximity」の節に、9 層の表、コメントの 2 分類、置き場所のパターン、近接性(設計判断)と階層についての注記があること。
