---
status: Accepted
date: 2026-11-08
deciders: Taiki Ogihara
---

# 0020. OS サンドボックスを既定で有効にし、日常作業に要る出口だけを開ける

## コンテキストと問題

[ADR-0014](0014-restore-credential-deny-rules.md) は、資格情報の読み取り拒否を `permissions.deny` で強制すると決めた。ただし、それが効くのは Claude のファイルツールと、Claude Code が見分けられる Bash のファイルコマンドだけである。Python や Node のスクリプトが自分で開くファイルには効かない。ADR-0014 は OS のサンドボックスを「範囲外で、別の決定に値する」として採らなかった。本 ADR がその決定である。

利用者は、セキュリティリスクの入る余地を最小限にし、サンドボックスを既定で有効にするよう求めた(2026-11-07)。あわせて、次の日常作業がサンドボックスの中でも動くことを求めた。Chromium の使用、Noto Sans のインストール、署名つきの git commit、`--profile` 付きの aws CLI の4つである。Bedrock 用のアカウント(`settings.json` の `env.AWS_PROFILE`)は、Claude Code が Bash で行う作業には使わないことも求めた。

2026-11-07 にこのマシン(macOS、Claude Code 2.1.319)で観察したことは、次のとおりである。

- サンドボックスの中で Chromium は、起動の時点で `bootstrap_check_in … MachPortRendezvousServer … Permission denied (1100)` で止まる。Seatbelt の規則は `(deny default)` で始まり、Mach サービスの登録(`mach-register`)を許す設定が無い。`--single-process` を付けると、同じサンドボックスの中で起動し、ページを描いた。
- `permissions.deny` の `Read(~/.aws/**)` は、サンドボックスの読み取りの拒否にもなる。書き込みの許可は作業ディレクトリと一時ディレクトリだけで、`~/.gnupg` と `~/Library/Fonts` を含まない。
- サンドボックスの中のコマンドは、許可していない Unix ソケットに接続できない。そのため gpg は gpg-agent にも、keyboxd にも届かない。
- `settings.json` の `env` は、Bash、フック、stdio の MCP サーバーのすべてに届く。Bash にだけ別の値を渡す設定キーは無い。
- 過去90日の会話記録では、Bash ツールが zsh で動くことによる誤りが繰り返されていた(一致しないグロブ342件、`=` で始まる語 約180件、引用符の無い変数の単語分割 約40件)。

## 決定

`.claude/settings.json` で、Bash のサンドボックスを既定で有効にする。厳しさは標準とする。中で動かないコマンドは、権限の確認(auto モードの判定か、利用者への確認)を経て外で再実行でき、許可リストにないホストは権限モードで決まる。そのうえで、次だけを開ける。

| 作業 | 決定 | 根拠 |
|---|---|---|
| 署名つきの git commit | `~/.gnupg` への書き込みと、`S.gpg-agent`・`S.keyboxd` のソケットへの接続を許す。秘密鍵・旧形式の秘密鍵束・失効証明書は読ませない。それらとキーリング・`trustdb.gpg`・gpg/gpgsm/gpg-agent/dirmngr/scdaemon/keyboxd の設定・`sshcontrol`・`trustlist.txt`・scdaemon がカードの状態の変化で実行する `scd-event` には書かせない(設定と `scd-event` は、サンドボックスの外の GnuPG のプロセスにプログラムを実行させられるため)。gpg-agent は SessionStart のフックでサンドボックスの外で起動する | 利用者の決定(2026-11-08)。外で `git commit` を動かすと、リポジトリの git フックも外で動く。読み取り専用のキーリングと信頼度のデータベースでも署名できることを、一時的な GNUPGHOME で確かめた |
| `aws … --profile X` | `excludedCommands: ["aws *"]` で、aws で始まる1つのコマンドだけを、権限の確認を経て外で動かす。`~/.aws` はサンドボックスの中から読めないままにする | 利用者の決定(2026-11-08)。SSO のアクセストークンは、割り当てられた全アカウントの一時的な認証情報を取れる。中で開けると、審査を経ないどのコマンドからも読める |
| Chromium | このリポジトリのスライドの検査器は、macOS のサンドボックスの中(`SANDBOX_RUNTIME=1`)では `--single-process` を付ける。ほかの起動のために、macOS ではこのことを文脈で Claude に伝える | 上の観察 |
| Noto Sans | `~/Library/Fonts` への書き込みと、`fonts.googleapis.com`・`fonts.gstatic.com` への確認なしの接続を許す | Google Fonts の CSS API は、curl に TTF を返す(2026-11-08)。`raw.githubusercontent.com` は任意の公開リポジトリの内容を返すので外した |

