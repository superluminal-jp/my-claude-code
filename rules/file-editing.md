# File Editing Strategy

**Purpose**: Efficient, reviewable file modifications for large codebases.

**When Applied**: All file editing tasks, especially files >100 lines.

---

## Core Principle

**Change only what needs to change.**

When modifying a 500-line file to update one function, the edit should affect only that function and necessary context (e.g., imports), not rewrite all 500 lines.

---

## Surgical, Targeted Changes

### When to Use

- Modifying specific functions or sections
- Updating configuration values
- Fixing bugs in known locations  
- Adding/removing specific code blocks
- Small, focused changes in large files

### Benefits

**Token Efficiency**:
- Only changed content in context
- 70-90% token reduction vs full rewrite
- Faster execution

**Code Quality**:
- Clear, reviewable diffs
- Preserves surrounding context
- Reduces risk of unintended changes
- Easier code review

**Example**:

```
Task: Add validation parameter to process_data function
File: 500 lines

Targeted Edit:
- Lines changed: ~15 (function def + calls)
- Tokens: ~500
- Review time: 30 seconds

Full Rewrite:
- Lines changed: 500
- Tokens: ~15,000
- Review time: 10 minutes
```

### Implementation

**Provide sufficient context**:
- Include enough surrounding code to uniquely identify location
- Maintain proper indentation
- Preserve existing code structure
- Use distinctive patterns (function names, comments)

**Example Intent**:

```typescript
Task: Add validation parameter to process_data function

Target: Only the function definition and its usage
Preserve: All other code unchanged
Include: Necessary import statements if adding new validators

// Before
function processData(input: string): Result {
  return transform(input);
}

// After  
function processData(input: string, validate: boolean = true): Result {
  if (validate) validateInput(input);
  return transform(input);
}
```

---

## Full File Rewrite

### When Appropriate

- **Complete restructuring**: Major refactor affecting >50% of file
- **Reformatting entire file**: Style changes throughout
- **Initial file creation**: New file from scratch
- **Short files**: File is <100 lines total
- **Fundamental architecture**: Changing core structure

### When to Avoid

❌ **Don't rewrite entire file for**:
- Single function modifications
- Adding one import statement
- Updating a few variables
- Bug fixes in specific sections
- Configuration value changes

**Why**: Wasteful, hard to review, error-prone, slow.

---

## Multi-Section Edits

### Strategy

**For multiple changes in same file, apply changes incrementally**:

#### 1. Identify All Changes

```
List each modification:
- Add import for validator module
- Update function signature  
- Add validation logic
- Update function calls

Group related changes:
- Imports together
- Function modifications together
- Call sites together

Order logically:
- Top to bottom of file
- Dependencies first
```

#### 2. Apply Changes Sequentially

```
Step 1: Add import for validator module
  Location: Top of file with other imports
  Preserve: Existing import order
  Verify: File still compiles

Step 2: Update function signature
  Location: process_data function definition
  Preserve: Function body initially
  Verify: Type checking passes

Step 3: Add validation logic
  Location: Beginning of function body
  Preserve: Existing processing logic
  Verify: Tests pass

Step 4: Update function calls
  Location: Each caller of process_data
  Preserve: Surrounding code
  Verify: Integration tests pass
```

#### 3. Verify Each Change

- Run relevant tests after each edit
- Ensure compilation/type checking passes
- Validate expected behavior
- Move to next section only after verification

### Example Workflow

```
Task: Add validation to data processing pipeline
File: src/data_processor.py (600 lines)

❌ Inefficient Approach:
1. Read entire 600-line file
2. Rewrite entire file with changes
3. Result: 600 lines in diff, hard to review
4. Risk: Unintended changes to unrelated code
5. Tokens: ~18,000

✅ Efficient Approach:
1. Identify exact changes needed:
   - Add import: line ~15
   - Update function: lines ~150-160
   - Update callers: lines ~300, ~450

2. Make targeted edits:
   - Edit 1: Add validator import
   - Edit 2: Modify process_data function
   - Edit 3: Update first caller
   - Edit 4: Update second caller

3. Result: ~30 lines total in diff
4. Benefit: Easy to review, low risk
5. Tokens: ~900 (95% reduction)
```

---

## Decision Tree

