# Incident report: trojanized "Lichii" Switch emulator → Go infostealer + Cloudflare tunnel backdoor

Host: VICTIM-PC (Windows 10 Pro N 19045), user `User` (local administrator).
Prepared: 2026-11-21 ~00:35 CST (UTC-6). All times are local CST unless marked Z (UTC).
Status at time of writing: both malware processes **suspended** (not killed); Run-key persistence removed; loader folder copied to quarantine; host on DNS-only egress restriction (not fully isolated).

## TL;DR
- **Initial access (high confidence):** 2026-11-07 11:59:53 CST a Google search for "Lichii" led to `https://lichii.org/` (fake "official website"). `lichii-win64.zip` downloaded from `https://lichii.org/downloads/lichii-win64.zip` at 11:59:57. The genuine project is `github.com/Frizti/Lichii` (redirects to `Frizti/Fritchii`).
- **Trojanized package:** in that zip `lichii.exe`, `opengl64x.dll` and `opengl64x_h.dll` are dated 2026-11-06 15:32:40 -06:00; every other file is 13:03:34 → added/modified after the real build. Both DLLs unsigned, MinGW-built; `opengl64x.dll` carries an encrypted blob that contains the name `opengl64x_h.dll`.
- **Execution:** emulator first run ≈12:00:39 (Eden profile created). 12:01:14 `%APPDATA%\t_id.txt` (encoded victim/install ID) written.
- **Second stage:** 12:28:37 `lichii-windows-x86_64.zip` appears in the extracted folder; 12:28:53 `%LOCALAPPDATA%\Programs\Python\Python399\` (fake Python folder) created; 12:29:00 `%APPDATA%\Microsoft\Internet Explorer\wd.pid` created.
- **Persistence:** HKCU Run value `Microsoft Display Driver Manager` = `pythonw.exe ...\Python399\python3\exec.py` (removed 11/21).
- **Runtime:** at each logon `exec.py` → `updater.cp313-win_amd64.pyd` (Cython) uses PythonForWindows + pythonmemorymodule to launch two processes from **`C:\Windows\Fonts\`** whose files are deleted from disk afterwards:
  - `calc.exe` → a renamed **cloudflared** (Cloudflare Tunnel client, Go 1.27.4) running a quick tunnel `https://included-comprehensive-electro-organizations.trycloudflare.com` → origin `http://localhost:49912`. Uses Cloudflare edge IPs 198.41.192.0/20 :7844 directly (DNS filtering does not block it).
  - `charmap.exe` → a **Go infostealer / C2 client** (browser Cookies, Login Data, Local State, Local Storage/leveldb, Brave; Exodus, MetaMask wallets) with six C2 domains and BNB Smart Chain RPC endpoints (likely blockchain dead-drop for C2 config).
