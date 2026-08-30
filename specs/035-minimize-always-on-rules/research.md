# Phase 0 リサーチ: 常時ロードルールの最小化と強制力の復元

**日付**: 2026-08-30 | **仕様**: [spec.md](./spec.md) | **計画**: [plan.md](./plan.md)

出典は Claude Code 公式ドキュメント（<https://code.claude.com/docs/en/memory>、<https://code.claude.com/docs/en/permissions>）と、本セッションでの直接観測。推測は「推測」と明記する。

---

## D1. `permissions.deny` のパターン形式とアンカー

**決定**: `Read(...)` 形式・gitignore 構文を使う。ホーム配下は `~/` 形式、プロジェクト配下はベアファイル名または `**/` 形式。**単一先頭スラッシュの `/path` 形式は使わない。**

**根拠**: 公式ドキュメントは 4 つのパターン型を定義し、`/path` は「設定ソース基準」でアンカーされると明記する。解決先は設定ファイルの置き場所で変わる:

| 定義場所 | `/path` の解決先 |
|---|---|
| プロジェクト設定 `.claude/settings.json` | `<主作業ディレクトリ>/path` |
| ユーザ設定 `~/.claude/settings.json` | `~/.claude/path` |

本リポジトリの `.claude/settings.json` は**プロジェクト設定であると同時に、`install.sh` によって `~/.claude/settings.json` としても配置される**。したがって `/path` 形式を書くと、同一のファイルが配置先によって別の意味を持つ。公式ドキュメントもこの落とし穴を名指しする — 「ユーザ設定の `Read(/secrets/**)` は `~/.claude/secrets/**` を塞ぐのであって、プロジェクト内の `secrets` ディレクトリではない。全プロジェクトに効かせたいなら `//` 絶対パスか `~/` ホーム相対を使え」。

一方、以下は両スコープで一貫して解決される:
- ベアファイル名: `Read(.env)` は `Read(**/.env)` と等価で、「カレントディレクトリ配下の任意の深さの `.env`」にマッチし、親ディレクトリや別プロジェクトの `.env` にはマッチしない。
- `~/` 形式: 常にホームディレクトリ基準。
- deny 規則の単一セグメントディレクトリ: `Read(secrets/**)` は deny では「任意の深さの `secrets` ディレクトリ」にマッチする（allow 規則とは挙動が異なる）。

**却下した代替案**:
- `/path` 形式 — 二重解決により本リポジトリでは危険。
- `//**/.env`（ファイルシステム全体） — 全ドライブを走査対象にする過剰な適用範囲。ユーザの他プロジェクトやバックアップにまで及ぶ。

---

## D2. ファイル名の部分一致はグロブ化しない

**決定**: 現行方針の「ファイル名に `secret` / `credential` / `token` / `key` を含むもの」は `permissions.deny` へ機械変換せず、`permissions.md` に方針文として残す。

**根拠**: 素朴な変換 `Read(**/*key*)` は `.claude/keybindings.json`、`monkey.ts`、`keyboard-shortcuts.md` といった無関係なファイルに一致する。決定的なのは、公式ドキュメントが **deny 規則は allow による例外を持てない**と明記していることである — 「`Bash(aws *)` のような広い deny は、より狭い allow `Bash(aws s3 ls)` に一致する呼び出しも含めてすべてブロックする。deny 規則は allowlist 例外を持てない」。つまり過剰阻害が判明しても、後から例外で緩和できず、パターン自体を削るしかない。安全側の設計は「狭く正確に書く」である。

**却下した代替案**:
- 個別列挙（`Read(**/id_rsa)`, `Read(**/*.key)` …） — 網羅不能であり、網羅したという誤った安心を与える。`.pem` / `.p12` / `.pfx` のような拡張子が確定しているものだけ拡張子で捕捉する。
- `ask` 規則にする — 毎回のプロンプトは実質的に無視されるようになり、保護として機能しない（警告疲れ）。

---

## D3. `Read` deny は `Edit` / `Write` も塞ぐ

**事実**: 公式ドキュメント明記 — 「`Read` deny 規則は同一パスに対する Edit / Write ツールも塞ぐ。新規ファイル作成を含む」（編集は v2.1.208 以降、書き込みは v2.1.228 以降）。`NotebookEdit` は対象外。

