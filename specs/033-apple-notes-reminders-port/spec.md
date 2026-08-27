# Feature Specification: Apple Notes and Reminders Automation Skills

**Feature Branch**: `033-apple-notes-reminders-port`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Port apple-notes and apple-reminders Claude Code skills from the local repo /Users/taikiogihara/work/apple-task-manager into this repo as generic, safe, efficient macOS automation skills for Apple Notes and Apple Reminders — no Scrum-specific coupling. Generic-only extraction (no project registry, no scrum body block, no flow-metrics wiring); Reminders automation via a compiled Swift/EventKit CLI; every ported behavioral claim independently re-verified against current official Apple documentation before being encoded. Keep skill names apple-notes and apple-reminders."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prepare a destination and capture something (Priority: P1)

An operator needs somewhere stable to put a note or a reminder, then needs to actually write one there — a goal, a task, a piece of prose — without first hand-checking whether that folder or list already exists.

**Why this priority**: This is the minimum useful capability. Without a safe, idempotent way to get a destination and write into it, nothing else in this feature has anywhere to operate.

**Independent Test**: Can be fully tested by requesting a folder (or list) by name twice in a row and confirming only one is ever created, then writing one note (or reminder) into it and confirming it appears with the expected content.

**Acceptance Scenarios**:

1. **Given** no folder named "Test Folder" exists in Notes, **When** the operator asks to ensure it exists, **Then** exactly one folder with that name is created.
2. **Given** a folder named "Test Folder" already exists, **When** the operator asks to ensure it again, **Then** no new folder is created and the existing one is reused.
3. **Given** two folders already exist with the exact same requested name, **When** the operator asks to ensure that name, **Then** the request fails rather than silently picking one.
4. **Given** a prepared folder or list, **When** the operator creates a note or reminder in it with a title/name and content, **Then** the item exists in that destination with the requested content, and reading it back returns what was written.

---

### User Story 2 - Read back what's there (Priority: P2)

An operator needs to find out what a folder or list currently contains, or fetch one specific item, without wading through unrelated bulk content.

**Why this priority**: Read access is what makes the write side (Story 1) useful for real work — an operator needs to confirm state and retrieve content, not just fire writes blindly.

**Independent Test**: Can be fully tested by listing a folder/list with known contents and confirming the returned items match, then fetching one item by its identifier and confirming its fields are complete and correctly typed.

**Acceptance Scenarios**:

1. **Given** a folder containing several notes, **When** the operator lists it without asking for full content, **Then** each note's identifying fields are returned but full body content is omitted.
2. **Given** the same folder, **When** the operator lists it and explicitly asks for full content, **Then** each note's body is included.
3. **Given** a known note or reminder identifier, **When** the operator fetches it directly, **Then** all of that item's fields are returned in one response.
4. **Given** a list of reminders, **When** the operator asks to see only the open (incomplete) ones, **Then** completed reminders are excluded from the result.

---

### User Story 3 - Update existing content without collateral damage (Priority: P3)

An operator needs to add to a note, edit one specific machine-owned section of a note in place, or update/complete a reminder — without disturbing content that isn't part of the requested change, and without accidentally creating a duplicate when the target doesn't exist.

**Why this priority**: Most real usage is incremental — appending a log line, updating a status field, checking something off — not wholesale recreation. This must be safe against clobbering unrelated content before any destructive capability (Story 4) is introduced.

**Independent Test**: Can be fully tested by appending to a note with existing content and confirming the original content is intact; by replacing one named section and confirming only that section changed; and by updating and completing a reminder and confirming its other fields are unaffected.

**Acceptance Scenarios**:

1. **Given** a note with existing content, **When** the operator appends new content, **Then** the original content remains unchanged and the new content is added.
2. **Given** a note containing one instance of a named, delimited section, **When** the operator replaces that section, **Then** only the content inside that section changes; content outside it is untouched.
3. **Given** a note with no instance of a named section yet, **When** the operator replaces that section, **Then** the section is created (appended) rather than the request failing.
4. **Given** a note containing two instances of the same named section, **When** the operator requests a replacement, **Then** the request fails rather than guessing which instance to change.
5. **Given** an existing reminder, **When** the operator updates one of its fields, **Then** only that field changes.
6. **Given** an identifier that does not resolve to any existing reminder, **When** the operator requests an update, **Then** the request fails rather than creating a new reminder.
7. **Given** an open reminder, **When** the operator marks it complete, **Then** its completion timestamp is set by the system automatically, not supplied by the operator, and the reminder can subsequently be reopened.

