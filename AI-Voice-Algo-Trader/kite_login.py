"""
One-time / daily helper to obtain KITE_ACCESS_TOKEN for kiteconnect.

Usage:
  1. Set KITE_API_KEY and KITE_API_SECRET in .env
  2. python kite_login.py
  3. Open the printed URL, log in, copy request_token from redirect URL
  4. Paste request_token when prompted
  5. Copy the printed access_token into .env as KITE_ACCESS_TOKEN

Access tokens expire daily (regenerate each trading day before market open).
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from kiteconnect import KiteConnect

load_dotenv()


def main() -> None:
    api_key = os.environ.get("KITE_API_KEY")
    api_secret = os.environ.get("KITE_API_SECRET")
    if not api_key or not api_secret:
        print("Set KITE_API_KEY and KITE_API_SECRET in .env", file=sys.stderr)
        sys.exit(1)

    kite = KiteConnect(api_key=api_key)
    print("\nOpen this URL in your browser and log in:\n")
    print(kite.login_url())
    print()
    request_token = input("Paste request_token from redirect URL: ").strip()
    if not request_token:
        print("No token provided.", file=sys.stderr)
        sys.exit(1)

    session = kite.generate_session(request_token, api_secret=api_secret)
    access_token = session["access_token"]
    print("\nAdd this to your .env file:\n")
    print(f"KITE_ACCESS_TOKEN={access_token}\n")


if __name__ == "__main__":
    main()
