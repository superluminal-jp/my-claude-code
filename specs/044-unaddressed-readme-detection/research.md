# Research: 未処分の兄弟 README の検出(S1)

未解決の NEEDS CLARIFICATION は無い。計画の判断点を、決定・根拠・代替案の形で記録する。

## R1. 「同じディレクトリの文書」の判定

- **Decision**: 候補の文書は、拡張子が文書の拡張子(`.md`、`.mdx`、`.markdown`、`.rst`、`.adoc`、`.asciidoc`)で、`is_changelog` に該当せず、`classify` に `decision` を含まないファイル。再帰はせず、元ファイルと同じディレクトリだけを対象にする。
- **Rationale**: 仕様は「README 系文書と Markdown 文書」を候補とする。`classify` の `documentation` は `LICENSE` や `CONTRIBUTING` など拡張子のない名前も文書として扱うため、ルート直下のあらゆる変更の候補に出てしまい、ノイズが大きい。変更履歴は S2 の範囲なので除く。決定記録は受理済みの不変性を持つ別の扱いのため候補にしない。
- **Alternatives considered**: `classify` に `documentation` を含むものすべて(ノイズ過多)。`README*` のみ(仕様の「Markdown 文書」を満たさない)。

## R2. 候補の元になるファイル一覧

- **Decision**: `common.list_files(root, config)` が返すファイル(`.gitignore` と除外設定を尊重)を、ディレクトリごとに分けて使う。
- **Rationale**: 既存の関数で除外の規則が一貫し、`common.py` の変更が不要(仮定 A3)。ファイルシステムの再帰走査より速く、`.gitignore` の扱いも既存と同じ。
- **Alternatives considered**: ディレクトリを直接走査(除外規則を重複させることになる)。

## R3. 「処分済み」の判定(C2 の最小形)

- **Decision**: 候補のパスが、作業ツリーの変更集合に含まれるか、最終メッセージに(ルート相対の POSIX パスの部分文字列として)現れるなら処分済み。ファイル名だけの言及は受け付けない。
- **Rationale**: 複数の README が同名なので、名前だけでは区別できない。パスの部分文字列は決定的で、テストしやすい。形式的な言及でも通るという限界(仮定 A2)は、G3・G4 で固定し、構造化された処分行の要求は B2 が偽になった場合に回す。
- **Alternatives considered**: 構造化された処分行(`Disposition:` など)を必須にする(スキルの報告書式を変える必要があり、S4 の範囲と衝突する)。

## R4. C1 の `source` と、同じ文書が複数の変更ファイルの候補になる場合

- **Decision**: 候補のレコードは「元ファイルと候補の組」ごとに 1 件(`source` は文字列)で、C1 の形を守る。ゲートは候補の `path` で重複を除いて 1 つの問題として扱う。
- **Rationale**: 契約 C1 を変えずに、複数の元ファイルを表現できる。仕様のエッジケースの記述(1 つの候補にまとめる)は、この決定に合わせて仕様側を更新する(spec の Edge Cases)。
- **Alternatives considered**: `source` を配列にする(C1 の変更になるため、上流の meta-spec の更新が必要)。

## R5. 変更されたファイルの種別による絞り込み

- **Decision**: 文書でない変更ファイルすべてを元として扱う(生成物、ロックファイル、設定を含む)。
- **Rationale**: 仕様 FR-001 に従う最小の挙動。ノイズの影響は仮定 A1 として S2 で実測し、必要なら絞り込みを仕様変更として扱う。
- **Alternatives considered**: 生成物・ロックファイルを除外する(判断としては妥当だが、仕様の範囲を広げる。実測前に決めない)。

## R6. `hooks/rule.md` の変更

- **Decision**: 本スライスでは変更しない。
- **Rationale**: 既存の整合検査 `test_rule_and_gate_agree_with_skill` は、スキル名と `Documentation impact` の一致のみを要求する。処分の規則の追記は S4 の範囲。

## R7. A3(`common.py` を変更せずに再利用できる)の事前確認

- **Decision**: 読解した範囲では成立する見込み。実装中に必要が生じたら B3 として停止する。
- **Rationale**: `Change(path, status, old_path)`、`changed_files`、`list_files`、`classify`、`excluded`、`is_changelog` で、必要な情報(変更集合、除外済みの一覧、分類)がそろう。
