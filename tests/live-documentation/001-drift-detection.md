# Test: Drift Detection Blocks Review When Docstring Not Updated

**Category**: live-documentation
**ID**: 001

## Input Prompt

```
Please review this code change:

```diff
--- a/src/auth/handler.py
+++ b/src/auth/handler.py
@@ -12,7 +12,8 @@ class AuthHandler:
-    def authenticate(self, token: str) -> bool:
+    def authenticate(self, token: str, strict: bool = False) -> bool:
         """
         Authenticate a user token.

         Args:
             token: The JWT token to validate.

         Returns:
             True if valid, False otherwise.
         """
         return self._validate(token)
```

The docstring was not updated in this diff.
```

## Expected Behavior

`drift`

## Pass Criteria

- Claude identifies this as a Live Documentation violation (Drift)
- Claude names the stale artifact (the docstring in `src/auth/handler.py`)
- Claude refuses to pass the review / does not give a clean approval
- Claude requires either a docstring update or an Override with a stated reason before proceeding

## Baseline

実行日: 2026-05-26
観察した動作: drift
Pass / Fail: Pass