```
Need to modify file?
│
├─ File < 100 lines?
│  └─ YES → Either approach acceptable (slight preference for targeted)
│
└─ File ≥ 100 lines?
   │
   ├─ Complete restructure needed (>50% changing)?
   │  └─ YES → Full rewrite appropriate
   │
   ├─ Multiple specific sections need changes?
   │  └─ YES → Incremental, targeted edits
   │     │
   │     ├─ Changes in 2-3 sections?
   │     │  └─ Apply 2-3 sequential edits
   │     │
   │     └─ Changes in 4+ sections?
   │        └─ Consider if restructure might be better
   │           If not, apply sequential edits
   │
   └─ Single section/function needs change?
      └─ YES → Surgical, targeted edit
```

---

## Tool-Agnostic Principles

**This strategy works across all AI coding tools**:

- **Claude Code**: Uses `str_replace` command with old_str/new_str
- **Cursor**: Provides high context to apply model
- **Aider**: Uses EditBlock or search/replace formats
- **GitHub Copilot**: Agent mode understands targeted edits

**Each tool implements differently, but the principle is universal**:
Make surgical edits that change only what needs changing.

---

## Anti-Patterns

### ❌ Bad Practice: Rewrite on Minor Change

```
Task: Fix typo in comment
File: 800 lines

❌ Don't:
- Read entire file
- Rewrite entire file with typo fixed
- Result: 800-line diff for 1-word change

✅ Do:
- Target the specific comment
- Change only that line
- Result: 1-line diff
```

### ❌ Bad Practice: Change Unrelated Code

```
Task: Add error handling to function

❌ Don't:
- Also refactor variable names
- Also reorganize imports
- Also fix unrelated bugs
- Result: Mixed concerns, hard to review

✅ Do:
- Add error handling only
- Keep other changes for separate commits
- Result: Focused, reviewable change
```

### ❌ Bad Practice: Insufficient Context

```
Task: Update function call

❌ Don't provide:
result = processData(input)

Problem: Multiple calls might match

✅ Do provide:
async function loadUserData(userId: string) {
  const input = await fetchData(userId);
  const result = processData(input);  // ← This specific call
  return result;
}

Benefit: Unique identification, no ambiguity
```

---

## Best Practices

### ✅ Provide Unique Context

**Include distinctive surrounding code**:

```typescript
// Good: Unique identifiers
function processData(input: string): Result {
  // Step 1: Validate input
  if (!input) throw new Error('Invalid input');
  
  // Step 2: Transform data  ← Distinctive comment
  const transformed = transform(input);
  
  return transformed;
}
```

### ✅ Maintain File Structure

**Preserve**:
- Indentation levels
- Spacing patterns
- Comment styles
- Import organization
- Code grouping

### ✅ Test After Each Edit

**For multi-edit workflows**:

```bash
# After each targeted edit
npm test -- affected-tests
npm run type-check
```

**Catch issues early**, not after all edits complete.

### ✅ Use Clear Edit Descriptions

**Explain what and why**:

```
Good:
"Add validation parameter to processData function to support 
optional schema checking. Defaults to true for backward compatibility."

Bad:
"Update function"
```

---

## Performance Impact

### Token Usage Comparison

```
Scenario: Update 1 function in 500-line file

Full Rewrite:
- Read: ~15,000 tokens
- Write: ~15,000 tokens
- Total: ~30,000 tokens

Targeted Edit:
- Read: ~500 tokens (function + context)
- Write: ~500 tokens
- Total: ~1,000 tokens

Savings: 97% reduction
```

### Execution Speed

```
Full Rewrite:
- Generation time: 30-60 seconds
- Review time: 5-10 minutes

Targeted Edit:
- Generation time: 5-10 seconds
- Review time: 30-60 seconds

Time saved: ~90%
```

---

## Checklist

**Before editing file >100 lines**:

```
[ ] Identified exact sections needing changes
[ ] Determined if targeted edit is appropriate
[ ] Planned sequence for multi-section edits
[ ] Prepared sufficient context for unique identification
[ ] Ready to test after each edit
```

**If any uncertainty**:
- Default to targeted edits
- Test incrementally
- Keep changes focused

---

## Summary

**Key Principle**: Change only what needs to change.

**Default Strategy**: Targeted edits for files >100 lines.

**Exception**: Full rewrite when >50% of file affected.

**Multi-Edit**: Apply changes sequentially, test between edits.

**Result**: Faster, clearer, more reviewable code changes.

---

**Last Updated**: 2025-02-07
