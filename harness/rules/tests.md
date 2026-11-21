---
paths:
  - "**/test_*.py"
  - "**/*_test.{py,go}"
  - "**/*.{test,spec}.{ts,tsx,js,jsx,mts,cts}"
  - "**/{tests,test,__tests__}/**"
---

# Tests

- A test states a behavior someone relies on. Name it after that behavior (`rejects_login_with_wrong_password`) and assert on what a caller can observe: a return value, an output, a state change, a call across a boundary.
- See a new test fail for the reason it is meant to catch before making it pass. A test that has never failed has not been shown to check anything.
- Keep one behavior per test, with its setup visible in the test or in a clearly named helper.
- Make tests deterministic: control the clock, random seeds, and ordering, and replace the network and other external services at the boundary. Use real collaborators inside that boundary, since heavy mocking tests the mocks.
- Write files only under a temporary directory the test framework provides, and leave nothing behind.
- When a test fails, find out whether the code or the test is wrong. Skipping it, loosening its assertion, or deleting it needs the person's agreement that the test itself is wrong.
- Cover the failure paths and edge values of what changed (empty, missing, boundary, malformed), not only the expected path.
