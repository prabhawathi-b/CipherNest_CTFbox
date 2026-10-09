# CipherNest CTF Play Box

IE3132 Penetration Testing, Assignment 02, Group 37.

CipherNest is a six-stage Capture-The-Flag box that runs in Docker. Players investigate a simulated incident at CeylonGov Secure, a fictional agency. All organisations, people, credentials and IP addresses are invented for this exercise.

WARNING: CN-02 is intentionally vulnerable (SQL injection). Run this box only on a local, isolated machine. Never expose it to the internet or test these techniques against real systems.

## Requirements

- Windows 10/11 (tested) with Docker Desktop and Docker Compose v2
- Free host ports: 8080, 2221 and 2121-2130
- Internet access for the first build (Docker Hub, PyPI and Alpine package mirrors)

## Quick start (Windows PowerShell)

    cd CipherNest
    docker compose up -d --build
    docker compose restart nginx
    docker compose ps
    curl.exe http://localhost:8080/health

Expected: eight containers running and {"service":"ciphernest-platform","status":"ok"}.

A warning that the compose attribute "version" is obsolete is harmless and can be ignored. Use curl.exe, not curl, because PowerShell aliases curl to Invoke-WebRequest.

## How to play

1. Open http://localhost:8080 and choose Start investigating.
2. Create an account: a callsign (3-20 letters, numbers or underscores) and a password of at least 8 characters. There are no default accounts.
3. On the dashboard, open each challenge, recover the flag, and submit it. Flags look like CipherNest{...}.
4. Progress is saved per account. The progress ring and the Solved/Next/Open status come from the database.

The stages are designed to be played in order, and each stage's output feeds the next. The dashboard recommends the order but does not enforce it.

## Challenges

| ID | Title | Domain | Difficulty | Where |
|----|-------|--------|------------|-------|
| CN-01 | Frame of Reference | Steganography | Easy | /cn01/ |
| CN-02 | Back Door Left Ajar | Web Security | Easy | /cn02/ |
| CN-03 | Weak Locks | Cryptography | Moderate | /cn03/ (static files, no container) |
| CN-04 | Buried Logs | Digital Forensics | Moderate | /cn04/ (HTTP Basic Auth) |
| CN-05 | Whispers on the Wire | Networking | Moderate-Hard | /cn05-capture/ and FTP on localhost:2221 |
| CN-06 | The Nest Revealed | OSINT / Capstone | Hard | /cn06/ |

## Architecture

| Container | Role | Network(s) | Host ports |
|-----------|------|------------|------------|
| ciphernest-nginx | Reverse proxy, serves CN-03 files | frontnet, challnet | 8080 |
| ciphernest-platform | Flask + gunicorn: UI, accounts, flag validation, logging | frontnet | none |
| ciphernest-cn01-stego | CN-01 image server | challnet | none |
| ciphernest-cn02-webapp | CN-02 vulnerable login (Flask + SQLite) | challnet | none |
| ciphernest-cn04-forensics | CN-04 evidence server (Nginx, Basic Auth) | challnet | none |
| ciphernest-cn05-capture | CN-05 PCAP server | challnet | none |
| ciphernest-cn05-target | CN-05 FTP service (pyftpdlib) | challnet, frontnet | 2221, 2121-2130 |
| ciphernest-cn06-profile | CN-06 staff profile page | challnet | none |

Networks: ctf-frontnet is a normal bridge. ctf-challnet is a bridge with internal: true, so containers that are only on it have no route to the internet. Players reach everything through Nginx on port 8080, except the CN-05 FTP service, which is published directly because FTP cannot be reverse-proxied by Nginx.

## Flag validation and logging

The platform stores only SHA-256 hashes of the six flags, never the plaintext. A submission is hashed and compared in constant time. Every submission (user, stage, accept/reject, time, IP) is written to a SQLite database in the Docker volume platform-data. Submissions are rate limited to 10 per minute per user, and login attempts are throttled separately. Passwords are stored as salted hashes, and the session cookie is signed with a random key kept in the same volume.

## Security controls

- Challenge containers sit on an internal Docker network with no internet route.
- Only port 8080 and the CN-05 FTP ports are published on the host.
- Every container's application process runs as a non-root user except cn05-target (FTP must bind port 21, which needs root). The stock nginx:alpine image used by the reverse proxy and several challenge containers always starts its master process as root by design (standard upstream nginx behaviour); the worker processes that actually handle requests run as the nginx user, and custom-built images additionally run as nginx or a dedicated non-root user at the application layer.
- Flags and credentials are not exposed in public pages or client-side code.

## Reset and recovery

Reset one stage (recreates its container or containers, then restarts Nginx):

    Set-ExecutionPolicy -Scope Process Bypass -Force
    .\scripts\reset_stage.ps1 -Stage CN02

CN-03 is a static file, so the script reports that there is nothing to reset.

Reset the whole box:

    .\scripts\reset_all.ps1

This recreates all challenge containers and DELETES all accounts, solves and submission logs. The Docker volume and the session key are kept, so after a full reset everyone registers again.

## Solver scripts (LO3)

Self-developed solver and exploit scripts are in the solvers folder, one per stage (cn01_solver.py to cn06_solver.py). Run any of them with --help for its options. Example for CN-05 using a throwaway container, so Python is not needed on the host:

    docker run --rm -v "${PWD}\solvers:/s" python:3.12-slim sh -c "pip install -q --root-user-action=ignore scapy && python /s/cn05_solver.py --pcap-url http://host.docker.internal:8080/cn05-capture/evidence_capture.pcap --ftp-host host.docker.internal --ftp-port 2221"

Challenge-generation scripts live next to each challenge, for example challenges/cn01-stego/embed_secret.py and challenges/cn04-forensics/evidence_source/build_evidence.py.

## Troubleshooting

- Nginx reports "host not found in upstream" right after starting or recreating containers: wait a few seconds and run docker compose restart nginx.
- Port 8080 already in use: stop the other program, or change the left side of "8080:80" in docker-compose.yml.
- Write Nginx .conf files with -Encoding ascii. A UTF-8 byte-order mark makes Nginx fail to parse them.
- If the project sits inside a OneDrive folder, file syncing can lock files. Pause syncing if builds fail with file errors.
- Page looks unstyled after an update: hard refresh the browser (Ctrl+F5).

## Known limitations

- The CN-05 A1 design included a decoy SSH service. Only FTP is implemented.
- CN-05 access is gated logically (the credentials come only from the PCAP), not by a per-participant network rule.
- Stage order is recommended on the dashboard but not enforced.
- No password recovery. A full reset clears all accounts.
- Full list of deviations from the Assignment 01 design: docs/design-changes.md

## Tools, libraries and acknowledgements

Docker and Docker Compose, Nginx, Python 3.12, Flask, Werkzeug, gunicorn, SQLite, Pillow (CN-01 image generation and LSB embedding), Scapy (CN-05 PCAP generation and solver), pyftpdlib (CN-05 FTP service), Apache htpasswd utility (CN-04 credentials). Participant tools referenced by hints: Wireshark, CyberChef, Python, a PNG/steganography library.

AI assistance: generative AI assistants were used while building the project (drafting, debugging and review of code and documents). The group reviewed and tested the result. No AI tool was used while recording the demonstration video.

