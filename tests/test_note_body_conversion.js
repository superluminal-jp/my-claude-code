#!/usr/bin/env node
'use strict';

const assert = require('assert/strict');
const path = require('path');

// write_note.js's top level calls ObjC.import(...) to reach the JXA/Apple
// Events bridge -- harmless to stub out under Node, since none of the pure
// conversion/validation functions under test touch it.
global.ObjC = { import() {} };

const SCRIPT = path.join(
  __dirname, '..', '.claude', 'skills', 'apple-notes', 'scripts', 'write_note.js'
);
const {
  dedupTitleLine,
  findBlock,
  firstVisibleLine,
  markdownToNotesHtml,
  openFenceHtml,
  validateNotesMarkdown,
  CLOSE_FENCE_HTML,
} = require(SCRIPT);

// Mirrors write_note.js's replaceBlock() fold logic exactly (data-model.md
// Named Block state transitions), but as a pure function of a body string --
// replaceBlock() itself needs a live Notes.app note to mutate.
function spliceBlock(body, name, innerHtml) {
  const newBlock = openFenceHtml(name) + innerHtml + CLOSE_FENCE_HTML;
  const existing = findBlock(body, name);
  return existing === null
    ? body + newBlock
    : body.slice(0, existing.start) + newBlock + body.slice(existing.end);
}

let pass = 0;
let fail = 0;
const failures = [];

function test(name, fn) {
  try {
    fn();
    pass += 1;
    console.log(`PASS ${name}`);
  } catch (error) {
    fail += 1;
    failures.push(name);
    console.log(`FAIL ${name}`);
    console.log(`     ${error.message}`);
  }
}

function rejectsFormat(input, expectedName) {
  assert.throws(
    () => validateNotesMarkdown(input),
    (error) => error instanceof Error && error.message.includes(expectedName)
  );
}

// Title behavior (contracts/notes-write.md mode1: title dedup on create()'s
// --text/--text-stdin only).
test('dedupTitleLine drops an exact-match plain first line', () => {
  assert.equal(
    dedupTitleLine('Definition of Done', 'Definition of Done\n\nBody'),
    '\nBody'
  );
});

test('dedupTitleLine drops an exact-match Markdown Title first line', () => {
  assert.equal(
    dedupTitleLine('Definition of Done', '# Definition of Done\n\nBody'),
    '\nBody'
  );
});

test('dedupTitleLine leaves a near-match untouched', () => {
  assert.equal(
    dedupTitleLine('Definition of Done', '# Definition of Done (v2)\nBody'),
    '# Definition of Done (v2)\nBody'
  );
});

test('firstVisibleLine removes supported block and inline markers', () => {
  assert.equal(
    firstVisibleLine('\n## **Sprint** ++Review++'),
    'Sprint Review'
  );
});

// Paragraph styles and inline formatting.
test('markdownToNotesHtml renders Notes paragraph styles', () => {
  assert.equal(
    markdownToNotesHtml('# Title\n## Heading\n### Subheading\nBody'),
    '<h1>Title</h1><h2>Heading</h2><h3>Subheading</h3><div>Body</div>'
  );
});

test('markdownToNotesHtml renders fenced blocks as Monostyled', () => {
  assert.equal(
    markdownToNotesHtml('```js\nconst x = <tag>;\nsecond\n```'),
    '<pre>const x = &lt;tag&gt;;\nsecond</pre>'
  );
});

test('markdownToNotesHtml renders all supported inline styles', () => {
  assert.equal(
    markdownToNotesHtml(
      'A **bold** *italic* ++under++ ~~strike~~ [paint]{color=#CC0000 size=24}.'
    ),
    '<div>A <b>bold</b> <i>italic</i> <u>under</u> <s>strike</s> ' +
      '<span style="color: #CC0000; font-size: 24px">paint</span>.</div>'
  );
});

test('markdownToNotesHtml supports nested balanced inline styles', () => {
  assert.equal(
    markdownToNotesHtml('**bold and *italic***'),
    '<div><b>bold and <i>italic</i></b></div>'
  );
});

test('markdownToNotesHtml applies alignment to one paragraph only', () => {
  assert.equal(
    markdownToNotesHtml('{align=center}Centered words\n{align=right}Right\nBody'),
    '<div style="text-align: center">Centered words</div>' +
      '<div style="text-align: right">Right</div><div>Body</div>'
  );
});

test('markdownToNotesHtml escapes raw HTML and quotes', () => {
  assert.equal(
    markdownToNotesHtml('<script>"x" & \'y\'</script>'),
    '<div>&lt;script&gt;&quot;x&quot; &amp; &#39;y&#39;&lt;/script&gt;</div>'
  );
});

test('unmatched inline markers remain readable text', () => {
  assert.equal(
    markdownToNotesHtml('before **open and ++open'),
    '<div>before **open and ++open</div>'
  );
});

