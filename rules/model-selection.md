# Model Selection

**Purpose**: Choose appropriate AI model based on task complexity and requirements.

**When Applied**: Task planning, execution optimization, cost management.

---

## Model Capabilities

### Claude Haiku (Fast, Cost-Effective)

**Best For**:
- File operations (read, write, move)
- Format conversion (JSON ↔ CSV ↔ XML)
- Data validation and schema checking
- Simple transformations
- Text reformatting
- Quick searches
- Repetitive tasks

**Characteristics**:
- **Speed**: Fastest response times
- **Cost**: Lowest token cost
- **Reasoning**: Limited complex reasoning
- **Use When**: Task is straightforward and well-defined

**Examples**:
```
✅ Convert CSV to JSON
✅ Validate JSON schema
✅ Find files matching pattern
✅ Reformat code (prettier, black)
✅ Extract specific data fields
```

---

### Claude Sonnet (Balanced, Default)

**Best For**:
- Code development and modification
- Analysis and debugging
- Documentation generation
- Test writing
- Moderate complexity refactoring
- API integration
- Database queries

**Characteristics**:
- **Speed**: Moderate response times
- **Cost**: Balanced token cost
- **Reasoning**: Good for most coding tasks
- **Use When**: Standard development work

**Examples**:
```
✅ Implement feature from spec
✅ Debug failing test
✅ Write API documentation
✅ Refactor function for clarity
✅ Generate unit tests
✅ Integrate third-party API
```

---

### Claude Opus (Deep Reasoning, Premium)

**Best For**:
- Architecture decisions
- Complex algorithm design
- System design and trade-off analysis
- Security analysis
- Performance optimization
- Intricate debugging
- Research and exploration

**Characteristics**:
- **Speed**: Slower response times
- **Cost**: Highest token cost
- **Reasoning**: Deep, nuanced analysis
- **Use When**: Task requires careful consideration

**Examples**:
```
✅ Design distributed system architecture
✅ Analyze algorithm complexity trade-offs
✅ Security vulnerability assessment
✅ Optimize critical performance bottleneck
✅ Evaluate technology stack options
✅ Complex multi-step refactoring
```

---

## Decision Framework

### Quick Decision Tree

```
Is task well-defined and simple?
├─ YES → Haiku
└─ NO
   ├─ Does it require deep reasoning?
   │  ├─ YES → Opus
   │  └─ NO → Sonnet
   └─ Is it standard development work?
      └─ YES → Sonnet
```

### By Task Type

**Haiku Tasks**:
- File I/O operations
- Data format conversions
- Simple validations
- Text processing
- Search and filter
- Formatting

**Sonnet Tasks**:
- Feature implementation
- Bug fixing
- Test writing
- Documentation
- Code review
- Moderate refactoring

**Opus Tasks**:
- Architecture design
- Algorithm optimization
- Security analysis
- Complex debugging
- System design
- Critical decisions

---

## Task Decomposition

**For complex work, break into subtasks with appropriate models**:

### Example: Implement New Feature

```
Task: Add user authentication with OAuth 2.0

Decomposition:

1. [Opus] Design authentication architecture
   - Evaluate OAuth flow options
   - Analyze security implications
   - Plan token management strategy
   
2. [Sonnet] Implement OAuth integration
   - Write authentication middleware
   - Integrate with provider
   - Handle token refresh
   
3. [Sonnet] Add authentication tests
   - Unit tests for auth logic
   - Integration tests for flows
   - Mock external OAuth provider
   
4. [Haiku] Validate configuration
   - Check environment variables
   - Validate OAuth settings
   - Format configuration files
   
5. [Sonnet] Write documentation
   - API documentation
   - Setup instructions
   - Usage examples
```

### Example: Debug Production Issue

```
Task: Investigate intermittent database timeout

Decomposition:

1. [Haiku] Gather logs and metrics
   - Extract relevant log entries
   - Filter by time window
   - Format for analysis
   
2. [Sonnet] Analyze patterns
   - Identify timeout patterns
   - Check query execution times
   - Review connection pool usage
   
3. [Opus] Determine root cause
   - Evaluate hypotheses
   - Analyze system architecture
   - Assess scaling implications
   
4. [Sonnet] Implement fix
   - Adjust connection pooling
   - Add query optimization
   - Update error handling
   
5. [Haiku] Validate fix
   - Run existing tests
   - Verify configuration
   - Check log output
```

---

## Parallel Execution

**Different models can work simultaneously on independent subtasks**:

```
Parallel Tasks Example:

[Opus] (in background)
└─ Design caching architecture for new feature

[Sonnet] (main thread)  
├─ Implement API endpoints
├─ Write integration tests
└─ Update documentation

[Haiku] (quick tasks)
├─ Validate input schemas
├─ Format configuration files
└─ Generate OpenAPI spec
```