---

### User Story 4 - Safely replace or remove a note's entire content (Priority: P4)

An operator occasionally needs to replace a note's whole content or delete it outright — a real, irreversible-feeling action against a human's own prose — and needs assurance that this can't silently clobber a note that changed since it was last read, and that it never happens without the operator's explicit, informed go-ahead.

**Why this priority**: This is the highest-risk capability in the feature. It depends on Stories 1–3 already working (a destination, a way to read current content, a way to write) and is deliberately last because its safety guarantees are what make it acceptable to ship at all.

**Independent Test**: Can be fully tested by reading a note's current content, computing its expected concurrency token, modifying the note out-of-band, then attempting the overwrite/delete with the stale token and confirming it is refused with zero change made; and separately, by performing a correctly-guarded overwrite/delete and confirming it succeeds only after the replacement content (or deletion target) has been presented for explicit confirmation.

**Acceptance Scenarios**:

1. **Given** a note whose current content the operator has just read, **When** the operator requests a whole-content overwrite using a concurrency token computed from that read, **Then** the overwrite succeeds and the note's content matches the new content exactly.
2. **Given** a note that has changed since the operator last read it, **When** the operator requests a whole-content overwrite using a token computed from the stale read, **Then** the request is refused, no content is changed, and the failure explains that the note changed since it was read.
3. **Given** a note the operator intends to delete, **When** the delete is requested with a valid, current concurrency token, **Then** the note is removed from its folder and is recoverable through the operating system's own deleted-items mechanism, not permanently destroyed on the spot.
4. **Given** any whole-content overwrite or delete request, **When** it is issued, **Then** the operator must have been shown the exact replacement content (or, for a delete, the identity of the note being removed) and given explicit approval before the underlying operation runs — this is a documented operator responsibility around every such call, not a check the system performs automatically at the call site.
5. **Given** a request to delete a reminder, **When** it is received, **Then** it is declined, with guidance that reminder deletion is a manual action in the Reminders app.

---

### User Story 5 - Link a note and a reminder together (Priority: P5)

An operator wants to associate one note with one reminder (e.g., a task and its supporting notes) and later follow that association in either direction, without either app offering a native shareable link between the two.

**Why this priority**: Useful, generically applicable connective tissue once the basic CRUD operations exist for both apps — but nothing else in the feature depends on it, so it is safe to build last.

**Independent Test**: Can be fully tested by recording a link from a reminder to a note, then resolving it from the reminder side to the correct note, and separately recording and resolving the reverse direction from the note side.

**Acceptance Scenarios**:

1. **Given** an existing note and an existing reminder, **When** the operator records a link between them, **Then** each item's identifier for the other is discoverable from the item's own content.
2. **Given** a reminder holding a link to a note, **When** the operator resolves that link, **Then** the correct note is returned.
3. **Given** a note holding a link to a reminder, **When** the operator resolves that link, **Then** the correct reminder is returned.
4. **Given** a link whose target has since been deleted, **When** the operator resolves it, **Then** the failure is reported clearly as an unresolved/stale link rather than a generic error.

---

### Edge Cases

