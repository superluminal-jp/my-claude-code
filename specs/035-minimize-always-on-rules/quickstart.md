# 検証ガイド: 常時ロードルールの最小化

**仕様**: [spec.md](./spec.md) | **データモデル**: [data-model.md](./data-model.md)

自動テストは存在しない（ADR-0005 / 0007 により hooks とスクリプトは撤去済み、本機能でも復活させない）。以下はすべて手動確認手順であり、SC-001〜SC-007 に 1 対 1 で対応する。すべてリポジトリルートで実行する。

## 前提

```sh
cd /Users/taikiogihara/work/my-claude-code
git branch --show-current   # → 035-minimize-always-on-rules
```

ベースライン値（変更前、`a884d6f` 時点）:

| 指標 | 値 |
|---|---|
| `.claude/rules/*.md` 合計 | 36,165 B |
| 最大ファイル | `live-documentation.md` 158 行 / 14,760 B |
| `.claude/skills/` の speckit 以外のスキル数 | 10 |
| ルール内のスキル列挙数 | 7（`adr` / `apple-notes` / `apple-reminders` が欠落） |

---

## 1. SC-001 — 合計バイト数が 16,000 B 以下

```sh
cat .claude/rules/*.md | wc -c
```

**期待**: 16,000 以下（見込み 約 13,100）。削減率は `(36165 - 実測) / 36165`。

ファイル別の内訳を見る場合:

```sh
wc -c .claude/rules/*.md | sort -n
```

## 2. SC-002 — どのファイルも 200 行未満

```sh
wc -l .claude/rules/*.md | awk '$2 != "total" && $1 >= 200 {print "VIOLATION:", $2, $1; f=1} END {exit f+0}' && echo "OK: 全ファイル 200 行未満"
```

**期待**: `OK: 全ファイル 200 行未満`。違反があれば該当ファイルと行数が出る。

## 3. SC-003 — 拒否と非拒否の両方向

**3a. 設定が入っていること**

```sh
python3 -c "import json;d=json.load(open('.claude/settings.json'));print('\n'.join(d['permissions']['deny']))"
```

**期待**: [contracts/permissions-deny.md](./contracts/permissions-deny.md) の確定形と一致。単一先頭スラッシュ `/` で始まるパターンが 0 件であること（`~/` と `**/` のみ）。

**3b. 拒否されること（実挙動）**

新しい Claude Code セッションで、スクラッチの `.env` を作って読ませる:

```sh
printf 'SECRET=dummy\n' > /tmp/claude-deny-check/.env   # 事前に mkdir -p
```

そのディレクトリで起動したセッションに `.env` を読ませ、拒否されることを確認する。`cat` 経由でも拒否されること（Claude Code が認識する Bash ファイルコマンドは deny の対象 — research.md D4）。

**3c. 過剰阻害がないこと**

同じセッションで以下が**読める**ことを確認する:

```
.claude/keybindings.json
.claude/settings.json
docs/live-documentation-standards.md
```

**期待**: いずれも拒否されない。1 件でも拒否されればパターンが広すぎる（research.md D2）。

**3d. 既知の副作用が想定どおりであること**

`.env.example` が読めなくなっていること、`.env` の**作成**も拒否されることを確認する。これは意図した帰結であり、失敗ではない（[contracts/permissions-deny.md](./contracts/permissions-deny.md) 「受け入れる帰結」）。想定と違う挙動（例: 作成は通る）が出た場合は、ドキュメントの記述が誤っているので修正する。

## 4. SC-004 — スキル列挙の矛盾が 0 件

```sh
echo "実体: $(ls .claude/skills | grep -vc '^speckit-') 個"
grep -rn "minto-reviewer\|minto-rewriter\|minto-builder\|scrum-master\|digital-agency-frontend" .claude/CLAUDE.md .claude/rules/*.md
```

**期待**: 2 行目の出力に、スキルを**網羅的に列挙した**箇所が現れない。`skill-routing.md` に残るのは複合作業の連鎖と否定的境界の文脈で名前が出る行のみで、「これが全スキルの一覧である」と読める記述が存在しないこと。

## 5. SC-005 — 移設先に 100% 存在し、到達可能

```sh
test -f docs/live-documentation-standards.md && echo "退避先あり"
grep -c "ISO/IEC/IEEE\|PMBOK\|PRINCE2\|arc42\|Diátaxis\|Martraire\|Minto" docs/live-documentation-standards.md
grep -n "live-documentation-standards" .claude/rules/live-documentation.md
grep -n "29148\|INVEST\|MoSCoW\|BABOK" .claude/skills/clarifier/SKILL.md
```

**期待**:
- 退避先が存在する
- 移設した規格名がすべて退避先に存在する（移設前の References と突き合わせる）
- `live-documentation.md` から退避先へのリンクが 1 件以上ある
- `clarifier` SKILL.md に移設した References が存在する

**退避先が `.claude/rules/` 配下でないこと**（自動ロードされないこと）:

```sh
find .claude/rules -name "*.md" | wc -l   # → 7 のまま
```

## 6. SC-006 — 壊れた参照が 0 件

```sh
grep -rn "rules/mcp.md\|rules/clarifier.md\|rules/permissions.md\|rules/live-documentation\|live-documentation.md" \
  README.md README.ja.md install.sh docs/ 2>/dev/null | grep -v "^docs/adr/00"
```

出た各行について、[data-model.md](./data-model.md) E6 の表と突き合わせ、以下を確認する:

- カタログ表を参照していた `README.md` L174 / `README.ja.md` L138 が、`.mcp.json` など実在する正本を指すよう repoint されている
- `README.md` L98 のツリー注記から「lifecycle standards」が消え、退避先に言及している
- `README.md` L25 / `README.ja.md` L15 の `.claude/rules/` 説明が現状と一致する
- `clarifier` SKILL.md L57 付近が `rules/clarifier.md § References` を指していない

さらに、シップされる成果物が Spec Kit 中間成果物を指していないこと（`live-documentation.md` §6）:

```sh
grep -rn "specs/035" README.md README.ja.md install.sh .claude/ docs/ 2>/dev/null
```

**期待**: 0 件。

## 7. SC-007 — ADR-0006 無改変 + supersede の存在

```sh
git diff a884d6f..HEAD -- docs/adr/0006-remove-permissions-config.md | wc -l   # → 0
test -f docs/adr/0014-restore-credential-deny-rules.md && echo "ADR-0014 あり"
grep -n "0006" docs/adr/0014-restore-credential-deny-rules.md
```

**期待**:
- 0006 の差分が 0 行
- 0014 が存在し、0006 を参照している
- 0014 に [contracts/permissions-deny.md](./contracts/permissions-deny.md) 「受け入れる帰結」の 3 項目（Edit/Write も塞がる、`.env.example` も塞がる、全プロジェクトへ波及）が負の帰結として書かれている

---

## 8. 全体の回帰確認（任意だが推奨）

変更後に新しいセッションを開き、`/context` で **Memory files** に何が読み込まれているかを確認する。

**期待**: `.claude/rules/` の 7 ファイルと `.claude/CLAUDE.md` が現れる。`docs/live-documentation-standards.md` は**現れない**。`@import` を削除した後もルール 7 件がすべて読み込まれていること — これが FR-011 の「import は冗長だった」という前提の実証になる。ここで 1 件でも欠ければ前提が誤りなので、import を戻す。