**帰結（ADR-0014 に負の帰結として記録すべき）**: 本変更後、Claude は `.env` を**読めなくなるだけでなく、作成・編集もできなくなる**。`.env.example` からの雛形生成のような正当な作業が阻害される。これは意図した副作用であり、隠してはならない。

**決定**: `Edit` deny は別途追加しない。`Read` deny がすでに Edit / Write を覆っており、追加で得られるのは `NotebookEdit` の被覆のみだが、対象パス（`.env`、秘密鍵、`.ssh/`）に Jupyter ノートブックが存在する現実的な場面がない。不要な規則は最小権限の観点でも足さない。

---

## D4. 強制の到達範囲 — どこまで塞げるか

**事実**: 公式ドキュメントの警告 — 「Read / Edit deny 規則は、組み込みファイルツールと、Claude Code が Bash 内で認識するファイルコマンド（`cat`、`head`、`tail`、`sed` など）に適用される。**ファイルを間接的に開く任意のサブプロセス（Python や Node のスクリプトなど）には適用されない。** 全プロセスを対象とする OS レベルの強制が必要ならサンドボックスを有効化せよ」。

補足事実: `ls`、`cat`、`head`、`grep` などは組み込みの読み取り専用コマンドとして全モードでプロンプトなしに実行されるが、deny 規則は**それでも適用される**。

**決定**: `permissions.md` はこの限界を明示する。「設定で塞がれる範囲」と「自己適用に頼る範囲」の境界を書かないことは、ADR-0006 が生んだ「方針だけあって強制がない」状態を、逆向きに繰り返すことになる（強制があると誤認させる）。Core Principle #1 の要求として、境界を書く。

**却下した代替案**: サンドボックス有効化 — 本仕様のスコープ外。ADR-0005 / 0007 の簡素化方針に対する大きな方向転換であり、別の決定として扱うべき。

---

## D5. 退避先を `docs/live-documentation-standards.md` とする

**決定**: `.claude/rules/live-documentation.md` から外す §0 標準規格表・§7.2/§7.3 の論拠・References は `docs/live-documentation-standards.md` に置く。

**根拠**: `.claude/rules/` 配下は**全 `.md` が再帰的に自動ロードされる**（公式明記: 「すべての `.md` ファイルが再帰的に発見されるので、`frontend/` や `backend/` のようなサブディレクトリに整理できる」）。したがって同ディレクトリ内のどこに置いても削減効果はゼロになる。これは選好ではなく技術的制約である。`docs/` は `docs/adr/`・`docs/claude-code-config-tips.md`・`docs/minto-*.ja.md` によりリポジトリの散文置き場として確立済み。

**却下した代替案**:
- 新規スキル `live-documentation` — スキルの `description` と `when_to_use` は常時コンテキストに注入されるため固定費が新たに増える。また参照資料（規格の一覧、参考文献）はモデルが自発的に読みに行く性質のものではなく、人間が確認するためのものである。スキルの想定用途と合わない。
- `.claude/rules/` 配下のサブディレクトリ — 自動ロードされるため無意味。
- 削除 — Core Principle #3 Traceability 違反。

---

## D6. スキル列挙を廃止する

**決定**: `.claude/CLAUDE.md` と `.claude/rules/skill-routing.md` から個々のスキルの列挙を削除する。追記による整合ではなく、列挙自体をやめる。

**根拠（直接観測）**: 本セッションのコンテキストには、ハーネスによって全スキルの `name`・`description`・`when_to_use` が自動注入されている。列挙はこの情報の重複である。さらにドリフトは仮説ではなく実測された — `.claude/skills/` に speckit 以外のスキルが 10 個あるのに対し、`CLAUDE.md` と `skill-routing.md` は 7 個しか挙げておらず、`adr` / `apple-notes` / `apple-reminders` が欠落している。二重管理は「保守を怠った」結果ではなく、二重管理という構造の必然的な帰結である。