- **Dwell time:** ~2 weeks (2026-11-07 → 2026-11-21). Defender never detected any component.
- **Ruled out:** SSH (only the owner's laptop key/attempts in OpenSSH log), winget (no install logs or packages related), `ootrshaders.zip` (two .bin shader files only).

## Timeline
| Time (CST) | Event | Source |
|---|---|---|
| 11/07 11:48:16 | Google search "Lichii" | Chrome history |
| 11/07 11:59:53 | Google search "Lichii" → 11:59:55 visit `https://lichii.org/` ("Lichii: Nintendo Switch 2 Emulator \| Official Website") | Chrome history |
| 11/07 11:59:57 | Download `lichii-win64.zip` from `https://lichii.org/downloads/lichii-win64.zip` | Chrome downloads + Zone.Identifier |
| 11/07 12:00:29 | Zip extracted to `Downloads\lichii-win64\` (opengl64x*.dll written) | FS timestamps |
| 11/07 12:00:39 | Emulator first run (`%APPDATA%\eden\` profile) | FS |
| 11/07 12:01:14 | `%APPDATA%\t_id.txt` (254 B, `25....` + base64 of an obfuscated string) | FS |
| 11/07 12:15–12:19 | Reddit guide → base64decode.org → `ootrshaders.zip` (buzzheavier) — benign data; `Lichii-Frizti-v3-Windows-x64.zip` from real GitHub | Chrome, FS |
| 11/07 12:28:37 | `Downloads\lichii-win64\lichii-windows-x86_64.zip` (116 MB "update") | FS |
| 11/07 12:28:53 | `Python399\` loader folder created (399 files, all same ctime) | FS |
| 11/07 12:29:00 | `wd.pid` created (holds PID of the stealer process) | FS |
| 11/07 12:34:22 | Update zip extracted over the original files (opengl64x*.dll retained) | FS |
| 11/07 12:45 | DS4Windows downloads from `github.com/ds4windowsapp` (via `ds4-windows.com`) — **unverified**, see below | Chrome, FS |
| 11/20 20:30:33 | Boot | WMI LastBootUpTime |
| 11/20 ≈20:31:14 | `pythonw.exe exec.py` from Run key; ≈20:31:28 `Fonts\calc.exe` + `Fonts\charmap.exe` start (WMI shows 11/21 02:31 — clock was ~6 h ahead right after boot, likely RTC-in-UTC; treat 02:31 stamps on 11/21 as ≈20:31 11/20) | WMI, 7045 |
| 11/20 23:35 | Owner's laptop SSH key login (benign) | OpenSSH log |
| 11/21 ~00:00–00:35 | Containment: Run key removed, pythonw killed, folder copied; charmap + calc suspended; dumps taken | SYSTEM_CHANGELOG |

## Components and hashes (SHA-256)
| File | SHA-256 | Notes |
|---|---|---|
| lichii-win64.zip | DA27BB51D82D14600DA3E8D5FA87087641C9DB09E9850365ADBF7D2B54E518B4 | from lichii.org |
| lichii-windows-x86_64.zip | 1560B9D46A20B54A8494316A650BFEF12A905FBD6C612758D4509DCEFCA61164 | "update", 12:28:37 |
| opengl64x.dll | C1A7B8883B29C67EABA1D2853C3D16265A6A84CF944DBCB5CB64A79E7A6FF79D | 32,256 B, unsigned, MinGW, encrypted blob |
| opengl64x_h.dll | 3D85F47B2C0528FF450CF1B93C8D4F3C2DA0EDC99CEE99BC1C449A93054688C0 | 17,920 B, unsigned |
| lichii.exe (fake, current, after update) | E62648BB5F5A57DA9F54CF29F46708C710EA0C29DB897B61901406495BAB5C7C | 42,180,608 B |
| lichii.exe (genuine GitHub Frizti v3, for comparison) | 7957495E5D24A2A35EA1E5F5B20B57806F5624101B131B15FD16816A22A4413C | 46,601,728 B |
| updater.cp313-win_amd64.pyd | FBB10BDFFBEE81893D16E533C9F4CF60CD029A4528617ABC9920CC09E1A3CD9D | Cython loader, imports only python313/CRT |
| calc.DMP (full dump of Fonts\calc.exe = cloudflared) | D932CF298CCE6FC4932E913A1E4C37894309BE0154641BA33B9FD3EFE28F68EA | 141 MB |
| charmap.DMP (full dump of Fonts\charmap.exe = stealer) | 2A4A1ACB20B415F442F27D3519962B234E29A63F76605DC0ED336264335B1985 | 61 MB |
Full per-file hash lists: `analysis\_sha256.csv` (Python399), `files\hashes_all_samples.txt`.

## Indicators of compromise
See `IOCs.txt` (plain list for blocking/searching).

### Network
- Delivery: `lichii.org` (`/downloads/lichii-win64.zip`)
- Stealer C2 (path prefix `/well-known/pki-validation/go/`, files `boing`, `akgo.php`, `err.php`, `abe.a`, `qoing`, `qperl`):
  `dpdc737.dpdatacenter.com`, `dongphucasian.com`, `waterseas.xyz`, `atomicplanets.cc`, `cosmicsky.cc`, `seaofstar.st`
- Blockchain RPCs used by the stealer (legit services, abused): bsc-dataseed.binance.org, bsc-dataseed{1,2,3}.defibit.io, bsc-dataseed{1,2}.ninicoin.io, bsc.publicnode.com, binance.llamarpc.com, rpc.backrunshield.com, bsc.blockrazor.xyz, bsc.api.pocket.network, lb.routeme.sh
- Tunnel: `included-comprehensive-electro-organizations.trycloudflare.com` (origin `localhost:49912`); edges 198.41.192.0/20 TCP/UDP 7844; metrics `127.0.0.1:20241`
- Seen in memory, unexplained: `<TAILSCALE-IP>` (Tailscale CGNAT range — check your tailnet), `79.29.185.165` (in cloudflared dump; may be cert/edge data)

### Host
- `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` → `Microsoft Display Driver Manager`
- `%LOCALAPPDATA%\Programs\Python\Python399\python3\{exec.py, updater.cp313-win_amd64.pyd, pythonmemorymodule\, windows\}`
- `C:\Windows\Fonts\calc.exe`, `C:\Windows\Fonts\charmap.exe` (deleted after launch; run from memory)
- `%APPDATA%\Microsoft\Internet Explorer\wd.pid`
- `%APPDATA%\t_id.txt`
- `Downloads\lichii-win64\opengl64x.dll`, `opengl64x_h.dll`

## Analysis notes
- `exec.py` = `from updater import update; update()`. The `.pyd` is a small Cython module (~42 KB code); its imports are Python C-API only, so behaviour lives in compiled Python + the bundled PythonForWindows (`windows\injection.py`, `remotectypes.py`, `native_exec`) and `pythonmemorymodule` (in-memory PE loader). Strings are not in plain text.
- Both Fonts processes contain extra 32-bit PE images in private (non-module) memory: `extract_charmap\pe_2087f950000.bin` (1.3 MB), `extract_calc\pe_1fb7cce0000.bin`, `pe_1fb7d040000.bin`. Not yet analysed.
- `charmap.exe` main image is 0x1270000 bytes, Go; `calc.exe` image 0x597d000 bytes, Go 1.27.4, full cloudflared (argotunnel, quic-go, urfave/cli, Sentry DSN 56a9c9fa5c364ab28f34b14f35ea0f1b — that is cloudflared's own).
- Triage output: `analysis\charmap_triage.txt`, `analysis\calc_triage.txt` (script: `analysis\mdparse.py.txt`).
- The URL `/well-known/` (missing leading dot) mimics ACME/PKI validation paths.
- The blockchain RPC list strongly suggests the C2 address (or config) is read from a smart contract on BNB Smart Chain ("EtherHiding"-style). This is an inference.

## Unverified / needs research
- **DS4Windows from `github.com/ds4windowsapp/DS4Windows` (reached via `ds4-windows.com`)** — not the usual upstream (`schmaldeo/DS4Windows`, formerly `Ryochan7`). `DS4Windows-Official.zip` ships an unsigned 9.5 MB `OUT\DS4Windows.exe` (SHA-256 AFD11142CF19FBD0727537B95A0DA49F0895B840C659FCF29252912772B74CCB) inside a source tree; `DS4Windows.3.5.x64.DS4-Windows.com.zip` has `DS4Windows.exe` 232,960 B (SHA-256 6267CBA17B87ADA8F13EC6E187B309E3C76AA087ACF2C255AB19DC2DB6799A34). ViGEmBus driver installed 12:47:58. Check both hashes. `ds4w.bat` itself is benign.
- What served `localhost:49912` (the tunnel origin) — nothing listening at collection time.
- `t_id.txt` encoding (prefix `25....`, base64, then a further obfuscation).
- Family name: not identified; search the C2 domains / path / hashes.
- Hermes Agent is running again (`hermes_cli.main gateway run`, Startup `<startup-script>.vbs`) despite being removed 11/15 — confirm whether the owner reinstalled it.

## Exposure / what to rotate (from a clean device)
Assume everything readable by the user account for 2 weeks is stolen: browser saved passwords, cookies/sessions (Chrome, Edge, Firefox, Brave), Discord token, Steam/Epic sessions, GitHub (`gh` token), SSH keys in `~/.ssh` (id_rsa, id_ed25519_test), API keys in env/config files, Tailscale node key, any crypto wallets (move funds to a new wallet created on a clean device). Revoke sessions, not just passwords.

## Folder guide (this archive)
- `system\` processes (csv/txt), installed programs, winget list, Defender status, users, systeminfo
- `persistence\` Run keys, Startup, scheduled tasks, services, WMI, Winlogon, Fonts dir
- `network\` TCP/UDP with PIDs, DNS cache, ipconfig, hosts/proxy, firewall, ARP/routes
- `logs\` CSV exports since 2026-11-05 (OpenSSH, Defender, PowerShell, System, Application, BITS) + service installs (7045)
- `files\` downloads with origin URLs, file-creation timeline 11/07 11:30–13:00, Python399 listing, zip listings, t_id/wd.pid copies, hashes, browser-history findings
- `browser\` raw History/places.sqlite copies (private — full browsing history)
- `analysis\` memory-dump triage, Run-key backup, process captures

The malware samples and memory dumps are in separate password-protected archives (see `PASSWORDS` note given in the terminal).
