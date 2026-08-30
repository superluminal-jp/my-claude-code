#!/usr/bin/osascript -l JavaScript
//
// Ensure one direct child folder exists -- in the Notes default account, or,
// with --parent-id, inside another folder.
//
//   osascript -l JavaScript ensure_folder.js --name "Some Folder"
//   osascript -l JavaScript ensure_folder.js --name "Sub Folder" --parent-id "<folder id>"
//
// Exact matching makes retries idempotent. Multiple exact matches fail before
// creation because a displayed name is not an identifier and choosing one
// would silently guess. --parent-id scopes both the match and the creation to
// that folder's direct children only -- a same-named folder anywhere else in
// the account neither matches nor blocks creation. This script creates at
// most one folder and exposes no move, rename, or deletion operation, with or
// without --parent-id.
//
// The Notes AppleScript dictionary documents `folder` as containing both
// `folders` and `notes` elements, so a folder can hold subfolders the same
// way the default account does; --parent-id targets that element instead of
// the account's.

ObjC.import('stdlib');
ObjC.import('Foundation');

function run(argv) {
  const opts = parseArgs(argv);
  const app = Application('com.apple.Notes');

  try {
    ensureRunning(app);
    if (opts.parentId) {
      return JSON.stringify(ensureInParent(app, opts), null, 2);
    }
    return JSON.stringify(ensureInAccount(app, opts), null, 2);
  } catch (error) {
    return fail(describeAppleEventError(error));
  }
}

// Launches Notes.app and waits briefly for it to report itself running
// before any dictionary-specific call (folders/notes) is sent to it. A cold
// Apple Event to an app that is not yet running can fail with -600
// ("Application isn't running") even in a normal, non-headless session --
// e.g. right after login, or when Notes has not been opened in a while (see
// "Sources" in SKILL.md) -- rather than silently auto-launching the way a
// warm one usually does. `running`/`activate` are Standard Suite features
// every JXA Application object exposes, unlike the Notes-specific
// `.whose()`/`.byId()` this skill avoids elsewhere, so they are safe to rely
// on here. This cannot fix a genuinely headless environment (no GUI login
// session) -- see describeAppleEventError() for that case -- only the
// ordinary "app was not warmed up yet" case this skill's own retries cannot
// distinguish from a permission denial.
function ensureRunning(app) {
  try {
    if (app.running()) return;
  } catch (error) {
    // Fall through and try to launch anyway -- some states make `running`
    // itself throw before the app has been asked to launch even once.
  }
  app.activate();
  const deadlineMs = Date.now() + 5000;
  while (Date.now() < deadlineMs) {
    try {
      if (app.running()) return;
    } catch (error) {
      // Keep waiting; see the comment above.
    }
    $.NSThread.sleepForTimeInterval(0.2);
  }
}

// Apple Event errors carry a numeric `errorNumber` alongside `.message`.
// Mapping the codes this skill's own "Before the first call" section in
// SKILL.md already documents means a caller sees the fix, not just the raw
// number, without cross-referencing the doc by hand.
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

function ensureInAccount(app, opts) {
  const account = app.defaultAccount;
  const accountName = account.name(); // Force the default-account specifier.
  const matches = account.folders().filter((folder) => folder.name() === opts.name);

  if (matches.length > 1) {
    fail('folder name is ambiguous in the default account: ' + opts.name);
  }
  if (matches.length === 1) {
    return describe(matches[0], accountName, false);
  }

  const folder = app.Folder({ name: opts.name });
  account.folders.push(folder);
  return describe(folder, accountName, true);
}

function ensureInParent(app, opts) {
  let parent;
  try {
    parent = app.folders.byId(opts.parentId);
    parent.name(); // Force the specifier to resolve now, not later.
  } catch (error) {
    fail('no folder with id: ' + opts.parentId);
  }

  const matches = parent.folders().filter((folder) => folder.name() === opts.name);

  if (matches.length > 1) {
    fail('folder name is ambiguous under parent ' + opts.parentId + ': ' + opts.name);
  }
  if (matches.length === 1) {
    return describe(matches[0], null, false, opts.parentId);
  }

  const folder = app.Folder({ name: opts.name });
  parent.folders.push(folder);
  return describe(folder, null, true, opts.parentId);
}

function parseArgs(argv) {
  const opts = { name: null, parentId: null };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--name') {
      i += 1;
      if (i >= argv.length) fail('--name needs a value');
      opts.name = argv[i];
    } else if (arg === '--parent-id') {
      i += 1;
      if (i >= argv.length) fail('--parent-id needs a value');
      opts.parentId = argv[i];
    } else {
      fail('unknown option or positional argument: ' + arg);
    }
  }
  if (opts.name === null) fail('--name is required');
  const name = String(opts.name).trim();
  if (name.length === 0) fail('--name must be non-empty');
  opts.name = name;
  return opts;
}

function describe(folder, accountName, created, parentId) {
  const result = {
    id: folder.id(),
    name: folder.name(),
    created: created,
  };
  if (parentId) {
    result.parent = parentId;
  } else {
    result.account = accountName;
  }
  return result;
}

function fail(message) {
  const text = $.NSString.alloc.initWithUTF8String('ensure_folder: ' + message + '\n');
  $.NSFileHandle.fileHandleWithStandardError.writeData(
    text.dataUsingEncoding($.NSUTF8StringEncoding)
  );
  $.exit(1);
}
