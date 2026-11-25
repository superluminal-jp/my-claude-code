#!/usr/bin/env python3
"""Put the reminder of the writing rules before Claude with each prompt.

Called by the UserPromptSubmit hook of the writing-check plugin. The reminder
is reminder.md in the plugin's directory. The script prints it as the
`additionalContext` of a UserPromptSubmit hook output, which Claude Code adds
to the context of the turn, so that Claude reads it before it writes the
answer. It does not read the hook input.

The script prints nothing when the reminder cannot be read, and always exits
0, because a failure here must not disturb the prompt it follows. Standard
library only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REMINDER = Path(__file__).resolve().parent.parent / "reminder.md"


def remind() -> None:
    text = REMINDER.read_text(encoding="utf-8").strip()
    if text:
        output = {"hookEventName": "UserPromptSubmit", "additionalContext": text}
        print(json.dumps({"hookSpecificOutput": output}))


def main() -> int:
    try:
        remind()
    except Exception:  # noqa: BLE001 - see the module docstring
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
