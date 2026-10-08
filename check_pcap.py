from scapy.all import rdpcap

packets = rdpcap("/work/evidence_capture.pcap")
print(f"Total packets: {len(packets)}")
for i, pkt in enumerate(packets):
    print(f"--- Packet {i} ---")
    print(pkt.summary())
    if pkt.haslayer("Raw"):
        print("Payload:", pkt["Raw"].load)