// Lists.
test('Bulleted List uses * markers', () => {
  assert.equal(
    markdownToNotesHtml('* one\n* two'),
    '<ul><li>one</li><li>two</li></ul>'
  );
});

test('Numbered List uses decimal markers and preserves order', () => {
  assert.equal(
    markdownToNotesHtml('1. one\n2. two'),
    '<ol><li>one</li><li>two</li></ol>'
  );
});

test('same-level list kind changes preserve sequence', () => {
  assert.equal(
    markdownToNotesHtml('* bullet\n1. number'),
    '<ul><li>bullet</li></ul><ol><li>number</li></ol>'
  );
});

test('two-space indentation creates a nested list', () => {
  assert.equal(
    markdownToNotesHtml('* parent\n  * child\n* next'),
    '<ul><li>parent<ul><li>child</li></ul></li><li>next</li></ul>'
  );
});

test('indented unmarked text creates an item continuation', () => {
  assert.equal(
    markdownToNotesHtml('* parent\n  continuation'),
    '<ul><li>parent<br>continuation</li></ul>'
  );
});

test('item continuation before a nested list stays inside its parent item', () => {
  assert.equal(
    markdownToNotesHtml('* parent\n  continuation\n  * child\n* next'),
    '<ul><li>parent<br>continuation<ul><li>child</li></ul></li><li>next</li></ul>'
  );
});

test('item continuation after a nested list is rejected instead of creating an empty bullet', () => {
  rejectsFormat('* parent\n  * child\n  late continuation', 'List continuation');
});

test('a blank line ends list context before an indented body paragraph', () => {
  assert.equal(
    markdownToNotesHtml('* parent\n  * child\n\n  indented body'),
    '<ul><li>parent<ul><li>child</li></ul></li></ul>' +
      '<div><br></div><div>  indented body</div>'
  );
});

test('odd list indentation is rejected before conversion', () => {
  rejectsFormat(' * item', 'List indentation');
});

test('tabs in list indentation are rejected before conversion', () => {
  rejectsFormat('\t* item', 'List indentation');
});

test('list nesting deeper than level 8 is rejected', () => {
  rejectsFormat('                  * too deep', 'List nesting');
});

// Unsupported native formats and invalid allow-list attributes
// (contracts/notes-write.md mode1; spec.md edge cases).
test('Block Quote is rejected', () => rejectsFormat('> quote', 'Block Quote'));
test('Highlight is rejected', () => rejectsFormat('==highlight==', 'Highlight'));
test('Font family syntax is rejected', () => rejectsFormat('{font=Marker Felt}x', 'Font family'));
test('CSS font-family is rejected', () => rejectsFormat('font-family: serif', 'Font family'));
test('HTML font tag is rejected in plain input', () => rejectsFormat('<font face="serif">x</font>', 'Font family'));
test('Dashed List is rejected', () => rejectsFormat('- dashed', 'Dashed List'));
test('unchecked Checklist is rejected before Dashed List', () => rejectsFormat('- [ ] todo', 'Checklist'));
test('checked Checklist is rejected before Dashed List', () => rejectsFormat('- [x] done', 'Checklist'));
test('invalid color is rejected', () => rejectsFormat('[x]{color=red}', 'color'));
test('invalid size is rejected', () => rejectsFormat('[x]{size=0}', 'size'));
test('invalid alignment is rejected', () => rejectsFormat('{align=middle}x', 'alignment'));

// Named Block splice (data-model.md): create-if-absent, replace-if-single-
// match, refuse-if-ambiguous-or-malformed.
test('findBlock returns null when the block does not exist yet', () => {
  assert.equal(findBlock('<div>prose</div>', 'status'), null);
});

test('spliceBlock creates (appends) the block when absent', () => {
  assert.equal(
    spliceBlock('<div>prose</div>', 'status', '<div>in progress</div>'),
    '<div>prose</div><div>--- status ---</div><div>in progress</div><div>---</div>'
  );
});

test('spliceBlock replaces the block in place when exactly one match exists', () => {
  const body = '<div>before</div><div>--- status ---</div><div>old</div><div>---</div><div>after</div>';
  assert.equal(
    spliceBlock(body, 'status', '<div>new</div>'),
    '<div>before</div><div>--- status ---</div><div>new</div><div>---</div><div>after</div>'
  );
});

test('findBlock refuses when the same block name matches more than once', () => {
  const body =
    '<div>--- status ---</div><div>a</div><div>---</div>' +
    '<div>--- status ---</div><div>b</div><div>---</div>';
  assert.throws(() => findBlock(body, 'status'), /ambiguous/);
});

test('findBlock refuses an unterminated block rather than guessing where it ends', () => {
  const body = '<div>--- status ---</div><div>no closing fence</div>';
  assert.throws(() => findBlock(body, 'status'), /unterminated/);
});

console.log(`\n${pass} passed, ${fail} failed.`);
if (fail > 0) {
  console.log('Failing: ' + failures.join(', '));
  process.exit(1);
}
