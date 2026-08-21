# Sourcing, freshness, and attribution

Load this when deciding which DADS source to trust, refreshing the bundled
archive, or writing attribution.

## The bundled archive

`references/dads-docs/` is a verbatim copy of the Digital Agency's official
Markdown export of the design system site, published by the Digital Agency for
AI reference. It contains guidance, foundations, component specifications, and
accessibility policy — and essentially **no code**. For implementation, go to
[component-implementation.md](component-implementation.md).

Read the version from the archive itself rather than from any prose:

```sh
grep -m1 '^# ' .claude/skills/digital-agency-frontend/references/dads-docs/index.md
```

### Refreshing the archive

The vendored dads-docs archive is kept unmodified so an update is a straight replace — nothing in
this skill duplicates its wording, so refreshing it never requires editing the
surrounding documents.

1. Download the current Markdown bundle from <https://design.digital.go.jp/dads/resources/> and unzip it.
2. Replace the directory, keeping Markdown only:

```sh
SKILL=.claude/skills/digital-agency-frontend/references
rm -rf "$SKILL/dads-docs" && mkdir -p "$SKILL/dads-docs"
cd <unzipped-bundle> && find . -name '*.md' -print0 \
  | tar --null -cf - --files-from=- \
  | (cd "$OLDPWD/$SKILL/dads-docs" && tar -xf -)
```

3. Confirm the new version stamp with the `grep` above and report the version change.
4. Confirm nothing was silently dropped — the staged count must equal the count on disk:

```sh
find "$SKILL/dads-docs" -name '*.md' | wc -l
git add "$SKILL/dads-docs" && git diff --cached --name-only | grep -c dads-docs/
```

A mismatch means an ignore rule swallowed part of the archive. The macOS global
`Icon` rule is the known case — `.gitignore` negates it for `foundations/icon/`.

Do not hand-edit files under `dads-docs/`. Local commentary belongs in the other
reference documents.

## Which source wins

In descending order of authority:

1. **The live official site and repositories**, when reachable. Always authoritative.
2. **The installed packages** in the target project (`node_modules/@digital-go-jp/*`) for token and API questions — they describe what the project actually builds against.
3. **`references/dads-docs/`** for design intent, component specifications, and accessibility policy.
4. **This skill's other reference documents**, which are distilled operational guidance.

Every page in the archive carries a `source_url` in its front matter. When
current detail matters — and always for versions, availability, and anything the
archive marks as changing — open that URL or query npm instead of quoting the
archive. If live content and the archive disagree, follow the live source, say so,
and name the archive path that is now stale.

Restrict source research to the Digital Agency sites and the official
`digital-go-jp` GitHub organization. If nothing current is reachable, use the
archive as a dated fallback and state that freshness was not verified.

## Licensing and attribution

The Digital Agency splits the design system into three parts with different terms.
Full text: <https://design.digital.go.jp/dads/introduction/notices/>.

### Design system proper — documentation, guidance, specifications

This covers the site and the bundled Markdown archive. Reuse requires attribution:

> 出典：デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/

If the content is edited or adapted, say so **separately and in addition** to the
attribution above:

> デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ のコンテンツを加工して作成

Never present adapted content as though the Digital Agency produced it. Otherwise
the Digital Agency copyright policy applies:
<https://www.digital.go.jp/copyright-policy>.

### Code snippets — the GitHub repositories and npm packages

MIT licensed. Because they exist to be adapted, **UI built by modifying them needs
no visible source attribution**. Publishing them unmodified does require it:

> 出典：デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ およびデジタル庁GitHub https://github.com/digital-go-jp

Preserve MIT notices where the license requires them in distributed source.

### Figma data

CC BY 4.0 via Figma Community, with the bundled Material Symbols icons under
Apache License 2.0. Adapted UI parts need no attribution; unmodified public reuse
does. This skill does not copy Figma data — check the live terms if a task
introduces it.

### Illustrations and icons

Governed by the separate 「イラストレーション・アイコン素材利用規約」, not by the
terms above. Do not copy them merely because a component example displays one.

### Third-party components

The site redistributes Noto Sans (SIL OFL 1.1), MiniSearch, the Invokers polyfill,
Vaporetto and its models, and several Rust/WASM crates (MIT, Unicode License v3,
zlib). These terms attach to those assets specifically, not to DADS content.

## Standing limits

- Never claim an interface is a Digital Agency product or is endorsed by the Digital Agency.
- Never invent tokens, component names, version numbers, or conformance claims. Label project-specific additions as such.
- State plainly what was reused and what was changed. When uncertain, link the live usage notice rather than paraphrasing it.
