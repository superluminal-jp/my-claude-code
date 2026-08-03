---
name: apple-reminders
description: Read and write Apple Reminders from macOS through the bundled osascript (JXA) scripts — list a Reminders list as JSON, create or update a reminder, resolve one by id, and read or write the machine-readable scrum block inside a reminder body. Use when a request needs reminder or task data out of Reminders.app, when items must be added or completed there, or when a Sprint Backlog kept in Reminders has to become flow-metric input.
when_to_use: Any request touching Apple Reminders or Reminders.app on macOS — "what's on my Sprint Backlog", "add a reminder", "mark it done", "which items did I forget to start", "turn my reminders into cycle time data". Also load it before writing any AppleScript or JXA against Reminders, so the property surface and the permission model are known first.
---

# Apple Reminders

Operate Reminders.app from the command line through the scripts in this skill.
Fetch and write with JXA; decide with Python. That split is the whole design:
`scrum_block.py` is unit-tested on any platform, while the `.js` files are a
thin layer that only runs on macOS.

Run scripts by their absolute path so they work whether this skill is installed
at project or user scope:

```bash
osascript -l JavaScript "${CLAUDE_SKILL_DIR}/scripts/list_reminders.js" "Sprint Backlog"
```

## Before the first call

Two separate permissions must be granted, and they fail differently.

1. **Automation (TCC).** The first `osascript` call raises a dialog asking the
   terminal app to control Reminders. Approve it, or pre-grant it at
   *System Settings → Privacy & Security → Automation → (terminal app) →
   Reminders*. Errors `-1743` and `-10004` mean this was denied.
2. **Claude Code permission.** The `Bash(osascript …)` call itself prompts.
   Nothing here is pre-approved on purpose — these scripts change the user's
   own task data.

Neither can be granted non-interactively. On a headless or CI-style run, say so
rather than retrying: the call will hang or fail, not succeed quietly.

## Why osascript and not EventKit

EventKit is Apple's official framework for Reminders and is the right answer for
an app. It is the wrong answer here, for three reasons:

- **It cannot touch Notes.** There is no Notes equivalent of EventKit, so a
  Reminders-via-EventKit design still needs AppleScript for Notes and ends up
  maintaining two mechanisms instead of one.
- **It needs a toolchain and a build artifact.** A Swift CLI means Xcode
  Command Line Tools, a compiled binary to keep current, and an `Info.plist`
  section linked into the binary just so TCC will show a dialog at all.
- **`osascript` is already trusted.** It ships with macOS and is already inside
  the permission framework; a self-built binary needs its own grant, signing,
  and entitlement handling.

The cost of this choice is real and is stated below under *What is not
reachable*. If a future task genuinely needs location triggers or recurrence
rules, EventKit is the escape hatch — say so rather than faking it in JXA.

## The property surface

Only what the Reminders scripting dictionary publishes is available:
`id`, `name`, `body`, `completed`, `completion date`, `due date`,
`remind me date`, `priority`, `creation date`, `modification date`, `container`.

`id` is the stable handle — it is what `--id` resolves and what cross-app links
store. Treat it as opaque; it is formatted `x-apple-reminder://<UUID>`.

### What is not reachable

- **Tags, subtasks, sections, smart lists.** Absent from AppleScript *and*
  EventKit. Reaching them requires the private ReminderKit framework or reading
  Reminders' SQLite store directly — both break on OS updates. Do not offer
  either; put the information in the body block instead.
- **A start date.** EventKit's `startDateComponents` exists but Reminders.app
  ignores it and returns `nil` for anything created in the app, and the
  AppleScript dictionary has no equivalent. This is why `started` lives in the
  body block.
- **The GUI's "linked item" chip.** The link a share-sheet or Siri "remind me
  about this" creates is not `EKReminder.url` and is not reproducible from any
  public API. See *Linking to a note*.

## Scripts

| Script | Does |
|---|---|
| `scripts/list_reminders.js` | A list (or one id, or `--lists`) as JSON |
| `scripts/write_reminder.js` | Create one reminder, or update one by id |
| `scripts/scrum_block.py` | Parse/render the body block; emit flow-metric CSV |

```bash
S="${CLAUDE_SKILL_DIR}/scripts"

# Read
osascript -l JavaScript "$S/list_reminders.js" --lists
osascript -l JavaScript "$S/list_reminders.js" "Sprint Backlog" --open-only
osascript -l JavaScript "$S/list_reminders.js" --id "x-apple-reminder://UUID"

# Create
osascript -l JavaScript "$S/write_reminder.js" \
  --list "Sprint Backlog" --name "Ship the login form" --due 2026-08-08

# Complete
osascript -l JavaScript "$S/write_reminder.js" --id "<id>" --complete
```

