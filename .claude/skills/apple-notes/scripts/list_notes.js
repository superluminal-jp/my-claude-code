#!/usr/bin/osascript -l JavaScript
//
// Read notes out of Notes.app as JSON, one object per note.
//
//   osascript -l JavaScript list_notes.js "Some Folder"
//   osascript -l JavaScript list_notes.js "Some Folder" --with-body
//   osascript -l JavaScript list_notes.js --id "x-coredata://ABC/ICNote/p42" --with-body
//   osascript -l JavaScript list_notes.js --id "<id>" --field body
//   osascript -l JavaScript list_notes.js --folders
//
// Bodies are omitted unless asked for. A note body is full HTML, and a folder
// of notes dumped in one call is a wall of markup nobody reads -- list first,
// fetch the one body that matters second.
//
// Notes has no EventKit-equivalent framework: AppleScript (here, via JXA for
// JSON output) is the only supported programmatic route, and it is macOS-only.
// There is no iOS path at all.

ObjC.import('stdlib');
ObjC.import('Foundation');

function run(argv) {
  const opts = parseArgs(argv);
  const app = Application('com.apple.Notes');

  try {
    ensureRunning(app);
    if (opts.folders) {
      return JSON.stringify(app.folders.name(), null, 2);
    }

    const items = opts.id ? [byId(app, opts)] : fromFolder(app, opts);

    if (opts.field) {
      return items.map((item) => (item[opts.field] == null ? '' : String(item[opts.field]))).join('\n');
    }
    return JSON.stringify(items, null, 2);
  } catch (error) {
    return fail(describeAppleEventError(error));
  }
}

// Duplicated verbatim from ensure_folder.js -- see that copy's comment for
// why a cold Apple Event needs this before any Notes-specific dictionary
// call, and "Sources" in SKILL.md.
function ensureRunning(app) {
  try {
    if (app.running()) return;
  } catch (error) {
    // Fall through and try to launch anyway.
  }
  app.activate();
  const deadlineMs = Date.now() + 5000;
  while (Date.now() < deadlineMs) {
    try {
      if (app.running()) return;
    } catch (error) {
      // Keep waiting.
    }
    $.NSThread.sleepForTimeInterval(0.2);
  }
}

// Duplicated verbatim from ensure_folder.js -- see that copy's comment.
function describeAppleEventError(error) {
  const code = error && typeof error.errorNumber === 'number' ? error.errorNumber : null;
  const hints = {
    '-600': 'Notes.app could not be launched -- this requires an active GUI (Aqua) login session; it cannot run over SSH or from a background/headless process.',
    '-1743': 'Automation permission for Notes was denied -- see SKILL.md "Before the first call".',
    '-10004': 'Automation permission for Notes was denied -- see SKILL.md "Before the first call".',
    '-10827': 'Automation permission for Notes was denied -- see SKILL.md "Before the first call".',
  };
  const hint = code !== null ? hints[String(code)] : null;
  return hint ? error.message + ' -- ' + hint : error.message;
}

function parseArgs(argv) {
  const opts = { folder: null, id: null, field: null, withBody: false, plaintext: false, folders: false };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--id') opts.id = argv[++i];
    else if (arg === '--field') { opts.field = argv[++i]; opts.withBody = true; }
    else if (arg === '--with-body') opts.withBody = true;
    else if (arg === '--plaintext') { opts.plaintext = true; opts.withBody = true; }
    else if (arg === '--folders') opts.folders = true;
    else if (arg.indexOf('--') === 0) fail('unknown option: ' + arg);
    else opts.folder = arg;
  }
  if (!opts.folders && !opts.id && !opts.folder) {
    fail('usage: list_notes.js <folder name> | --id <note id> | --folders');
  }
  return opts;
}

// Bulk property reads: one Apple Event per property for the whole folder.
//
// Folder lookup fetches the whole collection and filters in JavaScript
// rather than using `.whose({ name })` -- Notes.app's scripting dictionary
// has been reported unreliable for JXA's `.whose()` filter (it is not a
// general JXA defect: single positive-condition `.whose()` clauses are
// documented to work against better-behaved apps' dictionaries). Fetch-and-
// filter is exactly the approach SKILL.md already documents ("There is no
// query language. Filtering a folder means fetching it and filtering in the
// caller.") and what ensure_folder.js already does for the same reason --
// see "Sources" in SKILL.md.
function fromFolder(app, opts) {
  const folders = app.folders().filter((folder) => folder.name() === opts.folder);
  if (folders.length === 0) fail('no such folder: ' + opts.folder);

  const notes = folders[0].notes;
  const columns = {
    id: notes.id(),
    name: notes.name(),
    creationDate: notes.creationDate(),
    modificationDate: notes.modificationDate(),
  };
  if (opts.withBody) columns.body = notes.body();

  const items = [];
  for (let i = 0; i < columns.id.length; i++) {
    const item = { folder: opts.folder };
    Object.keys(columns).forEach((key) => {
      item[key] = normalize(columns[key][i]);
    });
    if (opts.plaintext) item.plaintext = toPlainText(item.body);
    items.push(item);
  }
  return items;
}

function byId(app, opts) {
  const note = findNoteById(app, opts.id);
  const folderName = folderNameForId(app, opts.id);

  const item = {
    id: normalize(note.id()),
    name: normalize(note.name()),
    creationDate: normalize(note.creationDate()),
    modificationDate: normalize(note.modificationDate()),
    folder: normalize(folderName),
  };
  if (opts.withBody) item.body = normalize(note.body());
  if (opts.plaintext) item.plaintext = toPlainText(item.body);
  return item;
}

// Looks up a note by id via a bulk id fetch + positional specifier instead of
// `app.notes.byId(id)` -- the same Notes.app scripting-reliability reasoning
// as fromFolder()'s filter above applies to `.byId()` too, and this is one
// Apple Event, not per-folder iteration. See "Sources" in SKILL.md.
function findNoteById(app, noteId) {
  const ids = app.notes.id();
  const index = ids.indexOf(noteId);
  if (index === -1) fail('no note with id: ' + noteId);
  try {
    const note = app.notes[index];
    note.name(); // Force the specifier to resolve now, not later.
    return note;
  } catch (error) {
    fail('no note with id: ' + noteId);
  }
}

// Notes documents a note's `container`, but JXA fails to resolve it for a
// valid by-id specifier. Folder membership is still available as collections
// of opaque note ids, and does not require reading unrelated titles or bodies.
function folderNameForId(app, noteId) {
  const folders = app.folders();
  let match = null;
  for (let i = 0; i < folders.length; i++) {
    if (folders[i].notes.id().indexOf(noteId) === -1) continue;
    if (match !== null) fail('note belongs to multiple folders: ' + noteId);
    match = normalize(folders[i].name());
  }
  if (match === null) fail('could not resolve folder for note: ' + noteId);
  return match;
}

// The dictionary's own `plaintext` property is not consistently documented
// across macOS versions, so this strips the markup here instead of depending
// on it. Good enough to read; never round-trip it back into a body.
function toPlainText(html) {
  if (!html) return null;
  return html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(div|p|h[1-6]|li|tr)>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, '&')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function normalize(value) {
  if (value === null || value === undefined) return null;
  if (value instanceof Date) return value.toISOString();
  return value;
}

function fail(message) {
  const text = $.NSString.alloc.initWithUTF8String('list_notes: ' + message + '\n');
  $.NSFileHandle.fileHandleWithStandardError.writeData(
    text.dataUsingEncoding($.NSUTF8StringEncoding)
  );
  $.exit(1);
}
