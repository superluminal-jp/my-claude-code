# Feature Specification: OS サンドボックスを既定で有効にし、日常作業に要る出口だけを最小限に開ける

**Feature Branch**: `feat/sandbox-by-default`

**Created**: 2026-11-07

**Status**: Draft

**Input**: User description: "chromium の使用, noto sans のインストールがサンドボックス内でもできるように。github mcpの設定は削除. セキュリティリスクや脆弱性が入る余地を最小限に設定できるように。他のMCPも合わせて棚卸し。デフォルトでサンドボックスを有効化するようにする。新しいブランチとワークツリーで作業。macのシェルはzshなので、bashとの違いによってエラーが出ることが多いのを修正したい。aws profile でbedrockのclaudeモデルを使用する際に使用するaws profileを作業用のprofile。~/.claude/settings.jsonのenvにAWS_PROFILEで指定しているプロファイルはbedrockを使うためだけのアカウント。claudecodeで作業をするアカウントにはその扱いを使わない。git コマンドが ~/.gnupg に、 aws cli, boto3が ~/.aws にアクセスできなかった。"(2026-11-07)。用途の補足: "用途としてはaws cliのコマンドにprofileをつけて実行したいのと、git commitに署名をつけたいだけ。"(2026-11-08)

**要旨**: ユーザー設定(`install.sh` が `~/.claude/settings.json` に入れるもの)で、Bash のコマンドを OS のサンドボックス(macOS では Seatbelt)の中で動かすことを既定にする。サンドボックスは、Claude が実行するシェルのコマンドが読み書きできるファイルと、接続できるホストを OS の機能で制限する仕組みである。そのうえで、利用者の日常作業に要る出口だけを開ける。Chromium の起動、Noto Sans のインストール、git の GPG 署名はサンドボックスの中で済ませる。`--profile` 付きの aws CLI だけは、権限の確認を経てサンドボックスの外で動かし、`~/.aws` はサンドボックスから閉じたままにする。Bedrock 用の AWS の変数は Bash に渡さない。Bash が zsh で動くときには、zsh で失敗しやすい書き方を Claude に伝える。GitHub MCP と、利用者が選んだ MCP を止める。

**利用者の決定と、Claude が決めた既定**:

| # | 論点 | 根拠 | 決めた事項 |
|---|---|---|---|
| D1 | サンドボックスの厳しさ | 利用者の決定(標準。Claude の推奨) | 既定で有効にする。サンドボックスの中で動かせないコマンドは、権限の確認(auto モードの判定か、利用者への確認)を経て外で再実行できる。許可リストにないホストへの接続は、権限モードに従って決まる |
| D2 | Chromium | 観察: サンドボックスの中で Chromium は起動の時点で `bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer.<pid>: Permission denied (1100)` で止まる。Claude Code 2.1.319 のサンドボックスの規則には、Mach サービスの登録(`mach-register`)を許す設定がない。`--single-process` を付けると、同じサンドボックスの中で起動し、ページを描き、Noto Sans JP で文字を描いた | Chromium を1プロセスで動かす。このリポジトリのスライドの検査器は、macOS のサンドボックスの中では自動で `--single-process` を付ける。ほかのプロジェクトのために、macOS ではこのことを Claude に伝える |
| D3 | Noto Sans のインストール | 観察: Google Fonts の CSS API は、curl に対して `fonts.gstatic.com` の TTF を返した(2026-11-08)。Claude の既定 | `~/Library/Fonts` への書き込みを許す。確認なしで許すホストは `fonts.googleapis.com` と `fonts.gstatic.com` の2つだけにする |
| D4 | git の署名 | 利用者の決定(2026-11-08。Claude の推奨。サンドボックスの外で git を動かすと、リポジトリの git フックも外で動くことを説明した後) | サンドボックスの中で署名する。`~/.gnupg` を書けるようにし、gpg-agent と keyboxd のソケットへの接続を許し、gpg-agent はセッションの開始時にサンドボックスの外で起動する。秘密鍵の場所・旧形式の秘密鍵束・失効証明書は読めないように、それらとキーリング・信頼度のデータベース・gpg・gpgsm・gpg-agent の設定ファイルは書けないようにする。残るリスク(gpg-agent がパスフレーズを覚えている間は、サンドボックスの中のどのコマンドも黙って署名できる)を利用者は受け入れた |
| D5 | aws CLI | 利用者の決定(2026-11-08。Claude の推奨)。用途は `--profile` 付きの aws CLI だけ | `aws` で始まる1つのコマンドだけを、権限の確認を経てサンドボックスの外で動かす。`~/.aws` はサンドボックスの中から読めないままにする(SSO のトークンを、審査を経ないコマンドに見せない)。Claude には、プロファイルを `--profile` で必ず指定するよう伝える |
| D6 | Bedrock 用の AWS の変数 | 利用者の要求 | Claude Code が Bedrock を使うセッションでは、Bash のコマンドは AWS の8つの変数(`AWS_PROFILE`、`AWS_DEFAULT_PROFILE`、`AWS_REGION`、`AWS_DEFAULT_REGION`、`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`、`AWS_BEARER_TOKEN_BEDROCK`)を引き継がない。作業用のプロファイルは `--profile` で指定するので、作業用のプロファイルを環境変数で渡す仕組みは作らない |
| D7 | zsh | 利用者の決定(「指示として zsh を使うことを伝える」) | シェルは zsh のままにし、Bash ツールが zsh で動くときだけ、zsh であることと、失敗しやすい書き方を Claude に伝える。常時ロードのルールは4ファイルと決まっているので(ADR-0015)、伝える手段はセッションの開始時に文脈を足すフックにする(Claude の既定) |
| D8 | 止める MCP | 利用者の決定 | GitHub MCP、`bedrock-agentcore`、claude.ai のコネクタすべて、claude.ai から同期されるプラグインを止める。ほかの MCP(aws-knowledge、aws-documentation、strands-agents、google-developer-knowledge、microsoft-learn、wolfram、deploy-on-aws)は残す |
| D9 | このマシンへの適用 | Claude の既定(マシン全体の状態を変えるため) | このリポジトリの変更だけを行う。`install.sh` の実行とプラグインのアンインストールは、利用者の承認を得てから行う |
| D10 | ほかの資格情報のファイル | 反証のレビュー CH-04 への Claude の既定。利用者の用途(aws CLI と git の署名)に影響しない | `~/.git-credentials`、`~/.netrc`、`~/.config/gh/hosts.yml`、`~/.docker/config.json`、`~/.kube/config` をサンドボックスから読めないようにする。`~/.npmrc` は npm がコマンドのたびに読むので含めない |

**Authority**: 本仕様が正である。ADR-0014 が「範囲外」とした OS のサンドボックスを、ここで採用する。ADR-0005 と ADR-0008 の、hooks を最小限にする方針は守る(フックは `settings.json` に直接書いた短いコマンドだけで、`.claude/hooks/` は作らない)。

## 用語

- **サンドボックス**: Claude Code が Bash のコマンドごとにかける OS の制限。読めるファイル、書けるファイル、接続できるホストとソケットを決める。Claude の Read・Edit ツール、MCP サーバー、フックはこの外で動く。
- **サンドボックスの外での実行**: サンドボックスをかけずにコマンドを動かすこと。この設定では、`aws` で始まる1つのコマンドと、サンドボックスの中で失敗して再実行されるコマンドがこれに当たり、どちらも権限の確認を経る。
- **Bedrock モード**: Claude Code が Amazon Bedrock 経由で Claude を呼ぶ設定(`CLAUDE_CODE_USE_BEDROCK` が真)のセッション。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - サンドボックスが既定で効き、資格情報と設定は守られる (Priority: P1)

利用者が `install.sh` を実行すると、どのプロジェクトでも Bash のコマンドがサンドボックスの中で動く。プロンプトインジェクションで実行されたコマンドも、`~/.aws`、GPG の秘密鍵と失効証明書、ほかの資格情報のファイルを読めず、GPG のキーリング・信頼度のデータベース・設定ファイルに書けない。

**Why this priority**: 利用者が求めた「セキュリティリスクや脆弱性が入る余地を最小限に」の中心であり、ほかの話はすべてこの上に成り立つ。

**Independent Test**: リポジトリの `settings.json` を検査するテストで確かめられる。

**Acceptance Scenarios**:

