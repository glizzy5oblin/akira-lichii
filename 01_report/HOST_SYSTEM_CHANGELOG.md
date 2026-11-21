# System Changelog

A dated log of changes to the infected desktop's system configuration. Each entry records the goal, what was done, the result, and how to revert it.

## Entry format

### YYYY-MM-DD: short title
- **Goal:** why the change was made
- **What was done:** the exact change (setting, command, registry key, install, etc.)
- **Result:** what happened, including failures or side effects
- **Revert:** exact steps or commands to undo the change, including the original value if known

---


### 2026-11-15: Remove Hermes Agent completely
- **Goal:** Uninstall Hermes (Hermes Agent) and all of its integration points from the machine.
- **What was done:**
  - Deleted `C:\Users\<USER>\AppData\Local\hermes` (about 100 GB: install, `models` ~86 GB, sessions, memories, vault, `.env`, `auth.json`, state DBs) and `C:\Users\<USER>\AppData\Roaming\hermes`.
  - Deleted startup script `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\<startup-script>.vbs` and `C:\Users\<USER>\Desktop\Hermes.lnk`.
  - Removed `C:\Users\<USER>\AppData\Local\hermes\bin` from the User PATH.
  - Removed User env vars `HERMES_HOME` (`C:\Users\<USER>\AppData\Local\hermes`) and `HERMES_GIT_BASH_PATH` (`C:\Program Files\Git\bin\bash.exe`).
  - Deleted `Downloads\Hermes-Setup.exe` and `Temp\hermes-custody-*.txt`.
  - Left alone: `Downloads\Hermes 4 14B\*.gguf` (model weights, 28 GB). No services, scheduled tasks, firewall rules or uninstall registry entries existed. WSL distros could not be checked (they failed to start with ERROR_NO_SYSTEM_RESOURCES).
- **Result:** All the above removed. No Hermes processes were running.
- **Revert:** The data deletion cannot be undone. Reinstall Hermes from its installer, which recreates the folder, PATH entry and env vars. To restore the old User PATH, run `[Environment]::SetEnvironmentVariable('Path', (Get-Content "$env:TEMP\user_path_backup_hermes.txt" -Raw).Trim(), 'User')` (the backup is in Temp and may be cleaned up). Original `HERMES_HOME` and `HERMES_GIT_BASH_PATH` values are listed above.

