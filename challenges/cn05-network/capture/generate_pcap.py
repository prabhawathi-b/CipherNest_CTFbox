"""
Generates evidence_capture.pcap: a synthetic packet capture showing a
plaintext FTP USER/PASS exchange, matching the credentials used by
cn05-target. Built with Scapy so it's a REAL, Wireshark-readable PCAP,
not a fake text file.
"""
from scapy.all import wrpcap, Ether, IP, TCP, Raw
import time

CLIENT_IP = "192.168.77.41"
SERVER_IP = "10.20.30.40"
CLIENT_PORT = 51234
SERVER_PORT = 21

packets = []
t = time.time()
seq_c = 1000
seq_s = 5000


def add_pkt(src, dst, sport, dport, flags, payload=b"", seq=0, ack=0):
    global t
    t += 0.05
    pkt = Ether() / IP(src=src, dst=dst) / TCP(
        sport=sport, dport=dport, flags=flags, seq=seq, ack=ack
    )
    if payload:
        pkt = pkt / Raw(load=payload)
    pkt.time = t
    packets.append(pkt)


# TCP handshake
add_pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "S", seq=seq_c)
seq_s_init = seq_s
add_pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "SA", seq=seq_s, ack=seq_c + 1)
seq_c += 1
add_pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "A", seq=seq_c, ack=seq_s + 1)
seq_s += 1

# FTP banner
banner = b"220 CeylonGov Secure - Internal Backup Service\r\n"
add_pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "PA", seq=seq_s, ack=seq_c, payload=banner)
seq_s += len(banner)
add_pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "A", seq=seq_c, ack=seq_s)

# USER command
user_cmd = b"USER svc_backup\r\n"
add_pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "PA", seq=seq_c, ack=seq_s, payload=user_cmd)
seq_c += len(user_cmd)
add_pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "A", seq=seq_s, ack=seq_c)

user_resp = b"331 Username ok, need password.\r\n"
add_pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "PA", seq=seq_s, ack=seq_c, payload=user_resp)
seq_s += len(user_resp)
add_pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "A", seq=seq_c, ack=seq_s)

# PASS command - the credential leak
pass_cmd = b"PASS B4ckup_Serv1ce_2024\r\n"
add_pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "PA", seq=seq_c, ack=seq_s, payload=pass_cmd)
seq_c += len(pass_cmd)
add_pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "A", seq=seq_s, ack=seq_c)

pass_resp = b"230 Login successful.\r\n"
add_pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "PA", seq=seq_s, ack=seq_c, payload=pass_resp)
seq_s += len(pass_resp)
add_pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "A", seq=seq_c, ack=seq_s)

wrpcap("/build/evidence_capture.pcap", packets)
print(f"PCAP generated with {len(packets)} packets.")