1. **Given** リポジトリの `.claude/settings.json`、**Then** サンドボックスは有効で、厳しさは標準(サンドボックス外への再実行を禁じず、許可リストの外を一律には拒まない)である。
2. **Given** 同じ設定、**Then** `~/.aws` の下も、ホームディレクトリ全体も、読み直しや書き込みのために開けていない。
3. **Given** 同じ設定、**Then** `~/.gnupg/private-keys-v1.d`、`~/.gnupg/secring.gpg`、`~/.gnupg/openpgp-revocs.d`、`~/.git-credentials`、`~/.netrc`、`~/.config/gh/hosts.yml`、`~/.docker/config.json`、`~/.kube/config` はサンドボックスから読めない。
4. **Given** 同じ設定、**Then** GPG の秘密鍵の場所、旧形式の秘密鍵束、失効証明書、キーリング(`pubring.kbx`、`pubring.gpg`、`public-keys.d`)、信頼度のデータベース(`trustdb.gpg`)、gpg・gpgsm・gpg-agent・dirmngr・scdaemon・keyboxd の設定ファイル、`sshcontrol`、`trustlist.txt`、scdaemon が実行する `scd-event` には書けない。
5. **Given** 同じ設定、**Then** すべての Unix ソケットへの接続は許さない。許すソケットは gpg-agent と keyboxd の2つだけである。
6. **Given** 確認なしで許すホストの一覧、**Then** Google Fonts の2つのホストだけである。

### User Story 2 - サンドボックスの中で Chromium が動き、Noto Sans を入れられる (Priority: P1)

利用者がスライドの検査や画面の確認を頼むと、Claude はサンドボックスの外に出ずに Chromium を起動する。Noto Sans を入れるときは、Google Fonts から TTF を取得し、`~/Library/Fonts` に置ける。

**Why this priority**: 利用者が名指しした作業であり、サンドボックスを既定にすると、これまで動いていたスライドの検査が止まる。

**Independent Test**: 検査器の起動引数を決める関数の単体テストと、macOS のサンドボックスの中での実際の起動で確かめる。

**Acceptance Scenarios**:

1. **Given** macOS でサンドボックスの中、**When** スライドの検査器が Chromium を起動する、**Then** `--single-process` を付ける。
2. **Given** サンドボックスの外、または macOS 以外、**Then** 検査器は Chromium の引数を足さない。
3. **Given** macOS でのセッションの開始、**Then** Claude に「サンドボックスの中の Chromium には `--single-process` が要る」ことが伝わる。macOS 以外では伝えない。
4. **Given** サンドボックスの設定、**Then** `~/Library/Fonts` に書け、`fonts.googleapis.com` と `fonts.gstatic.com` に確認なしで接続できる。

### User Story 3 - git の署名がサンドボックスの中で動き、aws CLI は審査を経て外で動く (Priority: P1)

利用者の報告どおり、git は `~/.gnupg` を、aws CLI は `~/.aws` を使えなかった。変更の後は、署名つきのコミットがサンドボックスの中で作れ、`--profile` 付きの aws CLI のコマンドは権限の確認を経てサンドボックスの外で動く。

**Why this priority**: 利用者が報告した失敗であり、用途として名指しした2つの作業である。

**Independent Test**: 設定の検査と、セッションの開始時に gpg-agent を起動するフックのテスト(gpg の代わりのスタブを使う)で確かめる。

**Acceptance Scenarios**:

1. **Given** サンドボックスの設定、**Then** `~/.gnupg` に書け(User Story 1 の4を除く)、gpg-agent と keyboxd のソケットに接続できる。
2. **Given** `gpgconf` があり `~/.gnupg` が存在するマシンでのセッションの開始、**Then** フックは gpg-agent をサンドボックスの外で起動する。どちらかが無ければ、何もしない。
3. **Given** サンドボックスの設定、**Then** サンドボックスの外で動かすコマンドの一覧は `aws *` だけである。
4. **Given** aws CLI があるマシンでのセッションの開始、**Then** Claude に、aws を1つのコマンドとして実行すること(パイプや `&&` でつながない)と、`--profile` を必ず付けることが伝わる。

### User Story 4 - Bash は Bedrock 用のアカウントを使わない (Priority: P1)

