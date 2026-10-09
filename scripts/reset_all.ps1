Set-Location (Split-Path $PSScriptRoot -Parent)
docker compose up -d --force-recreate cn01-stego cn02-webapp cn04-forensics cn05-target cn05-capture cn06-profile
docker compose up -d platform
$py = "import sqlite3; c=sqlite3.connect('/data/flags.db'); [c.execute('DELETE FROM '+t) for t in ('solves','submissions','users')]; c.commit(); print('database cleared')"
docker compose exec -T platform python -c $py
Start-Sleep -Seconds 3
docker compose restart nginx
docker compose ps