- What happens when the Automation (Notes) or Reminders privacy permission has not yet been granted, or was denied? The operator MUST be told which specific permission is missing and where to grant it, not shown a raw low-level error.
- What happens when the Reminders command-line tool has never been built on this machine (missing Xcode Command Line Tools, or a stale/missing binary)? The operator MUST be told a build step is needed, not shown an opaque "not found" failure.
- What happens on a non-interactive/headless run where a permission dialog would normally appear? The system MUST report that this cannot be granted non-interactively rather than retrying in a loop.
- What happens when an "ensure folder/list" request matches more than one existing folder/list with that exact name? The request MUST fail before writing anything, rather than picking one arbitrarily.
- How does the system handle a note-creation or overwrite request containing a formatting instruction that cannot be reliably produced (e.g., a checklist, a block quote, a highlight, a font-family change, a dashed list)? It MUST reject the request and name the specific unsupported format, before any content is written — never silently approximate it as something else.
- How does the system handle a named-block replace request where the block's delimiters are malformed (e.g., an opening fence with no matching close)? It MUST refuse rather than guess where the block ends.
- What happens when a whole-note overwrite or delete concurrency check fails (the note changed since it was last read)? Zero content changes MUST occur, and the failure MUST explain that the note changed underneath the caller.
- What happens when a cross-app link is recorded using an identifier known to be locally unstable (e.g., an identifier that can change when an item moves between accounts or calendars)? The system MUST prefer the more stable identifier available for that purpose instead.
- What happens when a caller requests deletion of a reminder? The system MUST decline and redirect to the manual deletion path in the Reminders app, since no safe, systemically-gated deletion path exists for reminders the way it does for notes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an operator to ensure (create-if-absent, reuse-if-present) a Notes folder by exact name, optionally as a direct subfolder of another named folder.
- **FR-002**: System MUST allow an operator to ensure (create-if-absent, reuse-if-present) a Reminders list by exact name.
- **FR-003**: System MUST fail an ensure-folder or ensure-list request, without creating anything, when more than one existing folder or list already matches the requested exact name.
- **FR-004**: System MUST allow creating a note in a specified destination folder from a defined, safe subset of Markdown-like formatting input, converting it to the note's native rich-content format.
- **FR-005**: System MUST allow creating a reminder in a specified destination list with at minimum a name, and optionally a due date and free-text body.
- **FR-006**: System MUST allow listing the contents of a folder or list as structured data, omitting each note's full body content by default and including it only when explicitly requested.
- **FR-007**: System MUST allow fetching a single note or reminder in full by its identifier.
- **FR-008**: System MUST allow appending content to an existing note without altering its prior content.
- **FR-009**: System MUST support replacing exactly one named, delimited region within a note's content in place: creating the region if it does not yet exist, replacing it if exactly one instance exists, and refusing the request if the name matches more than once or the region's delimiters are malformed — leaving all content outside the targeted region untouched in every case.
- **FR-010**: System MUST allow updating fields on an existing reminder, and MUST fail rather than create a new reminder when the given identifier does not resolve to an existing one.
- **FR-011**: System MUST allow marking a reminder complete or reopening it, and MUST derive the completion timestamp from the system automatically rather than accepting an operator-supplied value.
- **FR-012**: System MUST validate and fully convert all formatting input before performing any write, such that an invalid or unsupported formatting request cannot result in a partially-written note.
- **FR-013**: System MUST reject, rather than visually approximate, a formatting request for a style that cannot be reliably produced through the supported automation interface, and MUST name the specific unsupported format in the resulting error.
- **FR-014**: System MUST support a whole-content overwrite and a delete operation for notes, each guarded by a concurrency check against the content most recently read by the caller; the operation MUST be refused, with zero change made, if the note's current content does not match what the concurrency check expects.
- **FR-015**: System MUST require, as a documented operator responsibility surrounding every whole-content overwrite or delete of a note, that the exact replacement content (or, for a delete, the identity of the note being removed) is presented to the human user for explicit approval before the call is made.
- **FR-016**: System MUST NOT provide any operation that deletes a reminder; a request to delete a reminder MUST be declined with guidance to perform the deletion manually in the Reminders app.
- **FR-017**: System MUST provide a generic, non-domain-specific convention for recording a link between one note and one reminder, resolvable in both directions by identifier lookup, with no coupling to any particular workflow's own data model.
- **FR-018**: System MUST use, for cross-app link markers, whichever of an item's available identifiers is documented or established as the more stable one for that purpose, rather than one known to change across routine operations (e.g., an account or calendar move).
- **FR-019**: System MUST detect, before the first automation call against each app in a session, whether that app's required OS-level permission has been granted, and MUST report which specific permission is missing and where to grant it when it has not, rather than retrying silently or failing with a raw system error alone.
- **FR-020**: System MUST report, on failure of a Reminders automation call, which of the known preconditions (the command-line tool has not been built, the Reminders permission has not been granted, or the harness's own tool-invocation permission was denied) is the likely cause.
- **FR-021**: System MUST NOT read, write, reference, or otherwise depend on the source skills' Scrum-specific artifacts — the multi-project registry, the Scrum body-block convention, or any flow-metrics integration — none of which are in scope for this feature.
- **FR-022**: System MUST return only the specific fields or items a request asks for, rather than defaulting to full bulk content, wherever a narrower response is possible (see FR-006).

### Key Entities

- **Note**: A Notes.app item. Holds an identifier, an HTML body (from which the displayed title is derived — the first line of the body, not a separately-set name field), a containing folder, and creation/modification timestamps.
- **Notes Folder**: A named container for notes within a Notes account; may itself be nested inside a parent folder.
- **Reminder**: A Reminders.app item. Holds two distinct identifiers with different stability guarantees (see FR-018), a name, an optional free-text body, a completion state with an automatically-derived completion timestamp, an optional due date, priority, and list membership.
- **Reminders List**: A named collection of reminders within a Reminders account.
- **Named Block**: A delimited, machine-owned region within a note's body, identified by a name, distinct from the surrounding free-form prose a human may also edit in that same note.
- **Cross-App Link**: A recorded association between one note and one reminder, stored as each item's identifier for the other, resolvable independently from either side.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Requesting the same-named folder or list ten times in a row results in exactly one folder/list existing, with zero duplicates created.
- **SC-002**: 100% of note-write requests containing an unsupported formatting instruction are rejected, naming the specific unsupported format, before any content is written — never silently approximated as a different format.
- **SC-003**: 100% of whole-note overwrite or delete attempts against a note that changed since it was last read are blocked with zero content change, across all tested concurrent-edit scenarios.
- **SC-004**: An operator can resolve a note-to-reminder link, or the reverse, to its correct target in a single lookup call — no full-account search required in either app.
- **SC-005**: When a required OS-level permission is missing, the operator learns which permission and where to grant it from the very first failed attempt, without needing a second attempt to discover this.
- **SC-006**: Listing a folder or list returns without the caller needing to post-process or strip unwanted full-body content, in the default (no full-content) request shape.
- **SC-007**: Zero requirements in this specification reference, depend on, or require configuring the source skills' Scrum-specific artifacts (project registry, Scrum body block, flow-metrics pipeline).

## Assumptions

- This feature operates only on macOS with Notes.app and Reminders.app present locally; there is no iOS/iPadOS or fully non-interactive/headless execution path, matching the constraint already established for the source skills this feature is derived from.
- Minimum macOS version is macOS 14, since the Reminders permission model (full-access vs. write-only) that this feature relies on for its precondition-detection behavior (FR-019) was introduced there.
- The two OS-level permission grants this feature depends on — Automation for Notes, and the Reminders privacy category for the EventKit-based tool — plus the harness's own tool-invocation permission, cannot be obtained non-interactively; a headless run is expected to report this rather than retry.
- Reminders automation is implemented via a compiled EventKit-based command-line tool requiring a one-time local build step (Xcode Command Line Tools), per the decision made when scoping this feature, in preference to a simpler no-build AppleScript alternative that would not expose typed fields or the more stable cross-app identifier.
- The Scrum-specific capabilities of the source skills — the multi-project registry, the `--- scrum ---` body-block convention, and the flow-metrics CSV pipeline — are intentionally excluded from this feature; this repository's separately-vendored Scrum facilitation skill is not integrated with this feature.
- Deletion is available for notes (guarded per FR-014/FR-015) but deliberately not for reminders (FR-016): the source skills established this asymmetry deliberately — Notes has an operating-system-level "Recently Deleted" recovery path a guarded delete can rely on, while no equivalent recovery mechanism exists for a deleted reminder, so that action stays manual. This asymmetry is carried forward, not revisited, by this feature.
- The exact length of time a deleted note remains recoverable in Notes' "Recently Deleted" folder is not stated consistently across Apple's own current sources (independent verification during specification found reports ranging from 30 to 40 days). This feature's shipped documentation MUST describe the note as recoverable there for a limited, undocumented-with-precision window — never assert a specific day count as guaranteed.
- The exact property surface of the Notes AppleScript/JXA `note` and `folder` classes (id, name, body, creation date, modification date, container) is established by inspecting the live scripting dictionary in Script Editor on the operator's own machine, not by a citable Apple documentation page — Apple does not currently publish a browsable reference for this dictionary. Any documentation this feature ships MUST attribute this property list to on-device dictionary inspection, not to an external doc URL.
