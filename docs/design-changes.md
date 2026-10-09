# Design changes from the Assignment 01 design

The implementation follows the approved Assignment 01 design: six stages, the same domains, difficulty progression, narrative chain and flag format. The changes below were made for technical reasons. Each one keeps the architectural idea of the original.

| # | Assignment 01 design | As built | Technical justification |
|---|----------------------|----------|-------------------------|
| 1 | PostgreSQL, separate Flask platform, Flag Validation Service and Logging Service | One Flask platform container with SQLite. Validation and logging are separate modules inside it | Four services added orchestration and networking risk for a short build. Hash validation, rate limiting and submission logging are all preserved |
| 2 | CN-01: steghide payload in a JPEG | Self-written LSB embedder and extractor (embed_secret.py) using a PNG | steghide could not be installed because the build network blocked OS package mirrors. JPEG compression is lossy and destroys LSB data, so a lossless PNG is required. This also gives a stronger self-developed-code demonstration |
| 3 | CN-04: real .dd disk image analysed with Autopsy | Binary evidence package (staging_evidence.bin) with logs and a deleted file placed after a null-byte run and EOF marker, recovered by carving | Loopback-mounting a .dd image needs losetup/mount, which does not work from Windows Docker Desktop containers. The forensic skill is preserved: the file is invisible to normal reading and recoverable only by raw-byte carving |
| 4 | CN-05: network access granted per participant after Stage 4 | FTP reachable throughout. The real gate is logical: credentials exist only inside the PCAP | Per-participant dynamic network rules were out of scope. The A1 design itself avoided hard technical locks for other stages |
| 5 | CN-05: vsftpd and an SSH decoy service | pyftpdlib (pip-installed) FTP server. No SSH decoy | pyftpdlib avoids OS packages that the build network blocked. The SSH decoy was not built in the time available |
| 6 | All challenge containers run as non-root | cn05-target runs as root | Binding port 21 requires root. Capability-based alternatives were out of scope. All other containers are non-root |
| 7 | cn05-target isolated on the internal challenge network only | cn05-target is on both ctf-challnet and ctf-frontnet | Docker does not publish host ports for containers that are only on an internal network. FTP cannot be proxied by Nginx, so it needs a published port. It still has no internet access |
| 8 | Nginx terminates TLS on port 443 | Plain HTTP on port 8080 | Local, isolated lab deployment. TLS certificates add setup steps for the lecturer with no benefit on localhost |
| 9 | Participant authentication, hint delivery and CN-03 content delivered by the platform | Accounts with callsign and password stored in SQLite. Hints are shown on each challenge page. CN-03 is a static file served by Nginx | Keeps the platform to one small service. CN-03 remains a data-only artefact as in the A1 design |
| 10 | Admin console runs docker compose force-recreate for reset | PowerShell scripts: scripts/reset_stage.ps1 and scripts/reset_all.ps1 | Same mechanism, no admin web console needed |
| 11 | CN-03 hint 3 pointed to the cipher key | The key is no longer printed in the hint. The player must find it in the CN-02 maintenance notes | Assignment requirement 7: no trivial shortcut around the intended path |

## Not implemented

- SSH decoy service in CN-05 (see row 5).
- Per-participant network gating for CN-05 (see row 4).
- Enforcement of stage order. The dashboard recommends an order only.

- Container resource limits (CPU/RAM) from the A1 risk register were not implemented.
- read_only filesystem plus tmpfs mounts for CN-01, CN-04, CN-05 capture and CN-06 (A1 deployment step 11) were not implemented.
