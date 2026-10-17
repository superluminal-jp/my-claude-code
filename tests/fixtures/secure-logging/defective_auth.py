"""Fixture for the secure-logging skill: deliberately defective logging.

Used by the manual check in specs/050-secure-logging-skill/quickstart.md.
The sample credentials are fake values for this test only.
"""

import logging

log = logging.getLogger("auth")

USERS = {"alice": "s3cret-sample-password"}


def login(username: str, password: str, token: str) -> bool:
    # Defect 1: a password and a token are written to the log in clear text.
    log.info("login attempt user=%s password=%s token=%s", username, password, token)

    # Defect 2: untrusted input is logged without neutralizing CR/LF.
    log.info("login for " + username)

    if USERS.get(username) == password:
        return True

    # Defect 3: a failed authentication is not recorded at all.
    return False
