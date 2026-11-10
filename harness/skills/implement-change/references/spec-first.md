# Specification first

Read when the change adds or alters observable behavior. A trivial internal refactor needs no specification; the failing check alone is enough.

The specification is the single source of truth for what a feature does and why. Code satisfies the specification; documents describe the current code.

- Write or update the specification before the implementation.
- Keep it to what and why. Technology and framework choices stay out of it.
- Make every acceptance criterion verifiable: Given/When/Then, or a measurable criterion with an identifier. If a failing test cannot be written from the specification, it is still ambiguous: clarify before coding.
- When the implementation and the specification diverge, fix the implementation. When the specification itself is wrong, stop and tell the person. Never edit a specification to match broken code.
- When implementation reveals a gap in the specification, record the gap and ask before filling it.

The specification names the behavior, the test enforces it, and the implementation satisfies both.

## Projects that use Spec Kit

When the project already uses [github/spec-kit](https://github.com/github/spec-kit), follow its installed lifecycle (specification, planning, tasks, consistency analysis, implementation) as it is; do not improvise a shorter substitute.

One exception: when the change also has a requirements graph whose acceptance criteria a checker gates, that graph is the only source of the acceptance criteria. `spec.md` then cites the graph's acceptance identifiers instead of restating them. Every other step of the lifecycle stays.

## Sources

- Spec-driven development with GitHub Spec Kit: <https://github.com/github/spec-kit>
- Kent Beck, *Test-Driven Development: By Example*, Addison-Wesley, 2002.
