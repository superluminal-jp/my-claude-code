---
status: Accepted
date: 2026-11-10
deciders: Taiki Ogihara
---

# 0022. Spec Kit のプロジェクトファイル（`.specify/`）を追跡せず、各チェックアウトのローカルに置く

## コンテキストと問題

[ADR-0001](0001-remove-vendored-speckit-skills.md) は、`speckit-*` のスキルを追跡から外し、`specify init` がプロジェクトごとに作るものとした。そのとき `.specify/` は、このリポジトリ自身の Spec Kit の導入として、追跡したまま残した（46ファイル）。

2026-11-10 に、無視されたファイルの掃除で消した `speckit-*` を、README の「Opt-in to spec-kit」の手順（`specify init --here --force --integration claude`）で作り直した。そのとき入っていた `specify` は 1.2.5 で、`.specify/` の記録は 1.1.0 だった。作り直しは、追跡している `.specify/` の8つのファイルも 1.2.5 の内容に書き換えた。

- 書き換わったもの: 版の記録、git 拡張のスキルの登録、`.specify/.gitignore`、2つのスクリプト、2つの manifest
- 書き換わらなかったもの: テンプレート、`memory/constitution.md`、`extensions.yml`

`.specify/` を追跡していると、各自が最新版で `specify init` を実行するたびに作業ツリーが変わる。その変更をリモートに上げるかどうかの判断も、そのたびに要る。46ファイルのうち42は spec-kit の生成物で、scripts と templates は spec-kit が記録したハッシュと一致していた（手を入れていない）。残る4つのうち3つ（`extensions.yml` の、`before_specify` で clarifier を呼ぶフック、`extensions/git/git-config.yml` の、すべての手順の前後で自動コミットする設定、`workflows/overlays/speckit/full-pipeline.yml` の、流れを組み替えて push と PR まで進める重ね書き）は、このリポジトリで決めた内容だった。`memory/constitution.md` は、穴埋めの残った spec-kit のテンプレートのままだった。

利用者は 2026-11-10 に、「speckitはリモートにはあげない。使う人がローカルで最新版を使うように」と方針を示し、`.specify/` の扱いを尋ねた質問に「`.specify` をすべて外す」と答えた。

## 決定

- `.gitignore` に `.specify/` を入れ、46ファイルすべてを追跡から外す（`git rm -r --cached`）。各チェックアウトの `.specify/` は、そのチェックアウトの利用者が `specify init` で最新版を作るものとする。Spec Kit の何もリモートには上げない。
- このリポジトリで決めていた3つと `constitution.md` も、各自のローカルのものになる。新しいクローンには `.specify/` が無く、`specify init` と `specify extension add git` が spec-kit の既定で作る。
- `tests/run-install.sh` の確かめは、`git-config.yml` のチェックサムから、`.specify/` 全体に変える。`.specify/` が在るとき（作業中のチェックアウト）は `install.sh` がそれに触れないこと、無いとき（CI のチェックアウト）は作らないことを確かめる。`install.sh` が `.specify/` を名指さないことも確かめる。
- ADR-0001 の「`.specify/` は追跡したまま残す」の部分を、この ADR で置き換える。`speckit-*` のスキルを追跡しないことは、ADR-0001 のまま変えない。

## 検討した選択肢

- **追跡はそのままにし、手元だけ最新版にする**: 作業ツリーの変更が残り続け、後の作業で誤ってコミットしうる。`specify init` のたびに同じことが起きる。
- **この4つだけを追跡し、生成物を外す**: フックのつなぎ方や自動コミットの設定はリポジトリで共有できる。ただし `specify init` や `specify extension add git` がそれらを書き換えたとき、また同じ判断が要る。利用者は、すべてを外すほうを選んだ。
- **追跡したまま 1.2.5 に上げる PR を出す**（PR #128）: 方針（リモートに上げない）に反するので閉じた。

## 確認方法

- `git ls-files .specify` が何も出さない。`git check-ignore .specify/memory/constitution.md` が無視を示す。
- `bash tests/run-install.sh` が、`.specify/` が在るチェックアウトと無い CI のチェックアウトの両方で合格する。`install.sh` に `.specify/` に書く行を足すと、確かめが落ちる（2026-11-10 に確かめた）。

## 補足情報

- [ADR-0001](0001-remove-vendored-speckit-skills.md) — `speckit-*` のスキルを追跡から外した決定。この ADR はその `.specify/` の部分を置き換える。
- [ADR-0008](0008-restore-speckit-specify-update-check-hook.md) — `speckit-specify` の前に `specify-cli` の版を確かめるフック。各自の CLI を最新に保つ仕組みで、この決定と矛盾しない。
- `specs/001`〜`070` は追跡したまま残す。そこにある `.specify/` への言及は、それぞれの時点の記録である。
