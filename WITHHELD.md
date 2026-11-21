# Withheld and generalized material

This public copy is generated from a private working repository.

## Generalized
Personal identifiers were replaced with placeholders; research content is unchanged.

| Placeholder | Stands for |
|---|---|
| `VICTIM-PC` | the infected Windows desktop's hostname |
| `analysis-laptop`, `home-server` | the analyst's laptop and a home server |
| `C:\Users\<USER>` | the Windows account name |
| `<DESKTOP-LAN-IP>`, `<ROUTER-IP>`, `<LAN-HOST-A/B>`, `<LAN-IP>` | private LAN addresses |
| `<TAILSCALE-IP>`, `<MAC>` | VPN address, network hardware addresses |
| `<GITHUB-USER>` | the owner's code-hosting handle |
| `token=<REDACTED>` | download tokens in URLs |
| `<startup-script>.vbs` | a personal startup script name |
| `S-1-5-21-<MACHINE-SID>`, `<PRODUCT-ID>` | Windows machine SID and product ID |
| `desktop-linux`, `<SANDBOX-ACCOUNT>`, `<USER>` | VPN node name, sandbox account names, local account name |
| `<VM-SUBNET-IP>` | WSL/Hyper-V virtual adapter addresses |
| `<AI-APP>`, `<AI-VENDOR>` | names of an AI assistant app and its vendor seen in host logs |

## Withheld files

| File | What it was |
|---|---|
| `02_host_evidence/files/downloads_listing_with_origin.csv` | listing of the owner's downloads with their origin URLs |
| `02_host_evidence/files/downloads_listing_with_origin.txt` | listing of the owner's downloads with their origin URLs |
| `02_host_evidence/logs/Application.csv` | raw application event log |
| `02_host_evidence/logs/Microsoft-Windows-PowerShell_Operational.csv` | raw PowerShell operational log |
| `02_host_evidence/logs/Windows_PowerShell.csv` | raw PowerShell event log |

See the placeholder `README.md` inside each folder for other withheld material.