**Benefit**: Opus can handle deep thinking while Sonnet/Haiku handle implementation.

---

## Cost Optimization

### Token Usage by Model

**Approximate relative costs**:
```
Haiku:   1x (baseline)
Sonnet:  3x
Opus:    15x
```

**Optimize by matching model to task complexity**.

### Example Cost Comparison

```
Task: Process 100 files with validation and transformation

All Opus:
- 100 files × Opus cost × task time
- Total: ~15x baseline cost
- Time: Slow (deep reasoning unnecessary)

Optimized:
- [Opus] Design validation rules (1 task)
- [Sonnet] Implement transformation logic (1 task)
- [Haiku] Process all 100 files (100 tasks)
- Total: ~2x baseline cost
- Time: Fast (parallel Haiku execution)

Savings: 87% cost reduction
```

---

## Model Selection Examples

### Example 1: API Development

```
Task: Build REST API for user management

[Opus] API design
- Evaluate RESTful vs GraphQL
- Design authentication strategy
- Plan rate limiting approach

[Sonnet] Implementation
- Implement endpoints
- Write middleware
- Add validation logic
- Create tests

[Haiku] Supporting tasks
- Generate OpenAPI specification
- Validate request schemas
- Format response examples
- Check configuration files
```

### Example 2: Database Migration

```
Task: Migrate from PostgreSQL to DynamoDB

[Opus] Migration strategy
- Analyze data access patterns
- Design DynamoDB schema
- Plan migration steps
- Assess risks

[Sonnet] Implementation
- Write migration scripts
- Implement data transformers
- Create rollback plan
- Add monitoring

[Haiku] Execution
- Validate source data
- Run transformations
- Verify migrations
- Check data integrity
```

### Example 3: Bug Fix

```
Simple bug (clear cause):
[Sonnet] Identify and fix bug
[Haiku] Validate fix

Complex bug (unclear cause):
[Haiku] Gather logs and data
[Sonnet] Analyze patterns
[Opus] Determine root cause
[Sonnet] Implement fix
[Haiku] Validate fix
```

---

## Anti-Patterns

### ❌ Don't: Use Opus for Simple Tasks

```
Bad:
[Opus] Format JSON file
[Opus] Rename variables
[Opus] Run tests

Problem: Wasteful, slow, expensive
```

### ❌ Don't: Use Haiku for Complex Decisions

```
Bad:
[Haiku] Design system architecture
[Haiku] Evaluate security implications
[Haiku] Analyze algorithm trade-offs

Problem: Insufficient reasoning capability
```

### ❌ Don't: Use One Model for Everything

```
Bad:
All tasks → Sonnet only

Problem: Overpay for simple tasks, underperform on complex ones

Good:
Simple → Haiku
Standard → Sonnet  
Complex → Opus
```

---

## Best Practices

### ✅ Match Model to Task Complexity

**Consider**:
- Reasoning depth required
- Time sensitivity
- Cost constraints
- Accuracy requirements

### ✅ Plan Before Executing

**Create task list with model assignments**:

```
1. [Opus] Design authentication system
2. [Sonnet] Implement auth middleware (depends on #1)
3. [Sonnet] Write tests (depends on #2)
4. [Haiku] Validate config (depends on #2)
5. [Sonnet] Document API (depends on #2)
```

### ✅ Use Parallel Execution

**Independent tasks can run simultaneously**:

```
Parallel:
- [Opus] Design database schema (background)
- [Sonnet] Implement API endpoints (main)
- [Haiku] Generate API docs (quick)
```

### ✅ Optimize for Cost When Appropriate

**For high-volume tasks**:
- Use Haiku where possible
- Reserve Opus for critical decisions
- Use Sonnet as default

---

## Checklist

**Before starting work**:

```
[ ] Task complexity assessed
[ ] Model selected per task
[ ] Dependencies identified
[ ] Parallel execution opportunities noted
[ ] Cost implications considered
```

**During execution**:

```
[ ] Using appropriate model for current task
[ ] Not over-engineering with Opus
[ ] Not under-resourcing with Haiku
[ ] Monitoring token usage
```

---

## Summary

**Quick Guide**:

| Model | Speed | Cost | Use For |
|-------|-------|------|---------|
| Haiku | Fast | Low | File ops, validation, simple tasks |
| Sonnet | Medium | Medium | Development, debugging, documentation |
| Opus | Slow | High | Architecture, complex analysis, critical decisions |

**Default**: Start with Sonnet, adjust as needed.

**Optimization**: Break complex work into subtasks with appropriate models.

---

**Last Updated**: 2025-02-07
