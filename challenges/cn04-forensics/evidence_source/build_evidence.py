"""
Builds staging_evidence.bin: a binary evidence blob simulating a disk
snapshot. The two intact logs are stored as plain, grep-able text at the
start. The "deleted" file is appended AFTER a null-byte run and a fake
EOF marker, so it does not show up via simple 'cat'/browsing - it must
be recovered via carving (searching for the marker / strings extraction),
exactly like recovering a deleted file whose directory entry is gone but
whose data blocks remain on disk.
"""

with open("access.log", "rb") as f:
    access_log = f.read()

with open("system.log", "rb") as f:
    system_log = f.read()

with open("deleted_note.txt", "rb") as f:
    deleted_note = f.read()

EOF_MARKER = b"\x00\x00\x00--SNAPSHOT-EOF--\x00\x00\x00"
CARVE_MARKER = b"--RECOVERED-FILE-START--"

blob = b""
blob += b"=== access.log ===\n" + access_log + b"\n\n"
blob += b"=== system.log ===\n" + system_log + b"\n\n"
blob += EOF_MARKER
blob += b"\x00" * 64  # simulate unused/slack space
blob += CARVE_MARKER + b"\n"
blob += deleted_note
blob += b"\n--RECOVERED-FILE-END--\n"

with open("staging_evidence.bin", "wb") as f:
    f.write(blob)

print(f"Evidence package built: {len(blob)} bytes")
