"""
Minimal LSB (Least Significant Bit) steganography embedder.
Hides secret.txt inside the red channel's lowest bit of each pixel.
Pure Pillow, no external stego library needed.
"""
from PIL import Image

DELIMITER = "<<<END>>>"

def text_to_bits(text: str) -> str:
    return "".join(format(ord(c), "08b") for c in text)

with open("secret.txt", "r") as f:
    secret = f.read() + DELIMITER

bits = text_to_bits(secret)
total_bits = len(bits)

img = Image.open("banner_cover.png").convert("RGB")
pixels = img.load()
width, height = img.size

if total_bits > width * height:
    raise SystemExit("Image too small to hold the secret data.")

bit_idx = 0
for y in range(height):
    for x in range(width):
        if bit_idx >= total_bits:
            break
        r, g, b = pixels[x, y]
        r = (r & ~1) | int(bits[bit_idx])
        pixels[x, y] = (r, g, b)
        bit_idx += 1
    if bit_idx >= total_bits:
        break

img.save("ceylongov_banner.png", "PNG")
print(f"Secret embedded successfully ({total_bits} bits).")
