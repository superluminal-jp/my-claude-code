# Apple Notes — reference

Detail that SKILL.md doesn't inline: exact command usage, the note data
model, the Markdown grammar, the conditional overwrite/delete flow, the
Reminders-linking workaround, and citations. Read the section you need —
this file isn't meant to be read start to end.

- [The property surface](#the-property-surface)
- [Script usage](#script-usage)
- [Editing a named block in place](#editing-a-named-block-in-place)
- [The safe Markdown subset](#the-safe-markdown-subset)
- [Conditional overwrite and delete](#conditional-overwrite-and-delete)
- [Linking a note to a reminder](#linking-a-note-to-a-reminder)
- [Sources](#sources)

## The property surface

`id`, `name`, `body`, `creation date`, `modification date`, `container`
(and `folder`: `name`, `id`, `container`). This property list comes from
inspecting the live scripting dictionary in Script Editor on this machine —
Apple does not currently publish a browsable reference page for it (see
"Sources" below).

`id` is the stable handle — formatted `x-coredata://<store>/ICNote/p<N>`. Treat
it as opaque.

**`body` is HTML, not text.** Everything follows from that:

- List output omits bodies unless asked for (`--with-body`).
- `--plaintext` strips the markup for reading. Never round-trip that back into
  a body — it is lossy by construction.
- Create and whole-body overwrite accept a safe Markdown subset (below) and
  convert it to Notes-compatible HTML.
- Notes derives the displayed title from the **first line of the body**, not
  from a separately-set `name` property. `write_note.js` supplies only a body
  beginning with one `<h1>` at creation time; it never sets `name` alongside
  `body`, since doing so makes Notes inject a duplicate title line.

There is no query language. Filtering a folder means fetching it and filtering
in the caller.

## Script usage

```bash
S="${CLAUDE_SKILL_DIR}/scripts"

# Ensure a destination (safe to retry — matches by exact name, fails on
# more than one match rather than picking one)
osascript -l JavaScript "$S/ensure_folder.js" --name "Some Folder"

# Ensure a subfolder inside another folder
osascript -l JavaScript "$S/ensure_folder.js" --name "Sub Folder" --parent-id "<folder id>"

# Read — bodies are omitted unless asked for
osascript -l JavaScript "$S/list_notes.js" --folders
osascript -l JavaScript "$S/list_notes.js" "Some Folder"
osascript -l JavaScript "$S/list_notes.js" "Some Folder" --with-body
osascript -l JavaScript "$S/list_notes.js" --id "<id>" --plaintext

# Create — the first line of --text becomes the title Notes.app displays
osascript -l JavaScript "$S/write_note.js" --folder "Some Folder" \
  --title "Sprint 7 Goal" --text "Cut checkout drop-off on mobile."

# Prefer --folder-id once same-named folders can exist in different places
# (e.g. two projects each with their own "Sprint 1" subfolder) — --folder
# searches the whole account by exact name and refuses on more than one match.
osascript -l JavaScript "$S/write_note.js" --folder-id "<folder id>" \
  --title "Sprint 1 Goal" --text "..."

# Append (existing content is never altered)
echo "Follow-up: check with design" \
  | osascript -l JavaScript "$S/write_note.js" --id "<id>" --append-stdin

# Replace one named, fenced region in place — created on first write,
# replaced (not duplicated) on every write after that
echo "status: in progress" \
  | osascript -l JavaScript "$S/write_note.js" --id "<id>" --replace-block "status" --replace-stdin
```

`ensure_folder.js` trims boundary whitespace and requires a non-empty name.
One match is reused (`created: false`); no match creates one folder
(`created: true`); multiple matches fail before writing.

## Editing a named block in place

`--replace-block <name>` (with `--id`, plus one of `--replace <text>` /
`--replace-stdin` / `--replace-html <html>`) finds a `--- <name> ---` …
`---` fenced region in the note's raw HTML body and replaces exactly that
span — never anything outside it. If the block does not exist yet, it is
created (appended), the same "ensure" posture `ensure_folder.js` already
takes; if it exists exactly once, it is replaced; if the name matches more
than once, or the fence is unterminated, the call refuses rather than
guessing. Use this for machine-owned structured content inside a note — not
for editing a human's free-form prose, which append handles instead.

## The safe Markdown subset

`write_note.js`'s create mode never sets `name` alongside `body` — see "The
property surface" above for why. The full safe-Markdown-subset grammar
(headings, inline styles, lists, alignment, code blocks) and the explicit
rejection list for formats Apple Events cannot reproduce (Block Quote,
Highlight, Font family, Dashed List, Checklist) are implemented in
`markdownToNotesHtml`/`validateNotesMarkdown` in that script — read it before
extending the grammar, since every accepted format there was checked against
what the public Apple Events HTML boundary actually preserves, not just what
the app itself supports.

**Headings get an automatic blank line after them.** Notes does not keep `#`
through `###` as real `h1`–`h3` block elements with their own margin — a
round trip through the app flattens each one to a plain `<div>` holding a
bold, sized `<span>`, and inline `margin`/`padding` on that div (or using
`<p>` instead of `<div>`) is silently stripped the same way. A side-by-side
scratch note confirmed the one thing that does open visible space is a blank
paragraph — the same `<div><br></div>` a manual double-Return produces — so
`markdownToNotesHtml` inserts one after every heading whose next source line
isn't already blank (no double spacer if the caller already left one). This
is why a note built from this grammar doesn't look as cramped under its
headings as the raw HTML shape might suggest.

## Conditional overwrite and delete

`--overwrite-stdin` (replace the whole body) and `--delete` (remove the note)
both require `--expect-hash <sha256>` — the SHA-256 hexdigest of the note's
plaintext body, computed from a `--plaintext` read taken immediately
beforehand:

```bash
S="${CLAUDE_SKILL_DIR}/scripts"

CURRENT=$(osascript -l JavaScript "$S/list_notes.js" --id "<id>" --plaintext --field plaintext)
HASH=$(printf '%s' "$CURRENT" | python3 "$S/note_write_guard.py" hash)

# Whole-body replace
echo "corrected content" | osascript -l JavaScript "$S/write_note.js" --id "<id>" \
  --overwrite-stdin --expect-hash "$HASH"

# Delete
osascript -l JavaScript "$S/write_note.js" --id "<id>" --delete --expect-hash "$HASH"
```

Before either call, `write_note.js` recomputes the hash of the note's
*current* plaintext body and compares it to `--expect-hash`. If they don't
match — the note changed since the caller last read it — the call refuses:
**no write happens, at all**, and the command exits non-zero. This is
optimistic concurrency, not a permission check: a caller that read the note
seconds ago and is correctly, deliberately overwriting it sails through.
What it stops is silently clobbering a note that changed out from under the
caller between the read and the write.

**This is a real, irreversible-feeling capability.** Unlike append and
`--replace-block`, a wrong `--overwrite-stdin` or `--delete` call can destroy
a human's prose. The hash gate does not, and cannot, protect against a
caller that read the note correctly and then made the wrong call anyway — no
hook can inspect what an Apple Event actually sends. **Before calling either
flag, present the replacement content — or, for `--delete`, the note being
deleted — to the user and get their explicit approval, every time.** This is
a convention this script cannot enforce; it is the operator's responsibility.

A deleted note moves into Notes.app's "Recently Deleted" folder — the same
place a UI-driven delete lands it — where it stays recoverable for a limited
time before permanent removal. Apple's own sources do not agree on an exact
retention window (reports range from 30 to 40 days); do not state a specific
day count as guaranteed.

## Linking a note to a reminder

Neither app exposes a public API for the "linked item" chip the GUI shows,
and Notes' own "Add Link" feature only documents Safari, Podcasts, and other
notes as targets — Reminders is not among them. Apple *does* offer an
official one-way workflow instead — on macOS, select a note (or note text)
and use `File > Share > Reminders` (or "Send Copy" on iOS) — to turn its
content into a new reminder. It has real limits: it only goes Notes →
Reminders, the new reminder keeps no reference back to the source note, it's
a manual GUI action only (no script/API path), and it can misbehave on notes
with attachments. Point users there rather than inventing a custom linking
convention.

## Sources

Cited URLs were independently re-verified against current Apple documentation
while this skill was built (2026-08-27), rather than carried over from any
prior source unchecked.

- No official framework beyond AppleScript/Apple Events for Notes — [Scriptable Applications – Apple Developer](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptX/Concepts/scriptable_apps.html)
- Automation is a distinct macOS privacy category — [Allow apps to control other apps on Mac – Apple Support](https://support.apple.com/guide/mac-help/mchl07817563/mac)
- Notes text styles, font/color/size, highlighting, and alignment — [Format notes on Mac](https://support.apple.com/guide/notes/format-notes-apd1955d3b21/mac)
- "Add Link" documented targets (Safari, Podcasts, other notes — no Reminders) — [Add links in Notes on Mac](https://support.apple.com/guide/notes/add-links-apde615d29c2/mac)
- The `note`/`folder` property surface used above is from Script Editor's live scripting-dictionary viewer on this machine, not a published Apple reference page — [View an app's scripting dictionary in Script Editor](https://support.apple.com/guide/script-editor/view-an-apps-scripting-dictionary-scpedt1126/mac)

The following two were independently verified via web search on 2026-08-28,
when the "-600" troubleshooting item and the `.whose()`/`.byId()` avoidance in
`list_notes.js`/`write_note.js` were added, in response to both symptoms
being reported from another Mac:

- `-600` means "Application isn't running" and is thrown when `osascript` cannot even launch the target app (no active GUI session, Automation blocked by a hardened runtime, etc.) — [Error Number: -600 Application isn't running – MacScripter](https://www.macscripter.net/t/error-number-600-application-isn-t-running/70925)
- Notes.app's own AppleScript/JXA dictionary is widely reported as unreliable ("half-baked scripting support... a gazillion questions about weird behavior and errors"), independent of JXA's general `.whose()`/`.byId()` support — [Notes – JavaScript for Automation (JXA)](https://bru6.de/jxa/automating-applications/notes/)

The following was added on 2026-08-30, in response to a reported concern
that name-based `Application('Notes')` resolution could bind to the wrong
bundle (a widget extension was named as the suspected target):

- `Application()` officially accepts a bundle identifier as an alternative to a display name (`Application('com.apple.mail')` is Apple's own example) — [JavaScript for Automation Release Notes – OS X 10.10](https://developer.apple.com/library/archive/releasenotes/InterapplicationCommunication/RN-JavaScriptForAutomation/Articles/OSX10-10.html)
- On this machine, `Application('Notes').id()` and `id of application "Notes"` both correctly resolved to `com.apple.Notes` — the specific widget-extension misbinding could not be reproduced. What `lsregister -dump` (`/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -dump`) did show is a second, unrelated bundle also registered under the display name "Notes" (`com.apple.mobilenotes`, an on-demand placeholder under `~/Library/Daemon Containers/.../Placeholders-v6.noindex/`) — confirming display-name collisions are a real, general Launch Services condition on this class of app, even though this specific pair was not observed to cause a wrong bind. Scripts here now address Notes by bundle ID regardless, since that is the only form immune to the whole collision class rather than just the one pair checked.
