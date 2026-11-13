# 一括構築の試しの記録（AC-ROOT-1、AC-ROOT-4 の資料）

2026-11-14 に、`$TMPDIR/tree-dryrun` に作った Git リポジトリで、`harness/skills/sync-docs/SKILL.md` の「Build a documentation tree」の手順を、作業ツリーの版の skill で当てた記録。フィクスチャのファイルの写しは [dryrun-fixture/](dryrun-fixture/) にある（`.git` を除く。coupon は2つめの変更で足したもの）。記録のフォルダにはデータのファイルだけを置くので、写しの `.ts` のファイルは名前の後に `.txt` を付けて保存した（`cart.ts` は `cart.ts.txt`）。以下の出典の `cart.ts:1` などは、フィクスチャの中の元の名前で書いている。フィクスチャの `git log` と `git status` の出力は [dryrun-git.txt](dryrun-git.txt) にある（2つめの変更の README を書いた後に取った）。試しの後、AC-ROOT-4 の照合の指摘を受けて、SKILL.md の手順3の1文を「出典は、ファイルと行、またはコマンドとその出力」と直した。試しで使った skill との差はこの1文だけである。

## 手順と結果

1. フィクスチャ（コミット `4db85ed`）: 2つのプロダクト（`products/shop`、`products/admin`。ルートの `package.json` の workspaces が `products/*`）、それぞれに2つの機能フォルダ。README はルートにも無い。
2. Declare: 宣言なしで `check_tree.py` を実行すると、終了コード 0 で、候補 `products/*`（products）と `products/*/src/features/*`（features）を出した。手順は、人が候補を確かめてから設定を書く。このフィクスチャは試し用で利用者の確認を得る相手がいないため、実行した Claude が確かめた扱いにした（人の確認の代わりにはならない）。
3. 宣言を書いた後の `check_tree.py`: 終了コード 1、`missing-readme` が7件（ルート、2プロダクト、4機能フォルダ）。
4. Create / Fill: 節の種類ごとのひな形（`readme-repository.md`、`readme-product.md`、`readme-feature.md`）から7つの README を作った。書いた事実と出典は下の表のとおり。
5. Check: `check_tree.py` は終了コード 0（エラー 0 件、未記入の警告 7 件）、`check_links.py` は終了コード 0（7 ファイル、エラー 0 件）。`{{` と `replace:` の残りは 0 件。ルートの README から下向きのリンクだけをたどって、4つの機能フォルダの README すべてに着いた（`check_tree.linked_directories` で幅優先にたどった）。コミット `afe92d4`。
6. 2つめの変更: `products/shop/src/features/coupon/coupon.ts` を足した。`find_related.py` は候補なし（新しい節の README がまだ無いため）。`check_tree.py` は終了コード 1 で、`products/shop/README.md: no link to the child node products/shop/src/features/coupon` と `products/shop/src/features/coupon: no README.md in this feature folder` の2件。SKILL.md の Check の段に従い、機能フォルダのひな形から coupon の README を作り、`products/shop/README.md` の Features に1行足した。`check_tree.py` は終了コード 0（エラー 0 件、警告 8 件）、`check_links.py --changed` は終了コード 0。

## 作った README と、書いた事実の出典