あわせて次も決める。

- `~/.git-credentials`、`~/.netrc`、`~/.config/gh/hosts.yml`、`~/.docker/config.json`、`~/.kube/config` を、サンドボックスの中から読めないようにする。`~/.npmrc` は、npm がコマンドのたびに読むので含めない。
- Bedrock モード(`CLAUDE_CODE_USE_BEDROCK` が真)では、SessionStart のフックが `CLAUDE_ENV_FILE` に `unset` の行を書く。Bash のコマンドは、AWS の8つの変数(`AWS_PROFILE`、`AWS_DEFAULT_PROFILE`、`AWS_REGION`、`AWS_DEFAULT_REGION`、`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`、`AWS_BEARER_TOKEN_BEDROCK`)を引き継がない。作業用のプロファイルは、利用者が `--profile` で毎回指定する。
- SessionStart のフックが、条件に当たるセッションにだけ、短い注意を文脈に足す。Bash ツールが zsh のとき(`CLAUDE_CODE_SHELL`、なければ `SHELL`)は zsh の3つの落とし穴、macOS のときは Chromium の `--single-process`、aws CLI があるときは aws の書き方(1つのコマンドで、`--profile` を付ける)である。常時ロードのルールは4ファイルのまま(ADR-0015)にし、新しいルールは作らない。

フックは3つとも `settings.json` に直接書いた短いコマンドであり、`.claude/hooks/` は作らない。ADR-0005 の方針を保ち、ADR-0008 の前例に倣う。

### 結果

- 良い点: プロンプトインジェクションで実行されたコマンドも、`~/.aws`、`~/.ssh`、列挙した資格情報のファイル、GPG の秘密をファイルとして読めない。作業ディレクトリと一時ディレクトリの外、`~/.gnupg`(守る項目を除く)、`~/Library/Fonts` 以外には書けない。確認なしに届くホストは Google Fonts の2つだけになる。
- 良い点: 利用者が名指しした4つの作業は、中で済むか、審査を経た1つのコマンドとしてだけ外に出る。
- 悪い点: gpg-agent がパスフレーズを覚えている間は、サンドボックスの中のどのコマンドも、ソケットを通じて利用者の鍵で署名できる。パスフレーズの無い鍵なら書き出しもできる。利用者が受け入れた(2026-11-08)。
- 悪い点: `~/Library/Fonts` に置いたフォントは、サンドボックスの外の macOS のフォントの仕組みが読む。悪意あるフォントのファイルを置かれると、フォントの解析の脆弱性を突かれる経路になる。Noto Sans のインストールのために受け入れた。
- 悪い点: `aws` をパイプや `&&` でつなぐと外に出ず、`~/.aws` を読めずに失敗する。審査を通った aws のコマンドは、外で全ファイルに届く。
- 悪い点: Bedrock モードでも、`env` の AWS の変数はフックと stdio の MCP サーバーに届く。残す `deploy-on-aws` の `awsiac` と `awspricing` は、Bedrock 用のアカウントで AWS の API を呼ぶ。Bedrock の認証情報を `env.AWS_PROFILE` ではなく `awsCredentialExport` で渡せば、どの子プロセスにも届かない(利用者の各マシンでの設定であり、このリポジトリは書かない)。
- 悪い点: プロジェクトとローカルの設定は、このサンドボックスを緩められる。止められるのは管理設定か `--settings` だけである。
- 悪い点: サンドボックスの中の Chromium は、平文の HTTP は読めたが、プロキシ経由の HTTPS は時間切れになった。macOS の `mktemp` は、テンプレートが無いと `$TMPDIR` を使わずに失敗し、`/usr/bin/diff` は `<(...)` の `/dev/fd` を開けない。これらのコマンドは外での再実行に回る。`tests/run-install.sh` の `diff <(...)` は、文字列の比較に替えた。
- 悪い点: スライドの検査器は、サンドボックスを `SANDBOX_RUNTIME=1` で見分ける。これは観察した振る舞いであり、公式ドキュメントに記述は無い。変われば、Chromium は以前のように起動の時点で失敗する。
- 悪い点: `GNUPGHOME` を `~/.gnupg` 以外にしている場合、許可は及ばない。keyboxd を使う GnuPG では、公開鍵の取り込みはサンドボックスの外の keyboxd を通るので止まらない。
- 悪い点: `install.sh` の `jq '.[0] * .[1]'` は配列を置き換える。そのため、利用者が `~/.claude/settings.json` に書いた `sandbox` のパスの一覧と `hooks.SessionStart` は、インストールのたびにこのリポジトリの値になる。

