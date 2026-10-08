with open("evidence.bin", "rb") as f:
    data = f.read()

START = b"--RECOVERED-FILE-START--\n"
END = b"\n--RECOVERED-FILE-END--\n"

start_idx = data.find(START)
end_idx = data.find(END)

if start_idx == -1 or end_idx == -1:
    print("Marker not found - carving failed.")
else:
    recovered = data[start_idx + len(START):end_idx]
    print(recovered.decode())
