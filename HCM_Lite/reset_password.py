
import sqlite3
import bcrypt
from pathlib import Path
from getpass import getpass

db_path = Path(__file__).parent / "hcm_lite.db"
email = "ali@example.com"

password = getpass("Enter NEW Ali password: ")
confirm = getpass("Confirm NEW password: ")

if password != confirm:
    print("ERROR: Passwords do not match.")

elif len(password) < 8:
    print("ERROR: Password must be at least 8 characters.")

elif len(password.encode("utf-8")) > 72:
    print("ERROR: Password must not exceed 72 UTF-8 bytes.")

else:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE lower(email) = lower(?)
            """,
            (hashed, email)
        )
        conn.commit()

        if result.rowcount == 1:
            print("Ali's password updated successfully.")
        else:
            print("ERROR: Ali's login account was not found.")