利用者は Bedrock のためだけのアカウントを `AWS_PROFILE` に設定する。Claude が Bash で `--profile` を付け忘れても、そのアカウントで AWS を操作しない。

**Why this priority**: 誤ったアカウントでの操作は、取り消しにくい変更や課金につながる。

**Independent Test**: セッションの開始時のフックに環境変数を与えて実行し、Bash に渡す内容を確かめる。

**Acceptance Scenarios**:

1. **Given** Bedrock モード、**Then** Bash のコマンドには、D6 の8つの変数がない。
2. **Given** Bedrock モードでない、**Then** Bash の環境は何も変えない。

### User Story 5 - Bash が zsh のとき、zsh で失敗しやすい書き方が Claude に伝わる (Priority: P2)

過去 90 日の会話記録では、zsh 固有のエラーのほとんどが3種類だった。一致しないグロブ(`no matches found`、342件)、`=` で始まる語の展開(`===== not found` など、約180件)、引用符のない変数が単語分割されないこと(約40件)である。

**Why this priority**: 頻度は高いが、失敗しても Claude が書き直せば済む。

**Independent Test**: セッションの開始時のフックに、シェルの環境変数を与えて実行する。

**Acceptance Scenarios**:

1. **Given** Bash ツールのシェルが zsh(`CLAUDE_CODE_SHELL`、なければ `SHELL` が zsh)、**Then** 文脈に、Bash ツールが zsh で動くことと、上の3種類を避ける書き方が入る。
2. **Given** シェルが bash、**Then** その文脈は入らない。

### User Story 6 - 止めると決めた MCP がつながらない (Priority: P1)

**Acceptance Scenarios**:

1. **Given** 設定、**Then** GitHub がホストする MCP サーバー(`https://api.githubcopilot.com/`)は、どこで定義されていても読み込まれず、`github` プラグインは無効である。
2. **Given** 設定、**Then** `bedrock-agentcore` は読み込まれない。
3. **Given** 設定、**Then** claude.ai のコネクタは読み込まれず、claude.ai からプラグインを同期しない。
4. **Given** `install.sh` を、利用者が自分で入れたプラグインの設定や `env` を持つ `~/.claude/settings.json` に対して実行する、**Then** それらは残り、上の設定だけが加わる。

### Edge Cases

- `~/.gnupg` が無いマシン: gpg-agent は起動せず、ほかの設定は害なく残る。
- `GNUPGHOME` を `~/.gnupg` 以外にしているマシン: サンドボックスの許可が及ばないので、署名は外での再実行に回る(制限として文書に書く)。
- aws をパイプや `&&` でつないだコマンド: サンドボックスの外に出ず、`~/.aws` を読めずに失敗する。Claude には、aws を1つのコマンドで実行するよう伝える。
- フックが bash 以外(zsh や sh)で実行される: フックのコマンドは sh、bash、zsh のどれでも同じに動く。
- Chromium が HTTPS のページをサンドボックスのプロキシ経由で読む: 2026-11-07 の観察では時間切れになった(平文の HTTP は読めた)。この変更では直さず、制限として記録する。
- keyboxd を使う GnuPG: 公開鍵の取り込みは、サンドボックスの外の keyboxd が行うので、`public-keys.d` への書き込みの禁止では止まらない。信頼度は `trustdb.gpg` にあり、書けない。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: ユーザー設定は、Bash のサンドボックスを既定で有効にしなければならない(MUST)。厳しさは D1 のとおり標準とする。
- **FR-002**: サンドボックスは、`~/.aws` の下と、User Story 1 の3のファイルを読ませてはならない(MUST NOT)。
- **FR-003**: サンドボックスは、User Story 1 の4のファイルとディレクトリに書かせてはならない(MUST NOT)。
- **FR-004**: サンドボックスは、`~/.gnupg`(FR-003 を除く)と `~/Library/Fonts` への書き込みを許さなければならない(MUST)。
- **FR-005**: サンドボックスは、gpg-agent と keyboxd のソケットへの接続だけを許さなければならない(MUST)。すべてのソケットを開けてはならない。
- **FR-006**: 確認なしで許すホストは、`fonts.googleapis.com` と `fonts.gstatic.com` に限らなければならない(MUST)。
- **FR-007**: スライドの検査器は、macOS のサンドボックスの中でだけ、Chromium に `--single-process` を付けなければならない(MUST)。
- **FR-008**: セッションの開始時に、Bedrock モードでは、Bash の環境から D6 の8つの変数を外さなければならない(MUST)。Bedrock モードでなければ、何も変えてはならない。
- **FR-009**: セッションの開始時に、`gpgconf` と `~/.gnupg` があれば、gpg-agent をサンドボックスの外で起動しなければならない(MUST)。
- **FR-010**: セッションの開始時に、Bash ツールのシェルが zsh なら zsh の注意を、macOS なら Chromium の注意を、aws CLI があれば aws の注意を、Claude の文脈に足さなければならない(MUST)。どれにも当たらなければ、何も足してはならない。
- **FR-011**: 設定は、GitHub がホストする MCP サーバー、`bedrock-agentcore`、claude.ai のコネクタ、claude.ai からのプラグインの同期を止めなければならない(MUST)。
- **FR-012**: `install.sh` は、利用者が自分で書いた `settings.json` のキー(`env`、ほかのプラグインの有効・無効など)を残さなければならない(MUST)。
- **FR-013**: README(英日)、`docs/mcp-servers.md`、`docs/claude-config-design.md`、ADR は、上の振る舞いと、受け入れた制限を記述しなければならない(MUST)。
- **FR-014**: サンドボックスの外で動かすコマンドの一覧は、`aws *` だけでなければならない(MUST)。