## 検討した選択肢

- **標準の厳しさで有効にし、必要な出口だけ開ける(採用)**: 上記のとおり。
- **厳格(`allowUnsandboxedCommands: false`、`strictAllowlist: true`、`failIfUnavailable: true`)**: 外での再実行と、許可リストの外への確認を一切なくす。`gh`、SSH での `git push`、`brew`、`playwright install` が、個別に除外しない限り動かない。利用者が標準を選んだ。
- **aws をサンドボックスの中で動かし、`~/.aws/config` と SSO・CLI のキャッシュを開け直す**: aws の外での実行は不要になる。代わりに、SSO のトークンが審査を経ないすべてのコマンドから読める。`allowRead` が `permissions.deny` から作られた拒否を開け直せるかも未検証だった。利用者が外での実行を選んだ。
- **`git commit` を `excludedCommands` で外に出し、`~/.gnupg` は閉じる**: 署名の残余のリスクは無くなる。代わりに、リポジトリの git フックがサンドボックスの外で動き、審査ではコマンドの文字列しか見えない。利用者が中での署名を選んだ。
- **Bash ツールを bash に替える(`CLAUDE_CODE_SHELL=/bin/bash`)**: zsh 固有の誤りは無くなる。代わりに macOS の bash 3.2 の制約を負い、`~/.zshrc` の関数やエイリアスが使えなくなる。利用者は「指示として zsh を使うことを伝える」を選んだ。
- **Chromium に `sandbox.network.allowMachLookup` を使う**: この設定が作るのは `mach-lookup` の規則だけで、Chromium が止まる `bootstrap_check_in`(`mach-register`)は許さないため、効かない。
- **作業用のプロファイルを `WORK_AWS_PROFILE` で Bash に渡す**: 一度は設計した。利用者の用途は `--profile` を毎回付けることなので外した(2026-11-08)。

## 確認方法

- `tests/run-sandbox-settings.sh` は、次の3つを検査する。1つ目は `sandbox` のキーで、守る場所、開ける場所、ソケット、ホスト、外で動かすコマンドがレビュー済みの一覧と一致することを確かめる。2つ目は、3つのフックを sh・bash・zsh で実行したときの振る舞いである。3つ目は MCP のキー(ADR-0021)である。
- `tests/assert_deck_units.py` の UNIT-08〜11 は、検査器の Chromium の引数を確かめる。UNIT-08 は、サンドボックスの中で実際に Chromium を起動する。
- `tests/run-install.sh` は、リポジトリの `sandbox` と `github` プラグインの停止が利用者の値に勝ち、利用者のほかのキーが残ることを確かめる。
- Claude Code がこれらのキーに従うことは、`install.sh` の後の新しいセッションで手作業で確かめる([spec 067](../../specs/067-sandbox-by-default/spec.md) の SC-002〜SC-005)。署名つきのコミットは、GPG の鍵を持つマシンで確かめる。

## 補足情報

- [ADR-0014](0014-restore-credential-deny-rules.md) — OS のサンドボックスを範囲外とした決定。本 ADR がその後を受ける。ADR-0014 は変更しない。
- [ADR-0005](0005-remove-claude-hooks.md)、[ADR-0008](0008-restore-speckit-specify-update-check-hook.md) — hooks を最小限にする方針と、`settings.json` に直接書く前例。
- [ADR-0021](0021-block-mcp-servers-by-settings.md) — 同じ変更で止めた MCP サーバー。
- [spec 067](../../specs/067-sandbox-by-default/spec.md) — 要件、利用者の決定、反証のレビューとその処理(`challenge-report.json`)。
- Claude Code — Sandboxing: <https://code.claude.com/docs/en/sandboxing>、Settings reference: <https://code.claude.com/docs/en/settings-reference>、Environment variables: <https://code.claude.com/docs/en/env-vars>
- AWS CLI — IAM Identity Center の概念(トークンのキャッシュ): <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso-concepts.html>
