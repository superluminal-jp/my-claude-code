---
status: Accepted
date: 2026-08-27
deciders: Taiki Ogihara, Claude
---

# 0013. Automate Apple Reminders via a compiled EventKit CLI, not AppleScript

## Context and problem statement

The `apple-reminders` skill (ported into this repo as part of `specs/033-apple-notes-reminders-port`) needs a programmatic route into Reminders.app: creating/reading/updating reminders and lists, and detecting completion state and due dates. Apple exposes two viable routes to Reminders data: **EventKit** (a first-party Swift/Objective-C framework) and **AppleScript/JXA** (Apple Events, the same mechanism the sibling `apple-notes` skill uses for Notes.app, since Notes has no EventKit-equivalent framework at all — see `specs/033-apple-notes-reminders-port/research.md` decision 1).

Which route Reminders automation uses is a structural choice: it determines what fields are reachable (typed vs. untyped), what identifier stability guarantees exist for cross-referencing a reminder later, whether a compiled-binary build step and its own separate OS permission model are required, and what every downstream contract (permission-detection messaging, the CLI's command surface, the build toolchain) gets built against. Switching later is not a local change — it means redesigning the CLI's argument surface, its build step, and its permission-precondition messaging, not swapping one library call.

## Decision drivers

- Access to typed fields AppleScript cannot expose (recurrence rules, priority).
- A stable, server-provided identifier (`calendarItemExternalIdentifier`) usable for cross-referencing a reminder independent of local account/calendar moves.
- Minimizing setup friction (a build step and its own permission grant vs. zero-install AppleScript).

## Considered options

- EventKit (compiled Swift command-line tool)
- AppleScript/JXA (no build step, matching the `apple-notes` skill's approach for Notes)

## Decision outcome

We will automate Reminders via a compiled Swift/EventKit command-line tool, built once locally via `swiftc` against Xcode Command Line Tools, because EventKit is Apple's official framework for Reminders and returns typed objects with fields AppleScript cannot reach, including the more stable `calendarItemExternalIdentifier`. This was decided explicitly during scoping of `specs/033-apple-notes-reminders-port` (see that spec's Assumptions section and `research.md` decision 5), trading away a zero-install AppleScript alternative for these guarantees.

### Consequences

- Positive: reminder fields arrive typed rather than parsed out of Apple Event records; recurrence rules and priority become reachable; cross-app references can rely on `calendarItemExternalIdentifier`, which is more stable across account/calendar moves than the local `calendarItemIdentifier` AppleScript would be limited to.
- Positive: the Reminders privacy permission model (full-access vs. write-only, introduced in macOS 14) is EventKit-native and can be checked/reported precisely, rather than inferred from generic Automation-permission errors.
- Negative: requires a one-time local build step (Xcode Command Line Tools + `swiftc`), which AppleScript would not need — this is a real setup-friction cost for anyone installing the skill.
- Negative: the binary must link `Info.plist` into its `__TEXT,__info_plist` section for TCC to source the permission-dialog description from; omitting this produces an unrecoverable "access not granted" state with no way for the user to grant it. This is a load-bearing build detail future maintainers must not drop.
- Negative: introduces a second automation technology alongside `apple-notes`'s AppleScript/JXA approach, rather than one uniform mechanism across both skills — accepted because Notes has no EventKit equivalent to unify against in the first place.

## Confirmation

`apple-reminders/scripts/build.sh` is the single build entry point and is documented (in the skill's `SKILL.md` and in `specs/033-apple-notes-reminders-port/contracts/reminders-cli.md`) as the only supported way to produce the binary; a manual `swiftc` invocation without `build.sh`'s linker flags is called out there as producing the unrecoverable permission-dialog failure described above.

## Pros and cons of the options

### EventKit (compiled Swift CLI)

- Good: typed fields, stable external identifier, native Reminders permission model.
- Bad: build step required; a second automation technology in this repo's Apple-automation surface.

### AppleScript/JXA

- Good: no build step, no compiler toolchain dependency; uniform mechanism with `apple-notes`.
- Bad: no typed fields; no access to recurrence rules or priority; cross-app references would be limited to the less stable local identifier.

## More information

Originates from `specs/033-apple-notes-reminders-port/spec.md` (Assumptions) and `specs/033-apple-notes-reminders-port/research.md` (decision 5), where this trade-off was decided with the user during feature scoping. Those are this feature's planning artifacts, not a stable reference — this ADR is the durable record of the decision and its rationale.
