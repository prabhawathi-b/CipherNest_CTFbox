# CipherNest

**"Unravel the Nest. Decode the Truth."**

> Status: Phase 1 — repository and network skeleton only. Challenges are
> not yet implemented. This README is filled in incrementally as each
> phase completes; do not treat any section below as a completed feature
> until it explicitly says TESTED.

## 1. Project Overview
*(to be completed — Phase 12)*

## 2. Scenario
CeylonGov Secure, a fictional organisation, suffered a simulated security
incident in its staging environment. The participant acts as an ethical
hacker and must recover six "nest fragments" to reconstruct the intrusion
path: CN-01 → CN-02 → CN-03 → CN-04 → CN-05 → CN-06.

## 3. Learning Objectives
*(to be completed — Phase 12)*

## 4. Challenge Overview
*(to be completed as each stage is built — Phases 3–8)*

## 5. Architecture
Three-layer design: Participant (Kali) → CTF Control Layer (Nginx +
Flask platform) → Challenge Layer (per-stage containers on an isolated
Docker network). See `docs/architecture.md` (Phase 2+) and
`docs/design-changes.md` for deviations from the Assignment 01 design.

## 6. Prerequisites
- Docker Desktop (Windows, WSL2 backend) or Docker Engine + Compose v2 (Linux)
- Git
- A Kali Linux VM/machine (or any machine with nmap, steghide, exiftool,
  binwalk, Wireshark, an FTP client) for solving the challenges

## 7. Windows Setup
*(to be completed — Phase 12)*

## 8. Kali Setup
*(to be completed — Phase 12)*

## 9. Docker Installation
*(to be completed — Phase 12)*

## 10. Clone / Copy Project
```
git clone <repo-url> CipherNest
cd CipherNest
cp .env.example .env
```

## 11. Environment Configuration
Copy `.env.example` to `.env` and adjust values if needed (see comments
in that file). Do not commit `.env`.

## 12. Build
```
docker compose build
```

## 13. Start
```
docker compose up -d
```

## 14. Health Check
```
docker compose ps
curl http://localhost:8080/health
```
Expected: all listed services show `Up`, and the health check returns
`{"status": "ok", "service": "ciphernest-platform"}`.

## 15. Access URLs
| Service | URL |
|---|---|
| Platform / landing page | http://localhost:8080/ |

*(challenge-specific URLs added as each stage is built)*

## 16. Network Design
- `ctf-frontnet` — participant-facing bridge network. Only Nginx's port
  8080 is published to the host.
- `ctf-challnet` — `internal: true`. Challenge containers live here and
  cannot reach the public internet. Nginx joins both networks to proxy
  HTTP challenges through to the participant.

## 17. Flag Validation
*(to be completed — Phase 9)*

## 18. Reset
*(to be completed — Phase 10)*

## 19. Troubleshooting
*(to be completed — Phase 12)*

## 20. Testing
*(to be completed — Phase 11)*

## 21. Individual Contributions
| Member | Responsibility |
|---|---|
| Prabhawathi B | Platform & Architecture |
| Sanujan B | Challenge Design A |
| Sajeebarath S | Challenge Design B |
| Randunu R.P.R.R | Integration, Testing & Documentation |

## 22. Security / Isolation Notes
*(to be completed — Phase 12, summarising `tests/test_isolation.sh` results)*

## 23. External Tools / Resources Used
- Nginx, Flask, SQLite, Docker/Docker Compose
- steghide, Wireshark/tshark, Autopsy or equivalent CLI forensic tools (participant-side)

## 24. Known Limitations
*(to be completed — Phase 12)*

## 25. Assignment 01 Design Changes
See `docs/design-changes.md`.
