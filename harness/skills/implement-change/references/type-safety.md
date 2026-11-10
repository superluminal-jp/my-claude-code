# Type safety

Read when the language supports static or gradual typing (TypeScript, Python with type hints, Go, Rust, Swift, Kotlin, Java, C#, and the like). Match the repository's existing typing convention: do not introduce a new typing system, annotate untouched code, or refactor types beyond the task.

- **Annotate public interfaces.** New or changed public functions, exported values, and class members carry explicit annotations in the project's convention. When a change alters a typed interface's inputs or outputs, update the annotations in the same change.
- **No unsafe escape by default.** When the type checker reports an error, fix the mismatch by narrowing, correct typing, or a small refactor. Do not reach for `any`, a blanket cast, a suppression comment (`# type: ignore`, `@ts-ignore`), or a non-null assertion. When an escape is unavoidable, for example an untyped third-party library, add one line saying why and tell the person about the trade-off.
- **Verify, do not only annotate.** When the project has a configured type checker (`tsc`, `mypy`, `pyright`, and the like), run it with the other checks and resolve every error the change introduced. A project without one is unaffected; do not invent the step.
- **Validate at boundaries.** Data that enters typed code from outside the type system's guarantee (user input, external API responses, deserialized payloads, environment and configuration values) is validated or narrowed into the expected type at the boundary. Already-typed internal data needs no second validation.
