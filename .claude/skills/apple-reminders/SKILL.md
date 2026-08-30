---
name: apple-reminders
description: Read and write Apple Reminders from macOS through a bundled EventKit CLI — ensure or list a Reminders list as JSON, create, update, or complete a reminder, and resolve one by identifier. Use when a request needs reminder or task data out of Reminders.app, when a stable list must be prepared, or when items must be added or completed there.
when_to_use: Any request touching Apple Reminders or Reminders.app on macOS — "what's on my <list>", "add a reminder", "mark it done", "which reminders are still open". Also load it before writing any EventKit, AppleScript, or JXA against Reminders, so the property surface, the build step, and the permission model are known first.
---

# Apple Reminders

Operate Reminders.app through a small EventKit CLI, built from the single
Swift file in this skill.

## Why EventKit here, and JXA for Notes

Reminders has EventKit — Apple's official framework, and the route that
returns reminders as typed, queryable objects instead of Apple Event records
to be parsed back out of `osascript` output. Notes has no equivalent
framework, so the sibling `apple-notes` skill uses JXA instead. This is a
deliberate decision: EventKit was chosen over the AppleScript route because
only it returns typed objects instead of text to re-parse.

The price of EventKit is a build step and a different permission category.
Both are handled below, and neither is optional.

## Before the first call

### 1. Build the tool

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/build.sh"   # prints the binary path; no-op if current
```

Needs the Xcode Command Line Tools (`xcode-select --install`). One `swiftc`
call over one file — no package manifest, no lockfile.

**Do not build by hand without the linker flags.** `build.sh` links
`Info.plist` into the binary's `__TEXT,__info_plist` section, and that is
load-bearing: TCC reads the usage description out of the running binary, so a
bare Mach-O with no such section gives the permission dialog nowhere to come
from. A build without this flag fails as "access not granted" with no way for
the user to grant it — a build defect that looks exactly like a user denial.

### 2. Grant Reminders access

EventKit's permission is the **Reminders** privacy category — *not*
Automation, which is what the `apple-notes` skill needs. They are separate
grants and are denied separately.

The first run raises a dialog. If it does not appear, or was denied, grant it
at *System Settings → Privacy & Security → Reminders*. macOS 14 split this
into full and write-only access; this tool reads, so it requests full access.

Neither the build nor the grant can be done non-interactively. On a headless
run, say so rather than retrying. The `Bash` call itself also prompts in
Claude Code — nothing here is pre-approved on purpose.

## The property surface

Per reminder: `id`, `externalId`, `name`, `body`, `completed`,
`completionDate`, `creationDate`, `modificationDate`, `dueDate`, `priority`,
`list`.

**Two identifiers, not interchangeable:**

- `id` (`calendarItemIdentifier`) — local, not guaranteed to persist when an
  item moves between accounts.
- `externalId` (`calendarItemExternalIdentifier`) — server-provided, more
  stable, but not guaranteed unique for recurring items.

Prefer `externalId` for any reference kept beyond the current session.

Never set `completionDate` by hand — EventKit sets it automatically when
`completed` flips (both directions).

## Commands

| Command | Does |
|---|---|
| `lists` | Every reminder list, by name |
| `ensure-list --name <name>` | Create or reuse one exact-name list |
| `list <name> [--open-only]` | One list as JSON |
| `get <identifier>` | One reminder, by either identifier |
| `create --list … --name …` | Create one |
| `update <identifier> …` | Update one; never creates |
| `complete <identifier> [--undo]` | Complete or reopen one |

```bash
CLI="$(bash "${CLAUDE_SKILL_DIR}/scripts/build.sh")"

"$CLI" lists
"$CLI" ensure-list --name "Some List"
"$CLI" create --list "Some List" --name "Ship the login form" --due 2026-08-08
"$CLI" list "Some List" --open-only
"$CLI" get "<identifier>"
"$CLI" update "<identifier>" --name "Ship the login form (v2)"
"$CLI" complete "<identifier>"
"$CLI" complete "<identifier>" --undo
```

`update` never falls back to creating — an identifier that does not resolve
fails the call rather than silently forking a duplicate item.

`ensure-list` trims boundary whitespace and requires a non-empty name. It
matches by exact, case-sensitive name across reminder-capable calendars. One
match is reused (`created: false`); no match creates one list in the same
source as the configured default reminder list (`created: true`); multiple
matches fail before writing. If no default reminder list/source is
configured, the command stops instead of guessing an account.

There is **no delete command**, and `update` never falls back to creating.
Both are structural, not advisory: deleting a reminder destroys the only
record of it with no recovery path this CLI can rely on, unlike Notes' OS-level
"Recently Deleted" folder. If a caller asks to delete a reminder, decline and
point to Reminders.app for the manual action.

## Linking a note to a reminder

Neither app exposes a public API for the "linked item" chip the GUI shows.
Apple *does* offer an official one-way workflow — on macOS, `File > Share >
Reminders` (or "Send Copy" on iOS) — to turn a note's content into a new
reminder. It has real limits: it only goes Notes → Reminders, the new
reminder keeps no reference back to the source note, it's a manual GUI action
only (no script/API path), and it can misbehave on notes with attachments.
Point users there rather than inventing a custom linking convention.

## Reporting back

Return the answer, not the transcript. When a command fails, say which of the
three preconditions is the likely cause — the build, the Reminders grant, or
the Claude Code Bash permission.

## Sources

Cited URLs were independently re-verified against current Apple documentation
while this skill was built (2026-08-27), rather than carried over from any
prior source unchecked.

- `EKEventStore.requestFullAccessToReminders` and the macOS 14 full/write-only split — [Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekeventstore/requestfullaccesstoreminders(completion:))
- `calendarItemIdentifier` — [Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemidentifier)
- `calendarItemExternalIdentifier` — [Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemexternalidentifier)
- `EKReminder.url` reported nil over EventKit even when the GUI shows a link — [Apple Developer Forums thread 128140](https://developer.apple.com/forums/thread/128140)
- Adding a reminder from another app via the Share Sheet — [Add a reminder from another app – Apple Support](https://support.apple.com/guide/reminders/add-a-reminder-from-another-app-remn1f735fdc/mac)
- No reminder-list-group/section type in EventKit's public API, confirmed by an Apple engineer — [Apple Developer Forums thread 683611](https://developer.apple.com/forums/thread/683611)
