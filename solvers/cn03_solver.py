"""
CN-03 Solver - Weak Locks (Base64 + Vigenere)

Automates the intended solve path:
  1. Fetch the encoded string from the challenge page
  2. Base64-decode it
  3. Vigenere-decrypt the result using the key hinted in CN-02 (NEST)
  4. Print the Stage 3 flag and CN-04 credentials

Usage:
    python3 cn03_solver.py --url http://localhost:8080/cn03/challenge.txt --key NEST
"""
import argparse
import base64
import re
import urllib.request


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    key = key.upper()
    result = []
    key_idx = 0
    for ch in ciphertext:
        if ch.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord("A")
            base = ord("A") if ch.isupper() else ord("a")
            new_ch = chr((ord(ch) - base - shift) % 26 + base)
            result.append(new_ch)
            key_idx += 1
        else:
            result.append(ch)
    return "".join(result)


def main():
    parser = argparse.ArgumentParser(description="CN-03 Base64+Vigenere solver")
    parser.add_argument("--url", default="http://localhost:8080/cn03/challenge.txt")
    parser.add_argument("--key", default="NEST")
    args = parser.parse_args()

    print(f"[*] Fetching challenge artifact from {args.url}")
    with urllib.request.urlopen(args.url) as resp:
        content = resp.read().decode()

    match = re.search(r"Encoded string:\s*\n([A-Za-z0-9+/=]+)", content)
    if not match:
        print("[-] Could not find encoded string in challenge text.")
        return
    encoded = match.group(1)
    print(f"[*] Encoded string found: {encoded}")

    # Layer 1: Base64 decode
    layer1 = base64.b64decode(encoded).decode()
    print(f"[*] After Base64 decode: {layer1}")

    # Layer 2: Vigenere decrypt
    plaintext = vigenere_decrypt(layer1, args.key)
    print(f"[+] After Vigenere decrypt (key={args.key}): {plaintext}")

    flag_match = re.search(r"CipherNest\{[^}]+\}", plaintext)
    if flag_match:
        print(f"\n[FLAG] {flag_match.group(0)}")

    if "::" in plaintext:
        creds = plaintext.split("::", 1)[1]
        print(f"[CN-04 CREDENTIALS] {creds}")


if __name__ == "__main__":
    main()
