---
status: Accepted
date: 2026-11-17
deciders: Taiki Ogihara
---

# 0027. ~/.aws の SSO 設定とキャッシュだけをサンドボックスに開け、aws を中で動かす

## コンテキストと問題

[ADR-0020](0020-enable-sandbox-by-default.md) は、`~/.aws` をサンドボックスの中から読めないままにし、`aws` で始まる1つのコマンドだけを、権限の確認を経て外で動かすと決めた(`excludedCommands: ["aws *"]`)。そのときの用途は、`--profile` 付きの aws CLI だけだった。

利用者は、サンドボックスの中からも `~/.aws` に置いた SSO の設定で認証できるよう求めた(2026-11-17)。SSO は AWS IAM Identity Center のサインインを指す。中で認証したい対象は、boto3 などの SDK を使うスクリプト、CDK・SAM・Terraform、`aws sso login` である。ADR-0020 の設定では、これらは `~/.aws` を読めずに失敗する。`excludedCommands` はコマンドの文字列で一致を見るので、`python` や `npm run` から呼ばれる SDK には効かない。

公式ドキュメントで確かめたこと(2026-11-17。Claude Code の Sandboxing と Settings reference)は、次のとおりである。

- `sandbox.filesystem.allowRead` は、`denyRead` が閉じた範囲の中の特定のパスを開け直す。読み取りの規則が重なるときは、パスが狭いほうが効く。
- `permissions.deny` の `Read(...)` の規則は、サンドボックスの設定に統合される。
- `excludedCommands` に一致したコマンドは、ファイルの制限もネットワークのプロキシも受けずに動く。
- `sandbox.credentials` の `mask` は、環境変数の認証情報をプロキシが SigV4 で署名し直す。SSO のプロファイルとトークンのキャッシュについての記述は無い。`network.tlsTerminate`(実験的)が要る。

`allowRead` が、`Read(~/.aws/**)` と `Read(**/.aws/**)` から作られた拒否を開け直せるかは、公式ドキュメントに明記が無い。「狭いパスが効く」からの推論である。この変更は Linux のコンテナで作っており、macOS の実機では確かめていない。

## 決定

`harness/settings.json` の `sandbox` を、次のとおりに変える。ADR-0020 の表の `aws … --profile X` の行と、「検討した選択肢」の3つ目は、本 ADR が置き換える。ADR-0020 のほかの決定は変えない。

| 設定 | 値 | 根拠 |
|---|---|---|
| `filesystem.allowRead` | `~/.aws/config`、`~/.aws/sso/cache`、`~/.aws/cli/cache` | SSO のプロファイルは `config` に定義される。SDK と CLI は、SSO のアクセストークンを `sso/cache` から、CLI は一時的な認証情報を `cli/cache` から読む |
| `filesystem.allowWrite` | 上の2つのキャッシュを足す | トークンと一時的な認証情報の更新、`aws sso login` が書き込む |
| `filesystem.denyRead` | `~/.aws/credentials` を足す | 長期のアクセスキーを置くファイルである。`permissions.deny` からの統合に頼らず、サンドボックスの設定でも明示する |
| `excludedCommands` | `[]` | aws は中で動く。キーを消さずに空の配列にするのは、`install.sh` の統合(`jq '.[0] * .[1]'`)が配列を置き換えるためである。キーを消すと、利用者の `~/.claude/settings.json` に入っている `["aws *"]` が残る |
| `network.allowedDomains` | 変えない | AWS のホストは足さない。接続は権限モードが決める(利用者の決定) |

あわせて次も決める。

- `~/.aws/config` には書かせない。プロファイルの `credential_process` は、AWS のツールが実行するプログラムを指す。書けると、サンドボックスの外で動く AWS のツールにプログラムを実行させられる。
- `permissions.deny` は変えない。Claude のファイルツールは、`~/.aws` の下を読めないままである。
- SessionStart のフックが aws CLI のあるセッションで足す注意を、書き換える。伝えるのは、SSO のプロファイルなら中で認証できること、`~/.aws/credentials` は読めないこと、プロファイルを `--profile` か、そのコマンドの前の `AWS_PROFILE=名前` で毎回指定すること、SSO のセッションが切れたら `aws sso login --profile 名前 --use-device-code` を使うことである。
- `aws sso login` は `--use-device-code` で動かす。既定の方式は、ブラウザの起動と、ローカルのポートでの待ち受けが要る。デバイスコードの方式は、URL とコードを表示するだけで、利用者が自分のブラウザで開く。`sandbox.network.allowLocalBinding` を開けずに済む。

### 結果

