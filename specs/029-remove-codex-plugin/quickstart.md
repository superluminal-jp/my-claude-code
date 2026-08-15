# Quickstart: Validate the codex-plugin-cc Removal

## 1. Confirm no live reference remains

```sh
grep -rniE "codex-plugin-cc|openai-codex|codex@openai-codex" . \
  --include="*.md" --include="*.sh" --include="*.json" \
  --exclude-dir=.git \
  | grep -Ev "^(\./)?docs/adr/" \
  | grep -Ev "^(\./)?specs/(0[0-2][0-8])-"
```
Expected: no output — this feature is the last remaining live reference, and
it is being deleted, not documented.

## 2. Confirm `install.sh` issues no plugin commands

```sh
bash tests/run-install.sh
```
Expected: passes. As an added spot-check, inspect the stubbed command log the
test captures — it contains no `plugin marketplace add`, `plugin marketplace
update`, or `plugin install` entry (the test itself doesn't assert this
directly, since the code path no longer exists to produce one; the absence is
implicit in a passing run with no such stub interaction).

## 3. Confirm the step-comment sequence has no gap

```sh
grep -nE '^# [0-9]' install.sh
```
Expected: `0.`, `1.`, `2.`, `3.` in order (step `1a` is a lettered sub-step of
`1` and intentionally not matched by this numeric grep); no `4.` remains.

## 4. Confirm the installer test has no dead stub branches

```sh
grep -n "plugin marketplace list\|plugin list\b" tests/run-install.sh
```
Expected: no output.

## 5. Run the full behavior-suite set

```sh
for t in tests/run-*.sh; do
  echo "== $t =="
  bash "$t" || echo "FAILED: $t"
done
```
Expected: every suite passes.

## 6. Check shell quality

```sh
bash -n install.sh tests/run-install.sh && echo "syntax OK"
shfmt -d -i 2 install.sh tests/run-install.sh
shellcheck install.sh tests/run-install.sh
```
Expected: syntax and lint pass.

## 7. Confirm no ADR was added or changed

```sh
git status --porcelain docs/adr/
```
Expected: no output — this feature does not touch `docs/adr/` (see spec.md
Assumptions: no ADR is warranted for this two-way-door change).