### Key Entities

- **サンドボックスの設定**: 書ける場所、読ませない場所、書かせない場所、接続できるソケット、確認なしで接続できるホスト、外で動かすコマンド。
- **セッション開始のフック**: Bash の環境から Bedrock の変数を外すもの、gpg-agent を起動するもの、文脈を足すものの3つ。いずれもサンドボックスの外で動く。
- **止める MCP の一覧**: URL、名前、コマンドのどれかで MCP サーバーを特定する。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: リポジトリのテストがすべて通り、新しい設定の検査は FR-001〜FR-012 と FR-014 の各項目を、少なくとも1つずつ確かめる。
- **SC-002**: 変更の前にサンドボックスの中で失敗した Chromium の起動が、変更の後はサンドボックスの外に出ずに成功する。
- **SC-003**: Bedrock モードの新しいセッションで、Bash から見える `AWS_PROFILE` は未設定であり、`aws … --profile X` は権限の確認を経てサンドボックスの外で動く。
- **SC-004**: 新しいセッションで、止めると決めた MCP サーバー(GitHub、`bedrock-agentcore`、claude.ai のコネクタ7件、同期プラグイン2件)のツールが1つも現れない。
- **SC-005**: GPG の鍵を持つマシンの新しいセッションで、サンドボックスの中から署名つきのコミットを作れる(このマシンには `~/.gnupg` が無いので、利用者のマシンで確かめる)。

## Assumptions

- 利用者は macOS で Claude Code 2.1.319 以降を使う。設定のキーとその意味は、2026-11-07 に読んだ公式ドキュメント(code.claude.com の sandboxing、settings-reference、env-vars、hooks、mcp、plugins)に従う。
- サンドボックスの中のコマンドに環境変数 `SANDBOX_RUNTIME=1` が渡ることは、2026-11-07 の観察による(公式ドキュメントに記述は見当たらない)。変わったら、検査器は引数を足さなくなり、Chromium は以前のように起動の時点で失敗する。
- `CLAUDE_ENV_FILE` に書いた行が、サンドボックスの中と外のコマンドに効くかは、公式ドキュメントに記述がない。SC-003 で、変更を適用した新しいセッションで確かめる。
- AWS の API のホスト(`*.amazonaws.com`)は許可リストに入れない。aws CLI はサンドボックスの外で動くので要らず、S3 のように書き込みを受け付けるため、確認なしで開けると持ち出しの経路になる。
- `settings.json` の `env` の値は、Bash だけでなくフックと stdio の MCP サーバーにも届く。Bedrock モードでは、残す MCP サーバーのうち AWS の API を呼ぶもの(deploy-on-aws の awsiac と awspricing)は Bedrock 用のアカウントで動く。利用者の用途(aws CLI と git の署名)の外なので、この変更では扱わず、制限として記録する。
