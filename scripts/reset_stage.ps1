param([Parameter(Mandatory=$true)][ValidateSet("CN01","CN02","CN03","CN04","CN05","CN06")][string]$Stage)
$map = @{ CN01=@("cn01-stego"); CN02=@("cn02-webapp"); CN03=@(); CN04=@("cn04-forensics"); CN05=@("cn05-target","cn05-capture"); CN06=@("cn06-profile") }
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($map[$Stage].Count -eq 0) { Write-Host "$Stage is a static file served by Nginx. Nothing to reset."; exit 0 }
docker compose up -d --force-recreate $map[$Stage]
Start-Sleep -Seconds 3
docker compose restart nginx
docker compose ps