### 2026-11-18: Replace the MSC-TARDIS and Iron Man Suit mods in My Summer Car with their public builds
- **Goal:** Test the public (dev-code-free) releases of msc-tardis v0.2.0 and msc-ironman v0.1.0 in place of the private dev builds, and check nothing dev-related is left in the game folder.
- **What was done:**
  - Moved (not deleted) `C:\Users\<USER>\Desktop\My Summer Car\Mods\MscTardis.dll`, `IronManSuit.dll`, `Mods\Assets\MscTardis`, `Mods\Assets\IronManSuit` and a stray nested `Mods\Assets\Assets\IronManSuit` into `C:\Users\<USER>\vscode_projects\msc-tardis\backups\game-mods-before-public\`.
  - Downloaded the GitHub release zips (`MscTardis-v0.2.0.zip`, `IronManSuit-v0.1.0.zip`) and extracted both into `Mods\`.
  - Left alone: `Mods\Config` settings for both mods, and the other mods.
- **Result:** Both installed. The two dlls contain no "dev" identifiers or strings, and no dev, log, source or bridge files are in either mod's folders (suspect-file scan found none). Not yet run in game.
- **Revert:** Delete the new `Mods\MscTardis.dll`, `Mods\IronManSuit.dll`, `Mods\Assets\MscTardis`, `Mods\Assets\IronManSuit`, then move the contents of `backups\game-mods-before-public\` back (`*.dll` into `Mods\`, `Assets\*` into `Mods\Assets\`, `Assets_nested_Assets` to `Mods\Assets\Assets`). Or `make play` in the private repos, which redeploys the dev builds.

### 2026-11-18: Install Playwright in a scratch venv to record demo video and build PDFs for the Fiverr gig
- **Goal:** Record a dashboard demo video and render two PDFs for the Fiverr gallery without changing the global Python install.
- **What was done:**
  - Created a Python venv inside the <AI-APP> scratchpad (`C:\Users\<USER>\AppData\Local\Temp\<AI-APP>\f9d0f3b866ead17d\dcb2a9ff-5375-40ca-9d59-e3bf97bc1aeb\scratchpad\venv`) and ran `pip install playwright` inside it only. No browser download; the installed Google Chrome was used.
  - Ran a throwaway copy of PayPulse on `localhost:8000` with generated sample data, then stopped it. Nothing was installed globally and no real project data was touched.
- **Result:** Succeeded. Outputs are in `C:\Users\<USER>\vscode_projects\fiverr\`.
- **Revert:** Delete the `venv` folder above (or let the scratchpad be cleaned up). Nothing else needs undoing.

### 2026-11-20: Authorize an SSH public key in ~/.ssh/authorized_keys
- **Goal:** Allow SSH logins to this account using the key from `C:\Users\<USER>\id_ed25519.pub` (comment `user@analysis-laptop`).
- **What was done:** `C:\Users\<USER>\.ssh\authorized_keys` did not exist. Created it containing that one ed25519 public key (`AAAAC3NzaC1lZDI1NTE5AAAAICEcSfCWtIQa6jnUOsBfFQgm/8niAf33Ka0wxIPHZ6lW`). No sshd service, firewall rule or sshd_config was changed.
- **Result:** File created. Whether it takes effect depends on an OpenSSH server running on the desktop (not checked or enabled).
- **Revert:** Delete `C:\Users\<USER>\.ssh\authorized_keys` (it did not exist before), or remove just that key's line.

### 2026-11-21: Contain suspected malware loader (fake "Microsoft Display Driver Manager" Run key + Python399 folder)
- **Goal:** Stop a persistent Python loader that popped `C:\Windows\Fonts\calc.exe` at logon (02:31 on 11/21) and keep a copy for analysis.
- **What was done:**
  - Removed HKCU Run value `Microsoft Display Driver Manager`. Original value: `"C:\Users\<USER>\AppData\Local\Programs\Python\Python399\python3\pythonw.exe" "C:\Users\<USER>\AppData\Local\Programs\Python\Python399\python3\exec.py"` (also saved in `C:\Users\<USER>\quarantine\2026-11-21-Python399\_run_value_backup.txt`).
  - Killed `pythonw.exe` PID 14688 (the running loader).
  - Copied (robocopy, 399 files, not yet deleted) `C:\Users\<USER>\AppData\Local\Programs\Python\Python399` to `C:\Users\<USER>\quarantine\2026-11-21-Python399\Python399`, with SHA256 list in `_sha256.csv`. `updater.cp313-win_amd64.pyd` SHA256 = FBB10BDFFBEE81893D16E533C9F4CF60CD029A4528617ABC9920CC09E1A3CD9D.
  - Failed: moving the original folder (access denied; VS Code PID 8664 and Antigravity `agy.exe` PID 8960 have it open). The original folder is still in place and inert (nothing launches it now).
  - Separately, the user blocked DNS to everything except <AI-APP>.
- **Result:** Persistence removed, process stopped, evidence copied. Original folder still to be removed once the two programs are closed.
- **Revert:** Not recommended (it is malware). To restore: re-add the Run value from the backup text file. The folder is unchanged in its original place.

### 2026-11-21: Suspend in-memory implant process (charmap.exe from C:\Windows\Fonts) and collect investigation evidence
- **Goal:** Contain the second half of the malware (a process running from memory) without destroying it, so memory can be dumped and analysed.
- **What was done:**
  - Found `C:\Windows\Fonts\charmap.exe` PID 21260 (started 02:31:28, parent was the killed `pythonw.exe` 14688). The file is not on disk. It loaded ws2_32/dnsapi/iphlpapi/mswsock. `Roaming\Microsoft\Internet Explorer\wd.pid` (created 11/7 12:29:00) contains 21260.
  - Suspended it with `NtSuspendProcess` (all 19 threads suspended). It was NOT killed, to preserve memory.
  - Copied to quarantine (`C:\Users\<USER>\quarantine\`): `2026-11-21-Python399\_wd.pid`, `_charmap_process.txt`; `2026-11-21-lichii\` holds `lichii-win64.zip`, `lichii-windows-x86_64.zip`, `opengl64x.dll`, `opengl64x_h.dll`, `t_id.txt` (copies only; originals still in Downloads and Roaming).
  - Analysed `updater.cp313-win_amd64.pyd` and `opengl64x.dll` statically in REA (no execution).
- **Result:** Process suspended and inert. Suspect delivery: `lichii-win64.zip` from `https://lichii.org/downloads/` on 11/7 11:59, with `opengl64x*.dll` and a modified `lichii.exe` dated 11/6 3:32 PM. Not yet cleaned up.
- **Revert:** Not applicable (containment). To end it for good: `Stop-Process -Id 21260 -Force`. To resume (not recommended): `NtResumeProcess` on PID 21260.

### 2026-11-21: Suspend second implant process (calc.exe from C:\Windows\Fonts) and triage memory dumps
- **Goal:** Contain the other in-memory process and identify the malware from the user's memory dumps.
- **What was done:**
  - Suspended `C:\Windows\Fonts\calc.exe` PID 21136 with `NtSuspendProcess` (14 of 15 threads suspended; it was still running before this). Not killed.
  - Copied the user's dumps `AppData\Local\Temp\calc.DMP` (SHA256 D932CF29...68EA) and `charmap.DMP` (SHA256 2A4A1ACB...1985) to `C:\Users\<USER>\quarantine\2026-11-21-dumps\`. Parsed them read-only with a Python script in the session scratchpad; extracted PE fragments to `extract_calc\` and `extract_charmap\` there.
- **Result:** calc.exe is a renamed cloudflared (Cloudflare Tunnel client, Go 1.27.4). charmap.exe is a Go infostealer/C2 client (browser cookies/logins, Exodus/MetaMask, BSC blockchain RPCs, six C2 domains). No live network connections while suspended.
- **Revert:** Not applicable (containment). To end both: `Stop-Process -Id 21136,21260 -Force`.
