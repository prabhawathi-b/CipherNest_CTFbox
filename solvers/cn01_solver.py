#!/usr/bin/env python3
"""
CN-01 steganography solver.

Downloads ceylongov_banner.png from the CN-01 challenge, extracts the
hidden text from the least-significant bit of each pixel's red channel,
and prints the recovered flag.

Requires: pip install pillow requests
"""
import argparse
import io

import requests
from PIL import Image

DELIMITER = "<<<END>>>"


def extract_text(img: Image.Image) -> str:
    pixels = img.convert("RGB").load()
    width, height = img.size

    bits = ""
    text = ""
    for y in range(height):
        for x in range(width):
            r, _, _ = pixels[x, y]
            bits += str(r & 1)
            if len(bits) == 8:
                text += chr(int(bits, 2))
                bits = ""
                if text.endswith(DELIMITER):
                    return text[: -len(DELIMITER)]
    raise ValueError("Delimiter not found; image may not contain hidden data.")


def main():
    parser = argparse.ArgumentParser(description="CN-01 steganography solver")
    parser.add_argument("--url", default="http://localhost:8080/cn01/ceylongov_banner.png")
    args = parser.parse_args()

    print(f"[*] Downloading image from {args.url}")
    resp = requests.get(args.url, timeout=10)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content))

    print("[*] Extracting LSB payload from red channel...")
    recovered = extract_text(img)

    print("\n----- recovered text -----")
    print(recovered)
    print("---------------------------\n")

    flag = next((line for line in recovered.splitlines() if "CipherNest{" in line), None)
    if flag:
        start = flag.index("CipherNest{")
        end = flag.index("}", start) + 1
        print(f"[FLAG] {flag[start:end]}")
    else:
        print("[!] No CipherNest{...} flag found in recovered text.")


if __name__ == "__main__":
    main()
