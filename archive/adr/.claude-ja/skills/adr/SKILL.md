---
name: adr
description: "アーキテクチャ上重要で、後戻りが難しく、合理的な代替案が却下された意思決定を、コンテキスト・決定・結果・代替案を含む不変のArchitecture Decision Recordとして記録する。ユーザーが明示的にその操作を要求した場合にのみ、記録の作成または置き換えを行うこと。認可なしに該当する決定が生まれた場合は、記録を提案して待機すること。可逆的・局所的・自明・日常的な実装上の選択には使用しないこと。他の能力が独立して合致する場合は、それを継続したまま、重大な決定が確定した時点に記録または提案を配置すること。"
---

# Skill: adr

目的: Architecture Decision Record（ADR）を作成・維持すること。ADRは、機能の日々の*何を・なぜ*とは区別される、決定のコンテキスト・選択・結果・却下された代替案を記録する。テンプレートはNygardの原型をMADR 4.0.0のオプションセクションで拡張したものに従い、根拠となる内容はISO/IEC/IEEE 42010:2022に従う（[References](#references)を参照）。

## いつ記録するか

**すべて**が該当する場合に記録する: アーキテクチャ上重要である（構造、横断的関心事、または外部契約に影響する）、後戻りが難しい（一方通行のドアである）、そして合理的な代替案が却下された、の3つである。可逆的・局所的・自明・通常の実装上の選択はスキップする。必要であれば近接した場所での説明で十分である。

記録の作成または変更には、その操作についてのユーザーの明示的な要求が必要である。根底にある決定を実装せよという一般的な要求だけでは、十分な認可とはならない。あるセッションでフレームワーク、データストア、境界づけられたコンテキストの境界、API/プロトコル、認可モデル、ビルド/デプロイのトポロジーといった該当する選択が明示的な記録要求なしに確定した場合は、記録を提案して待機すること。決して黙って作成してはならない。

この手続きは、他の能力が独立して合致する場合でも引き続き適用される。その作業を継続しつつ、決定を覆すコストが高くなる前に提案を配置するか、決定と却下された代替案が確定した時点で認可された記録を作成すること。

## 手順

1. **権限と重要性の確認** — ユーザーが明示的に作成または置き換えを要求したこと、および決定が上記の全基準を満たすことを確認する。作成権限がない場合は、提案のみを行う。決定が十分に重要でない場合は、有用であれば近接した説明を推奨し、そこで終了する。
2. **次の番号を見つける** — `docs/adr/` をスキャンして最大の `NNNN` を見つけ、`NNNN+1` を4桁ゼロ埋めで使用する。以前のADRが却下または置き換えられた場合であっても、**番号を再利用しないこと**。`docs/adr/` が存在しない場合は作成する。単独の根拠記録は生成された契約文書ではない。
3. 下記のテンプレートから**起草する**。必須のコアを埋め、オプションのMADRセクションは決定の複雑さがそれを正当化する場合にのみ追加する（大きすぎるADRは読まれない — Nygard）。Consequences（結果）は具体的に書くこと — 利点だけでなく、否定的なトレードオフも明示する。関連する場合は、品質特性への影響（ISO/IEC/IEEE 42010）を記す。
4. **どう確認されるかを記す** — 該当する場合は、決定への準拠がどのように検証されるか（テスト、レビューゲート、フィットネス関数、またはlintルール）を*Confirmation*に記録する。
5. **Statusを設定する** — ユーザーが承認するまでは `Proposed` とし、承認後は `Accepted` とする。決定が代替案なしに無関係になった場合は `Deprecated` を使用する。後のADRがそれを置き換える場合は `Superseded by NNNN` を使用する。Acceptedとなった記録の内容は決して編集せず、置き換えられた/非推奨となった記録は**保持し**、削除しないこと。
6. **相互リンクする** — *More information* の下に、仕様、issue、関連するADRへの参照を記載する。

## テンプレート

必須コア = Title、Status、Date、Context and problem statement、Decision、Consequences。残りのセクションはMADR 4.0.0のオプションであり、決定が自明でない場合にのみ含める。

```markdown
---
status: Proposed | Accepted | Deprecated | Superseded by NNNN
date: YYYY-MM-DD
deciders: <who made the decision>
consulted: <SMEs consulted — optional>
informed: <kept informed — optional>
---

# NNNN. <Decision title: a short noun phrase>

## Context and problem statement

<The forces at play — technical, political, social, project-local — and the
problem that forces a decision now. Tie it to the stakeholder concerns or
quality attributes affected.>

## Decision drivers <!-- optional -->

- <driver / criterion 1>
- <driver / criterion 2>

## Considered options <!-- optional -->

- <Option A>
- <Option B>
- <Option C>

## Decision outcome

We will <Option A>, because <justification tied to the drivers>.

### Consequences

- Positive: <what becomes easier>
- Negative: <what becomes harder; trade-offs accepted>

## Confirmation <!-- optional -->

<How compliance with this decision will be verified: a test, review gate,
fitness function, or lint rule.>

## Pros and cons of the options <!-- optional -->

### <Option A>

- Good: <…>
- Bad: <…>

### <Option B>

- Good: <…>
- Bad: <…>

## More information <!-- optional -->

<Links to the spec, issue, related ADRs, evidence, or the team agreement.>
```

## 慣習

- **言語**: 現在の会話の言語で応答・記述すること。上記のテンプレートは英語であり、実行時に適応させること。
- **1つのADRにつき1つの決定** — 複合的な決定は分割すること。
- 短く保つこと — ADRはエッセイではなく記録である。大きな文書は読まれず、保守されなくなる（Nygard）。デフォルトでは必須コアのみを使用し、オプションセクションはそれに見合う価値がある場合にのみ追加する。詳細は外部リンクに任せる。

## References

- Michael Nygard, "Documenting Architecture Decisions," Cognitect, 2011-11-15 — <https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions>
- MADR — Markdown Any Decision Records, v4.0.0 (2024-09-17) — <https://adr.github.io/madr/>
- Joel Parker Henderson, "Architecture decision record (ADR)" template collection — <https://github.com/joelparkerhenderson/architecture-decision-record>
- ISO/IEC/IEEE 42010:2022, *Software, systems and enterprise — Architecture description* — <https://www.iso.org/standard/74393.html>