**残すもの**: description からは導けない情報のみ — 複合作業の連鎖規則（コード変更 + 既存文書更新 → `coder` の次に `minto-rewriter`）、`scrum-master` の否定的境界（一般的なプロジェクト管理は対象外）、および同点時の優先規則（成果物と動作が明示された簡潔な依頼は `clarifier` ではなく `minto-builder`）。

---

## D7. References の移設先は 2 つに分岐する

**決定**:
- `live-documentation.md` の References → `docs/live-documentation-standards.md`
- `clarifier.md` の References → `.claude/skills/clarifier/SKILL.md`（同スキルの既存 References セクションへ統合）

**根拠**: `clarifier` の SKILL.md は現に `rules/clarifier.md § References` を名指しで参照している（SKILL.md 57 行目: 「Shared standards (ISO/IEC/IEEE 29148:2018, INVEST, SMART, Gherkin, MoSCoW, BABOK): full citations at `rules/clarifier.md` § References」）。ルール側から References を単純に削除すると、この参照が宙に浮く — §1 Drift の典型例である。したがって削除ではなく移設し、SKILL.md 側の文言も同一変更内で更新する。移設先としてスキルが適切なのは、これらの規格が実際に使われるのは formal elicitation を行うとき、すなわちスキルがロードされているときだけだからである。

---

## D8. 公式の "Exclude sensitive files" 例は取得できなかった

**事実**: `permissions` ドキュメントは資格情報除外の「paste-ready example」が `settings-reference#exclude-sensitive-files` にあると述べているが、`settings-reference` ページは長大で、2 回の取得試行がいずれも本文途中で打ち切られ、当該セクションに到達できなかった。

**決定**: 公式例をそのまま引き写すのではなく、`permissions` ドキュメントに明記された**構文仕様そのもの**（D1〜D4）からパターンを導出する。導出結果は [contracts/permissions-deny.md](./contracts/permissions-deny.md) に、1 行ごとの根拠つきで記載する。

**未解決として残す**: 公式例が本文書の導出と異なる可能性は排除できない。実装時または後日、当該セクションを直接参照できたら突き合わせる。これは「確認できていない」であって「確認した結果一致した」ではない。

---

## D9. `paths:` フロントマターは導入しない

**決定**: 今回は 7 ルールのいずれにも `paths:` を付けない。

**根拠**: `paths:` はファイル種別・ディレクトリで発火する仕組みであり、公式ドキュメントも「Claude がパターンに一致するファイルを**読んだとき**に発火し、あらゆるツール使用時ではない」と明記する。対象 7 ルールはいずれもファイルではなく**話題**で発火する（AWS の質問、コミットの作成、曖昧な依頼）。パススコープは適合しない。

**却下した代替案**: `live-documentation.md` を `**/*.md` にスコープする — ドキュメント強制はコード変更時にこそ効く必要があり、`.md` を読んだときだけ効くのでは §1 Drift の目的を達成できない。むしろ有害。

**将来の選択肢としては残る**: 言語固有のコーディング規約など、ファイル種別で発火するルールを今後追加する場合には第一候補となる。

---

## D10. ADR 番号と supersede の形式

**決定**: 新規 ADR は `docs/adr/0014-restore-credential-deny-rules.md`。既存の最大番号は 0013（`0013-eventkit-for-reminders-automation.md`）。

**形式**: ADR-0006 は Accepted のまま**一切改変しない**。0014 が 0006 の「Considered options」で一度却下された選択肢 —「資格情報の deny 項目のみ残し、allow / ask を落とす」— を採用する形になることを明記する。0006 自身がこの選択肢を検討済みで却下していた事実は、0014 の Context に不可欠である（なぜ当時却下され、いま何が変わったのか）。

**変わったこと**: (a) 公式ドキュメントが設定＝強制層／CLAUDE.md＝非強制層の区別を明示するようになった、(b) `Read` deny の被覆範囲が Edit / Write にも拡張された（v2.1.208 / v2.1.228）、(c) 本セッションの計測で、方針文が 3,754 バイトの常時コストを払いながら強制力ゼロという費用対効果の悪さが定量化された。

**相互参照**: 0014 は 0006 を参照し、0006 は不変のまま。ADR ディレクトリの索引としては 0014 側から遡れれば十分（0006 への追記は不変性違反）。
