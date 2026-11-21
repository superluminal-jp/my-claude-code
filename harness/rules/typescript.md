---
paths:
  - "**/*.{ts,tsx,mts,cts}"
  - "**/tsconfig*.json"
---

# TypeScript

The project's own configuration decides: use the package manager its lockfile belongs to, and the compiler options, linter, formatter, and test runner it already has. The points below apply where the project is silent.

- Keep `strict` on and leave compiler options as they are; fix a type error in the code rather than loosening the option that reports it.
- Type a value of unknown shape as `unknown` and narrow it. `any`, `as` casts, and `!` assertions turn the checker off for that value, so keep each one to a place where the type is proven another way and say how in a comment.
- Parse data at the boundary (HTTP responses, form input, `JSON.parse`, environment variables) with the project's schema library or a type guard; a type annotation alone does not check anything at run time.
- Model alternatives as a discriminated union and handle every member, with a `never` check in the default branch so a new member is a compile error.
- Await or return every promise. Handle an error where something can be done about it, and narrow the caught value before reading its properties.
- In React, keep derived values out of state, give every list item a stable key, and list every value an effect reads in its dependency array.
