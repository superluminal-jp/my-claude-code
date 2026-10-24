# Expected inspection result for `defective_auth.py.fixture`

The fixture keeps a `.fixture` suffix so code scanners do not flag its
intentional defects; the line numbers below refer to the file as stored.

A correct inspection of `defective_auth.py.fixture` reports at least these Fail items,
each with its location:

| Item | Where | Why |
|---|---|---|
| `LOG-DATA-1` | `defective_auth.py.fixture:19` | the password and the token are written in clear text |
| `LOG-INJ-1` | `defective_auth.py.fixture:22` | `username` reaches the log without CR/LF neutralization |
| `LOG-EVT-1` | `defective_auth.py.fixture:28` | the failed authentication path logs nothing |

It also reports these practice items as Fail, counted apart from the security
Fail items above:

| Item | Where | Why |
|---|---|---|
| `LOG-PRC-1` | `defective_auth.py.fixture:12` | the logger is named `"auth"` instead of `__name__` |
| `LOG-PRC-3` | `defective_auth.py.fixture:22` | the message is built by concatenation instead of logger arguments |

It must also:

- report the operational items (`LOG-OPS-*`) as Unverified, never Pass, with the
  evidence the user must supply;
- state which target it inspected;
- begin with a verdict that counts the Fail and Unverified items.

For the implementation check, after "add the failed-authentication log", the
report must show a test that failed before the change, and the log output must
not contain `s3cret-sample-password`.
