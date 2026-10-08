"""
CN-04 Solver - Buried Logs (Digital Forensics / File Carving)

Automates the intended solve path:
  1. Download the evidence package with Basic Auth (creds from CN-03)
  2. Grep the intact logs for the suspicious repeated IP
  3. Carve the "deleted" file from the raw bytes using the recovery markers
  4. Print the Stage 4 flag and the CN-05 internal host/IP

Usage:
    python3 cn04_solver.py --url http://localhost:8080/cn04/staging_evidence.bin
"""
import argparse
import base64
import re
import urllib.request

START_MARKER = b"--RECOVERED-FILE-START--\n"
END_MARKER = b"\n--RECOVERED-FILE-END--\n"


def main():
    parser = argparse.ArgumentParser(description="CN-04 forensics solver")
    parser.add_argument("--url", default="http://localhost:8080/cn04/staging_evidence.bin")
    parser.add_argument("--username", default="archive_user")
    parser.add_argument("--password", default="Ar7ifact_Vau1t9")
    args = parser.parse_args()

    creds = base64.b64encode(f"{args.username}:{args.password}".encode()).decode()
    req = urllib.request.Request(args.url, headers={"Authorization": f"Basic {creds}"})

    print(f"[*] Downloading evidence package from {args.url}")
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    print(f"[+] Downloaded {len(data)} bytes.")

    text = data.decode(errors="ignore")
    suspicious_ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", text)
    from collections import Counter
    counts = Counter(suspicious_ips)
    most_common_ip, count = counts.most_common(1)[0]
    print(f"[*] Most frequent IP in logs: {most_common_ip} ({count} occurrences)")

    start_idx = data.find(START_MARKER)
    end_idx = data.find(END_MARKER)
    if start_idx == -1 or end_idx == -1:
        print("[-] Could not locate deleted-file markers - carving failed.")
        return

    recovered = data[start_idx + len(START_MARKER):end_idx].decode()
    print("\n----- Recovered deleted file -----")
    print(recovered)
    print("-----------------------------------")

    flag_match = re.search(r"CipherNest\{[^}]+\}", recovered)
    ip_match = re.search(r"investigation:\s*\n?\s*(\d+\.\d+\.\d+\.\d+)", recovered)

    if flag_match:
        print(f"\n[FLAG] {flag_match.group(0)}")
    if ip_match:
        print(f"[CN-05 TARGET IP] {ip_match.group(1)}")


if __name__ == "__main__":
    main()
