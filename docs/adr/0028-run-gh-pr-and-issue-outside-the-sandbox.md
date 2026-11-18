---
status: Accepted
date: 2026-11-18
deciders: Taiki Ogihara
---

# 0028. gh の pr・issue・repo view だけをサンドボックスの外で動かし、hosts.yml は閉じたままにする

## コンテキストと問題

[ADR-0020](0020-enable-sandbox-by-default.md) は、`~/.config/gh/hosts.yml` をサンドボックスの中から読めなくした。GitHub CLI(`gh`)は、このファイルに保存されたトークンで認証する。そのため、サンドボックスの中の `gh` は認証できず、PR や issue の操作が失敗する。

利用者は、`hosts.yml` の `denyRead` を残したまま、`gh` を `excludedCommands` で外に出すよう求めた(2026-11-18)。検討の結果、パターンは `gh *` ではなく、使うサブコマンドに絞ると決めた(2026-11-18、推奨案の採用)。

公式ドキュメントで確かめたこと(2026-11-18。Claude Code の Sandboxing、Settings reference、Permissions)は、次のとおりである。

- `excludedCommands` に一致したコマンドは、ファイルの制限もネットワークのプロキシも受けずに動く。`denyRead` は、そのコマンドには適用されない。したがって、外で動く `gh` だけが `hosts.yml` を読める。`denyRead` は、ほかのすべてのサンドボックス内コマンドに対して効き続ける。
- 除外されたコマンドも、通常の権限の流れを通る。`permissions.ask` と `permissions.deny` は効く。
- 一致は、コマンドの文字列で見る。`excludedCommands` は、一致しないコマンドをサンドボックスの中に残す。`cd`、コマンド置換、サブシェル、ヒアドキュメント、リダイレクト、`sudo`・`eval`・`xargs` 始まり、変数から来るコマンド名を含む呼び出しは、パターンに一致しても中に残る。
- ドキュメントは、広いパターンを避け、狭いパターンを使うよう警告している。権限ルールは、セキュリティ境界ではない。

公式ドキュメントに記載がなく、未確認のもの: パイプ(`gh … | cat`)と環境変数の前置(`FOO=1 gh …`)が除外の対象になるか。`gh pr *` が実機で一致するか(確認は Manual モードで行う)。

## 決定

`harness/settings.json` を、次のとおりに変える。`denyRead` の `~/.config/gh/hosts.yml` は変えない。

| 設定 | 値 | 根拠 |
|---|---|---|
| `sandbox.excludedCommands` | `["gh pr *", "gh issue *", "gh repo view *"]` | 利用者の用途は PR・issue の閲覧と操作に限られる。ほかの `gh` のサブコマンドは、中に残る |
| `sandbox.filesystem.denyRead` | 変えない | `hosts.yml` は、外に出した `gh` 以外から読めないままである |

`gh auth`(トークンの表示)、`gh api`、`gh gist`(任意のファイルの送信)、`gh extension`、`gh alias` は、除外に含めない。これらは中で動くので、`hosts.yml` を読めず、認証に失敗する。deny ルールは足さない。除外の範囲を狭めたことで、これらは外に出ないためである。

`permissions.ask` は足さない。[ADR-0006](0006-remove-permissions-config.md) と [ADR-0014](0014-restore-credential-deny-rules.md) は、`permissions` を `deny` だけにし、`allow` と `ask` を置かないと決めており、`tests/run-removed-guardrails.sh` がそれを検査する。外で動く `gh pr` と `gh issue` は、`defaultMode` が `auto` のため、分類器が審査する(公式ドキュメント: auto モードでは、分類器が除外されたコマンドを審査する)。利用者の選択(2026-11-18)。

`gh -R owner/repo pr …` のように、サブコマンドの前にフラグを置く呼び出しは `gh pr *` に一致せず、中に残って失敗する。安全側に倒れる。

### 結果

- 良い点: `gh pr` と `gh issue` が、トークンを読めるままで動く。ほかのコマンドは、`hosts.yml` を読めないままである。
- 良い点: 外に出るコマンドは3つのサブコマンドに限られる。
- 悪い点: 外で動く `gh pr` と `gh issue` は、ファイルの制限を受けない。`--body-file` に任意のパスを渡すと、そのファイルの内容を GitHub に送れる。確認が必ず出る保証はなく、分類器の審査に頼る。
- 悪い点: `gh pr create --body "$(cat <<EOF …)"` のようなコマンド置換やヒアドキュメント、`cd dir && gh pr …`、リダイレクトを含む呼び出しは、外に出ず、認証に失敗する。`--body-file` を使い、作業ディレクトリで `gh` を単独の命令として実行する。
- 悪い点: `gh -R`・`gh --repo` を前に置く呼び出しは、中で失敗する。リポジトリは、作業ディレクトリで決める。
- 悪い点: `gh pr checkout` は、リポジトリの git フックを外で動かす。審査は、コマンドの文字列しか見ない。
- 悪い点: 実機での一致は未確認である。Manual モードで状態を変えるコマンドを実行し、確認画面の題が「Bash command (unsandboxed)」になることで確かめる。

## 検討した選択肢

- **`gh pr *`・`gh issue *`・`gh repo view *` だけを除外する(採用)**: 上記のとおり。
- **GitHub を変更する操作に `permissions.ask` を足す**: 実行の前に確認が必ず出る。代わりに、ADR-0006 と ADR-0014 の決定を変える必要があり、`tests/run-removed-guardrails.sh` の期待値も変わる。利用者は見送った(2026-11-18)。
- **`gh *` を除外する**: 設定は最も単純。代わりに、`gh auth token` によるトークンの表示、`gh gist create` による任意のファイルの送信、`gh extension` による第三者のコードの実行、`gh api` による任意の API 呼び出しが、外で動く。deny ルールで個別に塞ぐ必要があり、権限ルールは境界ではない。
- **`hosts.yml` を `allowRead` で開ける**: `gh` は中で動き、パイプやコマンド置換も使える。代わりに、トークンが中のすべてのコマンドから読める。ADR-0020 が避けたリスクである。
- **`GH_TOKEN` に絞った fine-grained トークンを渡す**: 権限と期限を絞れ、`hosts.yml` は閉じたままにできる。代わりに、トークンが中のすべてのコマンドから読める。トークンの作成と保管の手間もある。利用者は、外での実行を選んだ。
