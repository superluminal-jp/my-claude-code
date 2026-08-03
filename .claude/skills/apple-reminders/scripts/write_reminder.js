#!/usr/bin/osascript -l JavaScript
//
// Create or update one reminder. Prints the resulting reminder as JSON.
//
//   # create
//   osascript -l JavaScript write_reminder.js --list "Sprint Backlog" \
//     --name "Ship the login form" --due 2026-08-08
//
//   # update: body comes from stdin, because a scrum block spans lines
//   python3 scrum_block.py set --started today < old_body \
//     | osascript -l JavaScript write_reminder.js --id "<id>" --body-stdin
//
//   # complete / reopen
//   osascript -l JavaScript write_reminder.js --id "<id>" --complete
//
// Two rules this script enforces structurally rather than by convention:
//
//   1. **No delete.** Removing a reminder destroys the only record of its
//      Cycle Time, and no guardrail hook can recognise a destructive Apple
//      Event. Deletion stays a human action in Reminders.app.
//   2. **--id means update, never create.** An unresolvable id fails rather
//      than falling back to creating something, so a typo cannot silently
//      fork the backlog into a duplicate item.
//
// `completion date` is written by Reminders.app itself when `completed` flips
// to true; this script never sets it, so the completion timestamp always comes
// from the app rather than from whatever clock this process happened to see.

ObjC.import('stdlib');
ObjC.import('Foundation');

function run(argv) {
  const opts = parseArgs(argv);
  const app = Application('Reminders');

  try {
    const reminder = opts.id ? update(app, opts) : create(app, opts);
    return JSON.stringify(describe(reminder), null, 2);
  } catch (error) {
    return fail(error.message);
  }
}

function parseArgs(argv) {
  const opts = {
    id: null,
    list: null,
    name: null,
    body: null,
    due: null,
    remindMe: null,
    priority: null,
    completed: null,
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--id') opts.id = argv[++i];
    else if (arg === '--list') opts.list = argv[++i];
    else if (arg === '--name') opts.name = argv[++i];
    else if (arg === '--body') opts.body = argv[++i];
    else if (arg === '--body-stdin') opts.body = readStdin();
    else if (arg === '--due') opts.due = argv[++i];
    else if (arg === '--remind-me') opts.remindMe = argv[++i];
    else if (arg === '--priority') opts.priority = parseInt(argv[++i], 10);
    else if (arg === '--complete') opts.completed = true;
    else if (arg === '--uncomplete') opts.completed = false;
    else fail('unknown option: ' + arg);
  }
  if (!opts.id && !opts.list) fail('--list is required when creating (--id updates)');
  if (!opts.id && !opts.name) fail('--name is required when creating');
  return opts;
}

function create(app, opts) {
  const lists = app.lists.whose({ name: opts.list });
  if (lists.length === 0) fail('no such list: ' + opts.list);

  const props = { name: opts.name };
  if (opts.body !== null) props.body = opts.body;
  if (opts.due !== null) props.dueDate = parseDate(opts.due, '--due');
  if (opts.remindMe !== null) props.remindMeDate = parseDate(opts.remindMe, '--remind-me');
  if (opts.priority !== null) props.priority = opts.priority;

  const reminder = app.Reminder(props);
  lists[0].reminders.push(reminder);
  return reminder;
}

function update(app, opts) {
  let reminder;
  try {
    reminder = app.reminders.byId(opts.id);
    reminder.name(); // Resolve now: a bad id must fail here, not silently later.
  } catch (error) {
    fail('no reminder with id: ' + opts.id);
  }

  if (opts.name !== null) reminder.name = opts.name;
  if (opts.body !== null) reminder.body = opts.body;
  if (opts.due !== null) reminder.dueDate = parseDate(opts.due, '--due');
  if (opts.remindMe !== null) reminder.remindMeDate = parseDate(opts.remindMe, '--remind-me');
  if (opts.priority !== null) reminder.priority = opts.priority;
  if (opts.completed !== null) reminder.completed = opts.completed;
  return reminder;
}

function describe(reminder) {
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

// ISO 8601 in, so the caller never has to guess this machine's date format.
function parseDate(value, flag) {
  const parsed = new Date(value);
  if (isNaN(parsed.getTime())) fail(flag + ' is not a parsable date: ' + value);
  return parsed;
}

function normalize(value) {
  if (value === null || value === undefined) return null;
  if (value instanceof Date) return value.toISOString();
  return value;
}

function readStdin() {
  const data = $.NSFileHandle.fileHandleWithStandardInput.readDataToEndOfFile;
  return ObjC.unwrap($.NSString.alloc.initWithDataEncoding(data, $.NSUTF8StringEncoding));
}

function fail(message) {
  const text = $.NSString.alloc.initWithUTF8String('write_reminder: ' + message + '\n');
  $.NSFileHandle.fileHandleWithStandardError.writeData(
    text.dataUsingEncoding($.NSUTF8StringEncoding)
  );
  $.exit(1);
}
