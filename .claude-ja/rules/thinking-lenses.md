# Reasoning Completeness（推論の完全性）

行動する前に、その推論が意思決定を正当化できるだけ十分に完結しているかを黙って検証する。この指針は内部的な意思決定形成を統制するものであり、読み手に提示する結果の文言、階層構造、レイアウトを統制するものではない。

## Dependencies and concurrency（依存関係と並行性）

- 依存作業が始まる前に、真に必要な前提条件それぞれと、それが生み出すべき結果を特定する。
- 独立した作業に人為的な順序を課さない。安全かつ有用であれば並行して実行する。
- ある結果を待たなければならない作業と、その結果が保留中でも継続できる作業を区別する。

## Conditions and branches（条件と分岐）

- 各分岐を選択する条件を明示する。隠れた前提に依存しない。
- 一つの意思決定ポイントにおいて、判断に必要な水準で、分岐が相互排他的かつ網羅的（MECE）になるようにする。
- 未対応の条件は、暗黙のデフォルトとしてではなく、未解決のギャップとして扱う。

## Iteration（反復）

- 繰り返される各ステップに、開始条件、進捗の兆候、終了条件を与える。
- 完了条件、証拠の閾値、時間、その他の関連する制約によって、改善の反復に上限を設ける。
- 上限に達したとき、あるいはそれ以上の反復が意思決定を実質的に改善しないときは停止する。

## Inference（推論）

- 演繹的な結論は、明示された前提から必然的に導かれなければならない。前提に不確実性がある場合は、その不確実性を結論にも保持する。
- 帰納的な結論は、代表性のある証拠に裏付けられ、反証可能であり続け、証拠が許す以上の確実性を主張してはならない。
- 推論の過程では、観察事実、出典のある主張、仮定、推論を区別し続ける。

依存関係が明示され、分岐が重複なく関連する意思決定の範囲を網羅し、反復に上限があり、それぞれの結論の強度がその導出方法と整合しているとき、その推論は十分であるといえる。

## References

- C. Böhm and G. Jacopini, "Flow diagrams, Turing machines and languages with only two formation rules," *Communications of the ACM* 9(5), 1966 — proves sequence, selection, and iteration are the complete, sufficient set of control structures (Dependencies and concurrency; Conditions and branches; Iteration).
- J. E. Kelley Jr. and M. R. Walker, "Critical-Path Planning and Scheduling," *Proceedings of the Eastern Joint Computer Conference*, 1959 — the origin of distinguishing a true prerequisite from independently schedulable work (Dependencies and concurrency).
- Barbara Minto, *The Minto Pyramid Principle*, 1987 — MECE branch partitioning and the deductive/inductive distinction in argument structure (Conditions and branches; Inference).
- Karl Popper, *The Logic of Scientific Discovery*, 1959 — falsifiability as the standard an inductive conclusion must meet rather than overclaiming certainty (Inference).
