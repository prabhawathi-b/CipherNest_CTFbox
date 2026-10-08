"""
CN-06 Solver - The Nest Revealed (OSINT Capstone / Final Derivation)

Combines the five previous flags using the rule disclosed on the CN-06
profile page:
  1. Take the 3rd character of each flag's inner content (stage order)
  2. Concatenate into one string
  3. Caesar-shift each letter using the key named in the profile's
     favourite quote ("RAVEN" - the bird referenced in the quote)
  4. Wrap as CipherNest{...}

Usage:
    python3 cn06_solver.py
"""

PREVIOUS_FLAGS = [
    "st3g0_fr4gm3nt_r3c0v3r3d",   # CN-01
    "b00l3an_1nj3ct10n_m4st3r",   # CN-02
    "v1gn3r3_crypt0_crack3r",     # CN-03
    "d3l3t3d_but_n0t_g0n3",       # CN-04
    "ftp_sn1ff3d_1n_th3_cl34r",   # CN-05
]

KEY = "RAVEN"


def caesar_shift(text: str, key: str) -> str:
    result = []
    for i, ch in enumerate(text):
        shift = ord(key[i % len(key)].upper()) - ord("A")
        if ch.isalpha():
            base = ord("a") if ch.islower() else ord("A")
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def main():
    print("[*] Previous flags (in stage order):")
    for i, f in enumerate(PREVIOUS_FLAGS, start=1):
        print(f"    CN-0{i}: CipherNest{{{f}}}")

    third_chars = "".join(f[2] for f in PREVIOUS_FLAGS)
    print(f"\n[*] 3rd character of each: {third_chars}")

    final_core = caesar_shift(third_chars, KEY)
    print(f"[*] After Caesar shift (key={KEY}): {final_core}")

    final_flag = f"CipherNest{{{final_core}}}"
    print(f"\n[FLAG] {final_flag}")


if __name__ == "__main__":
    main()