| README | 書いた事実 | 出典 |
|---|---|---|
| `README.md` | 題名 acme-platform | `package.json:2` |
| `README.md` | ルートの `test` スクリプトは `vitest run` を実行する | `package.json:6` |
| `README.md` | 子の @acme/shop は Customer-facing web shop. | `products/shop/package.json:2-3` |
| `README.md` | 子の @acme/admin は Internal console for staff. | `products/admin/package.json:2-3` |
| `products/shop/README.md` | 題名 @acme/shop、目的 Customer-facing web shop. | `products/shop/package.json:2-3` |
| `products/shop/README.md` | build は `vite build`、test は `vitest run` | `products/shop/package.json:5-6` |
| `products/shop/README.md` | 子の cart は Keeps the items a customer intends to buy, in the browser session only. | `products/shop/src/features/cart/cart.ts:1` |
| `products/shop/README.md` | 子の checkout は Turns a cart into an order. | `products/shop/src/features/checkout/checkout.ts:1` |
| `products/shop/README.md` | 子の coupon は Applies a discount code to an order total.（2つめの変更） | `products/shop/src/features/coupon/coupon.ts:1` |
| `products/admin/README.md` | 題名 @acme/admin、目的 Internal console for staff. | `products/admin/package.json:2-3` |
| `products/admin/README.md` | build は `vite build`、test は `vitest run` | `products/admin/package.json:5-6` |
| `products/admin/README.md` | 子の audit-log は Records staff actions for later review. | `products/admin/src/features/audit-log/audit.ts:1` |
| `products/shop/src/features/cart/README.md` | 目的 Keeps the items a customer intends to buy, in the browser session only. | `cart.ts:1` |
| `products/shop/src/features/cart/README.md` | 守るべき条件「Adding an item keeps the items already in the cart」と、それを確かめるテスト | `cart.test.ts:2-3` |
| `products/shop/src/features/cart/README.md` | 最初に読むファイル cart.ts、照らし合わせたコミット 4db85ed | [dryrun-git.txt](dryrun-git.txt) の13行（cart.ts を含むコミット）と3行（4db85ed） |
| `products/shop/src/features/checkout/README.md` | 目的 Turns a cart into an order. | `checkout.ts:1` |
| `products/shop/src/features/checkout/README.md` | 扱わないこと: 支払い（外部の提供者が扱う） | `checkout.ts:1` |
| `products/shop/src/features/checkout/README.md` | 守るべき条件「空のカートは注文にならない」、テストなし | `checkout.ts:3`、フォルダにテストのファイルがない |
| `products/shop/src/features/checkout/README.md` | 最初に読むファイル checkout.ts、照らし合わせたコミット 4db85ed | [dryrun-git.txt](dryrun-git.txt) の14行と3行 |
| `products/admin/src/features/users/README.md` | 最初に読むファイル users.ts、照らし合わせたコミット 4db85ed | [dryrun-git.txt](dryrun-git.txt) の10行と3行 |
| `products/admin/src/features/audit-log/README.md` | 目的 Records staff actions for later review. | `audit.ts:1` |
| `products/admin/src/features/audit-log/README.md` | 守るべき条件「書いた記録は後から編集しない」、テストなし | `audit.ts:1`、フォルダにテストのファイルがない |
| `products/admin/src/features/audit-log/README.md` | 最初に読むファイル audit.ts、照らし合わせたコミット 4db85ed | [dryrun-git.txt](dryrun-git.txt) の9行と3行 |
| `products/shop/src/features/coupon/README.md` | 目的 Applies a discount code to an order total. | `coupon.ts:1` |
| `products/shop/src/features/coupon/README.md` | 守るべき条件「1つのコードは1回の注文で1度だけ使える」、テストなし、`applyCoupon` も確かめない | `coupon.ts:1-3` |
| `products/shop/src/features/coupon/README.md` | 最初に読むファイル coupon.ts、照らし合わせた版 afe92d4 と未コミットの coupon の変更 | [dryrun-git.txt](dryrun-git.txt) の2行（afe92d4）と17-19行（未コミットの変更は products/shop/README.md と coupon の2ファイルだけ） |

## 残った未記入の項目（`check_tree.py` の警告）

- `README.md`（3）: 目的、前提（ランタイムとパッケージマネージャの版）、その他の文書。
- `products/shop/README.md`（3）、`products/admin/README.md`（4）: ローカルでの起動方法、依存してよいもの・いけないものとその検査（2つ）。admin はさらに、子の users の1行の説明。
- `products/admin/src/features/users/README.md`（5）: 目的、扱わないこと、設計の理由、守るべき条件とその検査（2つ）。`users.ts` には目的を述べる記述がなく、関数名 `listUsers` から推し量って埋めることはしなかった。
- `products/shop/src/features/cart/README.md`（2）: 扱わないこと、設計の理由。
- `products/shop/src/features/checkout/README.md`（2）: 支払いの提供者とその連携の場所、設計の理由。
- `products/admin/src/features/audit-log/README.md`（2）: 扱わないこと、設計の理由。
- `products/shop/src/features/coupon/README.md`（2）: 扱わないこと、設計の理由。