`write_reminder.js` cannot delete, and `--id` never falls back to creating. Both
are structural, not advisory. Deleting a reminder destroys the only record of
its Cycle Time and no guardrail hook can recognise a destructive Apple Event, so
deletion stays a human action in Reminders.app — if a user asks for one, tell
them where to click.

Never write `completion date` by hand. Reminders.app sets it when `completed`
flips to true, so the timestamp comes from the app rather than from this
process's clock.

## The scrum block

An opt-in convention, used when a Sprint Backlog lives in Reminders. Because
neither tags nor a start date are reachable, the metadata goes in `body`:

```
--- scrum ---
sprint: 7
size: M
started: 2026-08-01
note: x-coredata://ABC-123/ICNote/p42
---
```

Prose above and below the fence is preserved — a human editing the reminder in
Reminders.app will put it there. `scrum_block.py` is the only thing that should
write this block; it refuses to rewrite a body whose closing fence is missing
rather than guess where the user's prose begins.

```bash
S="${CLAUDE_SKILL_DIR}/scripts"
FLOW="$HOME/.claude/skills/scrum-master/scripts/flow_metrics.py"

# Flow-metric input, then the metrics themselves
osascript -l JavaScript "$S/list_reminders.js" "Sprint Backlog" \
  | python3 "$S/scrum_block.py" csv > tickets.csv
python3 "$FLOW" tickets.csv --as-of "$(date +%F)"

# Items in flight that never recorded a start -- these are missing from
# Cycle Time entirely, so check this before trusting any of the numbers
osascript -l JavaScript "$S/list_reminders.js" "Sprint Backlog" --open-only \
  | python3 "$S/scrum_block.py" unstarted

# Record a start (read-modify-write; the block spans lines, hence stdin)
osascript -l JavaScript "$S/list_reminders.js" --id "<id>" --field body \
  | python3 "$S/scrum_block.py" set --started today \
  | osascript -l JavaScript "$S/write_reminder.js" --id "<id>" --body-stdin
```

`csv` emits exactly `item_id,started_at,completed_at`, which is what the
`scrum-master` skill's `flow_metrics.py` reads — so real Reminders data runs
through it unmodified, and no metric has to be invented.

Two properties of the data worth stating whenever these numbers are reported:

- **An item with no `started` is absent from Cycle Time.** `csv` drops it and
  warns on stderr; `unstarted` names it. Report the count alongside the metrics
  — a median over half the sprint is not a median of the sprint.
- **`creation date` → completion is Lead Time, not Cycle Time.** The gap
  between the two is the item's wait in the Product Backlog. Keep them
  separate; never substitute one for the other.

## Linking to a note

The chip that Reminders shows for a GUI-created link cannot be produced from
any public API. `EKReminder.url` is a different field that does not drive it,
and the `x-apple-reminderkit://` scheme that does is undocumented and unowned.

So links are stored as ids and resolved by script: the `note:` key above holds a
note's id, and the note's body holds `[[reminder:<id>]]` going the other way.
Resolving either direction is a `--id` lookup. The trade-off is deliberate — no
one-tap native link, in exchange for a link built only on object ids, the most
basic and most stable thing both apps expose.

Ids can go stale (a deleted target leaves an orphan marker, and an item moved
between accounts can change id). Verify a link resolves before presenting it as
live.

## Reporting back

Return the answer, not the transcript. A list of 200 reminders is JSON the
caller does not need; the three overdue ones are. When a script fails, give the
error and which of the two permissions above is the likely cause.

## Sources

- Reminders AppleScript properties — [Demonstration of using AppleScript with Reminders.app](https://gist.github.com/n8henrie/c3a5bf270b8200e33591)
- `startDateComponents` and Reminders.app ignoring it — [Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekreminder/startdatecomponents), [Apple Developer Forums thread 676018](https://developer.apple.com/forums/thread/676018)
- `EKReminder.url` not driving the GUI link — [Apple Developer Forums thread 128140](https://developer.apple.com/forums/thread/128140)
- Tags and subtasks absent from the public surface — [Introducing RemCTL (MacStories)](https://www.macstories.net/stories/introducing-remctl-the-power-user-reminders-cli-for-macos-and-ai-agents/)
- The GUI link path that has no API equivalent — [Add a reminder from another app on Mac](https://support.apple.com/guide/reminders/remn1f735fdc/mac)
- Cycle Time / Lead Time / WIP definitions — `scrum-master` skill, `references/sources.md` `[KGS21]`
