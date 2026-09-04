---
name: apple-notes
description: Read and write Apple Notes from macOS through bundled JXA (osascript -l JavaScript) scripts — ensure a folder (optionally as a subfolder of another), list a folder as JSON, fetch one note by id, create a note, append to an existing one, replace one named block in place, and conditionally overwrite or delete a note under a SHA-256 hash gate. Use when a request needs content out of Notes.app, when a stable folder must be prepared, or when prose has to be recorded there.
when_to_use: Any request touching Apple Notes or Notes.app on macOS — "what does my <folder> note say", "write this up in Notes", "append today's decision", "find the <topic> note". Also load it before writing any AppleScript or JXA against Notes, so the HTML body model and the macOS-only constraint are known first.
---

# Apple Notes

Operate Notes.app from the command line through the scripts in this skill.

Run scripts by their absolute path so they work whether this skill is installed
at project or user scope:

```bash
osascript -l JavaScript "${CLAUDE_SKILL_DIR}/scripts/list_notes.js" "Some Folder"
```

## Two constraints to state up front

**Notes has no framework.** There is no EventKit equivalent, no Contacts-style
API. Apple Events — AppleScript, or JXA on the same dictionary — is the only
supported programmatic route.

**It is macOS-only.** There is no iOS route to write a note programmatically,
and there is no fully non-interactive (headless) execution path — see
"Before the first call" below. If a workflow needs to run from iPhone or in
CI, the note side of it cannot; say so rather than designing around a path
that does not exist.

Every script addresses the app by bundle identifier —
`Application('com.apple.Notes')`, not `Application('Notes')`. Apple's own
JXA release notes document the bundle-ID form as an equally valid argument
to `Application()` (see "Sources"), and it is the only form immune to
display-name collisions: `lsregister -dump` on a real machine can show more
than one bundle registered under the display name "Notes" (the real
`com.apple.Notes` and, observed here, a `com.apple.mobilenotes` on-demand
placeholder bundle) — a documented general mechanism by which name-based
resolution is not guaranteed unique, independent of whether any single
observed misbinding involved that specific pair. If a write ever lands
somewhere unexpected, confirm which bundle answered with
`Application('com.apple.Notes').id()` before assuming the script is wrong.

## Before the first call

Three separate requirements, failing differently. None can be satisfied
non-interactively — on a headless run, say so rather than retrying.

1. **Automation (TCC).** The first `osascript` call raises a dialog asking the
   terminal app to control Notes. Approve it, or pre-grant it at
   *System Settings → Privacy & Security → Automation → (terminal app) →
   Notes*. Errors `-1743`, `-10004`, and `-10827` mean this was denied.
2. **Claude Code permission.** The `Bash(osascript …)` call itself prompts.
   Nothing here is pre-approved on purpose — these scripts change the user's
   own notes.
3. **An active GUI (Aqua) login session.** `osascript`/JXA can only launch
   and control Notes.app when a user is logged into the Mac's graphical
   session — it cannot over SSH, from a LaunchAgent/LaunchDaemon not bound to
   that session, or at the login screen. Error `-600` ("Application isn't
   running") means this, not a TCC denial: Notes could not even be launched
   to ask for permission. Every script here launches Notes and waits up to 5
   seconds for it to report itself running before doing anything else, so a
   plain cold start (Notes simply hadn't been opened yet) resolves itself
   automatically — a `-600` that still reaches the caller means the GUI
   session itself is unavailable, a different machine's environment rather
   than something retrying the same call will fix.

Every script's own error output already names which of the three this is —
`-600`, `-1743`, `-10004`, and `-10827` are translated into the sentences
above rather than left as bare numbers.

## Scripts

| Script | Does |
|---|---|
| `scripts/ensure_folder.js` | Create or reuse one exact-name folder, or, with `--parent-id`, as a direct child of another folder |
| `scripts/list_notes.js` | A folder (or one id, or `--folders`) as JSON |
| `scripts/write_note.js` | Create a note, append to one by id, replace one named block, or — under a hash gate — overwrite or delete one |
| `scripts/note_write_guard.py` | Computes the SHA-256 hash gate `--overwrite-stdin`/`--delete` check against |

A note's `body` is HTML, not plain text — a `--plaintext` read is lossy and
must never be round-tripped back into a write. That, exact command usage for
every script above, the safe-Markdown grammar `write_note.js` accepts, the
conditional-overwrite/delete hash-gate flow, and the Notes↔Reminders linking
workaround are all in `references/reference.md` — read the section you need
there before calling a script for the first time in a session.

## Reporting back

Return the answer, not the transcript. A folder's worth of HTML bodies is not
a result; the two lines the caller asked about are. When a script fails, pass
along the error text — it already names the likely cause among the three
requirements above when the failure matches a known Apple Event error code.
