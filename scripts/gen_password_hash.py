#!/usr/bin/env python3
"""Generate a bcrypt hash for the single admin password.

Usage:
    python scripts/gen_password_hash.py 'your-plain-password'

Paste the output into ADMIN_PASSWORD_HASH in your .env file.
Requires: pip install bcrypt
"""
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/gen_password_hash.py 'your-password'")
        raise SystemExit(1)
    try:
        import bcrypt
    except ImportError:
        print("bcrypt not installed. Run: pip install bcrypt")
        raise SystemExit(1)
    password = sys.argv[1].encode("utf-8")
    hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")
    print(hashed)


if __name__ == "__main__":
    main()