- 良い点: SSO のプロファイルを使う aws CLI、SDK のスクリプト、CDK・SAM・Terraform が、サンドボックスの中で認証できる。パイプや `&&` でつないだ aws のコマンドも中で動く。
- 良い点: aws のコマンドが、ファイルとネットワークの制限を受けるようになる。ADR-0020 では、審査を通った aws のコマンドは外で全ファイルに届いた。
- 良い点: `~/.aws/credentials` の長期のアクセスキーは、中から読めないままである。
- 悪い点: サンドボックスの中のどのコマンドも、SSO のアクセストークンと、キャッシュされた一時的な認証情報を読める。SSO のアクセストークンは、利用者に割り当てられた全アカウントの一時的な認証情報を取れる。プロンプトインジェクションで実行されたコマンドも同じである。ADR-0020 が避けたリスクであり、利用者が受け入れた(2026-11-17)。持ち出しには、許可リストにないホストへの接続が要り、権限モードの判定を経る。
- 悪い点: 中のコマンドは、2つのキャッシュに書ける。キャッシュのファイルを書き換えて、別の認証情報で AWS のツールを動かせる。
- 悪い点: AWS を呼ぶたびに、接続先のホスト(`portal.sso.<region>.amazonaws.com`、`oidc.<region>.amazonaws.com`、各サービスの API)を権限モードが判定する。`*.amazonaws.com` を確認なしで開けると、任意の S3 バケットへの持ち出しの経路になるので、開けない。
- 悪い点: `~/.aws/credentials` の長期のアクセスキーを使うプロファイルは、中では失敗する。aws のコマンドは、権限の確認を経た外での再実行に回る。ADR-0020 では、最初から外で動いた。
- 悪い点: ADR-0020 は、Bedrock モードの Bash から `AWS_PROFILE` を外す。SDK のスクリプトと Terraform には、プロファイルをコマンドごとに渡す必要がある。
- 悪い点: CDK・SAM・Terraform が `~/.aws` の外に書く場所(`~/.cdk`、`~/.aws-sam`、`~/.terraform.d` など)は開けていない。そこに書く手順は、外での再実行に回る。[`team/package-safety/README.ja.md`](../../team/package-safety/README.ja.md) は、macOS のサンドボックスの中で `terraform` が TLS の検証に失敗すると記録している。
- 悪い点: `AWS_CONFIG_FILE` や `AWS_SHARED_CREDENTIALS_FILE` で場所を変えている場合、許可は及ばない。

## 検討した選択肢

- **SSO に要る部分だけを開ける(採用)**: 上記のとおり。
- **`~/.aws` 全体を開ける**: 設定は最も単純で、長期のアクセスキーのプロファイルも中で動く。代わりに、長期のアクセスキーが中のどのコマンドからも読め、`config` への書き込みで `credential_process` を差し込める。
- **ファイルは閉じたまま、プロキシで署名し直す(`sandbox.credentials` の `mask` と `network.tlsTerminate`)**: 中のコマンドには偽のキーだけが見え、SSO のトークンは露出しない。代わりに、`~/.aws` の SSO の設定を直接は使えない。Claude Code の起動の前に、一時的な認証情報を環境変数に書き出す必要があり、期限が切れると起動し直す。ストリーミングの送信と署名つきの URL は、既定で失敗する。`tlsTerminate` は実験的である。
- **閉じたまま、外で動かすコマンドを増やす(`cdk *`、`sam *`、`terraform *`)**: `~/.aws` は中から読めないままである。代わりに、それらのコマンドはファイルとネットワークの制限を一切受けない。スクリプトから呼ばれる SDK には効かない。
- **AWS のホストを許可リストに入れる(SSO の2系統だけ、または `*.amazonaws.com`)**: 判定の手間は減る。利用者は入れないことを選んだ。
- **`aws sso login` のために `allowLocalBinding` を開ける**: 既定のログインの方式が中で動く可能性がある。代わりに、中のどのコマンドもローカルのポートで待ち受けられる。デバイスコードの方式で足りるので採らない。

## 確認方法

- `tests/run-sandbox-settings.sh` は、次を検査する。SBX-03 は、読み取りを開け直す場所が上の3つとちょうど一致し、ホームディレクトリも `~/.aws` 全体も開けていないことを確かめる。SBX-04 は `~/.aws/credentials` が読めないこと、SBX-09 は書き込みを開ける場所、SBX-10 は名前で外に出すコマンドが無いこと、SBX-11 は AWS のホストを確認なしで開けていないことを確かめる。NOTE-06 と NOTE-07 は、フックの注意の文面を確かめる。
- Claude Code がこれらのキーに従うことは、`install.sh` の後の新しいセッションで、macOS の実機で手作業で確かめる。確かめる項目は次の5つである。
  1. サンドボックスの中で `aws sts get-caller-identity --profile <SSO のプロファイル>` が、ホストの確認を経て成功する。
  2. サンドボックスの中で `cat ~/.aws/credentials` が失敗する。
  3. サンドボックスの中で `~/.aws/config` への追記が失敗する。
  4. サンドボックスの中で、boto3 のスクリプトが `AWS_PROFILE=<SSO のプロファイル>` で認証できる。
  5. サンドボックスの中で `aws sso login --profile <SSO のプロファイル> --use-device-code` が URL とコードを表示し、承認の後に `~/.aws/sso/cache` を更新する。
- 1 が `~/.aws/config` を読めずに失敗するなら、`allowRead` は `permissions.deny` から作られた拒否を開け直せない。その場合は、この決定を見直す。

## 補足情報

- [ADR-0020](0020-enable-sandbox-by-default.md) — サンドボックスを既定で有効にした決定。本 ADR は、その aws の扱いだけを置き換える。
- [ADR-0014](0014-restore-credential-deny-rules.md) — ファイルツールに対する資格情報の読み取り拒否。変更しない。
- Claude Code — Sandboxing: <https://code.claude.com/docs/en/sandboxing>、Settings reference: <https://code.claude.com/docs/en/settings-reference>
- AWS CLI — IAM Identity Center の概念(トークンのキャッシュ): <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso-concepts.html>
