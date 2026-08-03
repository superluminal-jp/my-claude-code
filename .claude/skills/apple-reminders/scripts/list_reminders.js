#!/usr/bin/osascript -l JavaScript
//
// Read reminders out of Reminders.app as JSON, one object per reminder.
//
//   osascript -l JavaScript list_reminders.js "Sprint Backlog"
//   osascript -l JavaScript list_reminders.js "Sprint Backlog" --open-only
//   osascript -l JavaScript list_reminders.js --id "x-apple-reminder://UUID"
//   osascript -l JavaScript list_reminders.js --id "<id>" --field body
//   osascript -l JavaScript list_reminders.js --lists
//
// JXA rather than AppleScript for exactly one reason: JSON.stringify. The
// scripting dictionary is the same either way, but AppleScript's record output
// would need parsing on the way out, and the parsing layer is Python
// (scrum_block.py) -- which is where it can be unit-tested.
//
// Only the properties the Reminders dictionary publishes are read. Tags,
// subtasks, and sections are absent from every public Apple automation surface
// and are not reachable from here; the scrum block in `body` stands in for them.
//
// Emits JSON on stdout. On failure, a message on stderr and exit 1 -- so a
// missing list or a denied automation permission is distinguishable from an
// empty list, which is a valid `[]`.

function run(argv) {
  const opts = parseArgs(argv);
  const app = Application('Reminders');

  try {
    if (opts.lists) {
      return JSON.stringify(app.lists.name(), null, 2);
    }

    const items = opts.id ? [byId(app, opts.id)] : fromList(app, opts.list, opts.openOnly);

    if (opts.field) {
      // Raw single field, unquoted, for piping into scrum_block.py set.
      return items.map((item) => (item[opts.field] === null ? '' : String(item[opts.field]))).join('\n');
    }
    return JSON.stringify(items, null, 2);
  } catch (error) {
    return fail(error.message);
  }
}

function parseArgs(argv) {
  const opts = { list: null, id: null, field: null, openOnly: false, lists: false };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--id') opts.id = argv[++i];
    else if (arg === '--field') opts.field = argv[++i];
    else if (arg === '--open-only') opts.openOnly = true;
    else if (arg === '--lists') opts.lists = true;
    else if (arg.indexOf('--') === 0) fail('unknown option: ' + arg);
    else opts.list = arg;
  }
  if (!opts.lists && !opts.id && !opts.list) {
    fail('usage: list_reminders.js <list name> | --id <reminder id> | --lists');
  }
  return opts;
}

// Bulk property reads: one Apple Event per property for the whole list rather
// than one per reminder per property. On a list of any size the difference is
// the whole runtime of this script.
function fromList(app, listName, openOnly) {
  const lists = app.lists.whose({ name: listName });
  if (lists.length === 0) fail('no such list: ' + listName);

  const reminders = lists[0].reminders;
  const columns = {
    id: reminders.id(),
    name: reminders.name(),
    body: reminders.body(),
    completed: reminders.completed(),
    completionDate: reminders.completionDate(),
    creationDate: reminders.creationDate(),
    modificationDate: reminders.modificationDate(),
    dueDate: reminders.dueDate(),
    remindMeDate: reminders.remindMeDate(),
    priority: reminders.priority(),
  };

  const items = [];
  for (let i = 0; i < columns.id.length; i++) {
    if (openOnly && columns.completed[i]) continue;
    const item = { list: listName };
    Object.keys(columns).forEach((key) => {
      item[key] = normalize(columns[key][i]);
    });
    items.push(item);
  }
  return items;
}

// The link resolver: an id is what both the scrum block's `note:` key and the
// note-side `[[reminder:...]]` marker store, so "open what this points at"
// bottoms out here.
function byId(app, id) {
  let reminder;
  try {
    reminder = app.reminders.byId(id);
    reminder.name(); // Force the specifier to resolve now, not later.
  } catch (error) {
    fail('no reminder with id: ' + id);
  }
  return {
    id: normalize(reminder.id()),
    name: normalize(reminder.name()),
    body: normalize(reminder.body()),
    completed: normalize(reminder.completed()),
    completionDate: normalize(reminder.completionDate()),
    creationDate: normalize(reminder.creationDate()),
    modificationDate: normalize(reminder.modificationDate()),
    dueDate: normalize(reminder.dueDate()),
    remindMeDate: normalize(reminder.remindMeDate()),
    priority: normalize(reminder.priority()),
    list: normalize(reminder.container.name()),
  };
}

// Dates go out as ISO 8601 strings; scrum_block.py truncates them to days.
// `missing value` arrives as null or undefined depending on the property.
function normalize(value) {
  if (value === null || value === undefined) return null;
  if (value instanceof Date) return value.toISOString();
  return value;
}

// stderr + exit 1, so a caller can tell "list not found" or "automation denied"
// apart from "the list is empty", which is a successful `[]`.
ObjC.import('stdlib');
ObjC.import('Foundation');

function fail(message) {
  const text = $.NSString.alloc.initWithUTF8String('list_reminders: ' + message + '\n');
  $.NSFileHandle.fileHandleWithStandardError.writeData(
    text.dataUsingEncoding($.NSUTF8StringEncoding)
  );
  $.exit(1);
}
