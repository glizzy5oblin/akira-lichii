# akira-lichii: Trojanized "Lichii" Emulator → "Akira Remote" RAT + Cloudflare Tunnel

Evidence, analysis and response documents for a 14-day compromise of a Windows desktop by a Go remote-access trojan, delivered through a fake emulator download site.

| | |
|---|---|
| **Infected machine** | `VICTIM-PC`: Windows 10 Pro N 19045, account `User` (local administrator) |
| **Infected** | 2026-11-07 ≈12:00 CST, after downloading `lichii-win64.zip` from the fake site `lichii.org` |
| **Contained** | 2026-11-21 ≈00:30 CST: persistence removed, both malware processes suspended |
| **Exposure** | ~14 days of full remote control (screen, webcam, mic, keylogger, files, browser sessions) |
| **Analysis machine** | `analysis-laptop`, the analyst's laptop. Analysis was static only; the malware was never executed |
| **Status** | Containment done. Offline Windows triage (`08_windows_offline/`) and the string emulator are in progress |

## Table of contents

1. [Start here](#start-here)
2. [Safety and privacy](#safety-and-privacy)
3. [Incident overview](#incident-overview)
   - [The story in 60 seconds](#the-story-in-60-seconds)
   - [Key facts at a glance](#key-facts-at-a-glance)
   - [Still unknown](#still-unknown)
4. [Repository map](#repository-map)
5. [Folder reference](#folder-reference)
   - [Top-level files](#top-level-files)
   - [`01_report/`](#01_report-documents-for-people)
   - [`02_host_evidence/`](#02_host_evidence-raw-evidence-from-the-infected-desktop)
   - [`03_memory_dumps/`](#03_memory_dumps-full-process-memory)
   - [`04_analysis/`](#04_analysis-everything-derived-from-the-evidence)
   - [`05_archives/`](#05_archives-original-bundles)
   - [`06_other_devices/`](#06_other_devices-checks-of-everything-except-the-infected-windows)
   - [`07_work_in_progress/`](#07_work_in_progress-raw-working-files)
   - [`08_windows_offline/`](#08_windows_offline-artifacts-copied-off-the-infected-drive)
6. [Verifying integrity](#verifying-integrity)
7. [Methodology](#methodology)
8. [Maintenance conventions](#maintenance-conventions)

---

## Start here

| If you want to… | Open |
|---|---|
| Know **what to do now**, step by step | [`01_report/ACTION_CHECKLIST.md`](01_report/ACTION_CHECKLIST.md) |
| Understand **what the malware is and what it could do** | [`01_report/FINDINGS_2026-11-21.md`](01_report/FINDINGS_2026-11-21.md) |
| See **how the infection happened**, with timeline and hashes | [`01_report/INCIDENT_REPORT.md`](01_report/INCIDENT_REPORT.md) |
| Get **indicators to block or search for** | [`01_report/IOCs.txt`](01_report/IOCs.txt) |
| Read the **attacker's control-panel source code** | [`04_analysis/panel_source/`](04_analysis/panel_source/) |
| Read the **decompiled malware code** | [`04_analysis/ghidra/INDEX.tsv`](04_analysis/ghidra/INDEX.tsv) |
| Know whether **the server, the analysis laptop, the USB stick and the desktop's Linux drive** were touched | [`01_report/OTHER_DEVICES_2026-11-21.md`](01_report/OTHER_DEVICES_2026-11-21.md) |

## Safety and privacy

> **Read this before opening anything.**

### Live malware
- `05_archives/malware-samples_PASSWORD-infected.7z` contains real samples. **Never extract it on a machine you care about; use an isolated VM.**
- Wine is installed. Its binfmt handler was **disabled on 2026-11-21**, so a Windows `.exe` no longer launches by double-click, but `wine file.exe` would still run it.
- Every carved or extracted item ends in `.txt` or `.DO_NOT_RUN.bin` (or `.py`/`.java` for my own scripts), and nothing has the execute bit.
- `07_work_in_progress/rebuilt_images_DO_NOT_RUN/` holds the RAT's code rebuilt from memory. It is the real malware's code and is detectable as such. It isn't runnable as stored, and it's read-only with no execute bit, but never rename it to `.exe`, never run it through `wine`, and never upload it.

### Sensitivity of each folder

| Path | Sensitivity | Why |
|---|---|---|
| `02_host_evidence/browser/` | **Private, never upload** | Full browsing history |
| `03_memory_dumps/` | **Private, never upload** | Process memory: usernames, paths, project names |
| `05_archives/memory-dumps_SENSITIVE.7z` | **Private, never upload** | Encrypted copy of the dumps |
| `07_work_in_progress/` | **Private, never upload** | Rebuilt RAT images, and `memory_strings_PRIVATE/` with every string from both dumps |
| `06_other_devices/desktop_linux_nvme/`, `06_other_devices/home-server/` | **Private, never upload** | File paths, project names, login history |
| `08_windows_offline/` | **Private, never upload** | The infected drive's registry, event logs, PowerShell history and full file list |
| Original lichii.org zips (inside the samples archive), hashes, `01_report/IOCs.txt` | Safe to share with researchers | These are the only shareable items |

---

## Incident overview

### The story in 60 seconds

1. A Google search for "Lichii" led to `lichii.org`, a fake "official website". It served a **trojanized emulator zip** with two added DLLs (`opengl64x.dll`, `opengl64x_h.dll`) and a modified `lichii.exe`.
2. Running it planted a fake Python install (`%LOCALAPPDATA%\Programs\Python\Python399\`) and a Run key named **"Microsoft Display Driver Manager"**.
3. At every logon that loader started two programs from `C:\Windows\Fonts\` and deleted them from disk, so they ran from memory only:
   - **`charmap.exe`** is the **"Akira Remote" RAT**: a Go program obfuscated with garble. It has a stealer and a full web control panel built in.
   - **`calc.exe`** is a stock **cloudflared**. It published that panel on the internet through a Cloudflare quick tunnel, **with no password**.
4. The RAT finds its C2 servers through six domains and a **BNB Smart Chain smart contract** (a "blockchain dead drop").
5. Defender never detected it. It was found on 11/21, and both processes were suspended and dumped.

### Key facts at a glance

| | |
|---|---|
| **Delivery** | `https://lichii.org/downloads/lichii-win64.zip` (real project: `github.com/Frizti/Fritchii`) |
| **Persistence** | HKCU Run `Microsoft Display Driver Manager` → `Python399\python3\pythonw.exe exec.py` |
| **RAT** | "Akira Remote", Go + garble; runs as `C:\Windows\Fonts\charmap.exe` from memory |
| **Tunnel** | cloudflared as `C:\Windows\Fonts\calc.exe`, `tunnel --url http://localhost:49912` → `included-comprehensive-electro-organizations.trycloudflare.com` |
| **C2 domains** | `dpdc737.dpdatacenter.com`, `dongphucasian.com`, `waterseas.xyz`, `atomicplanets.cc`, `cosmicsky.cc`, `seaofstar.st` |
| **Dead drop** | BNB Smart Chain contract `0xF97CB22B8dBd52790493e962d4684B3FDB08A2Be` (`get()`) |
| **Exfil** | Telegram ("Full grab") and the C2 domains |
| **Also steals** | Windows Credential Manager (`vaultcli.dll`); bypasses Chrome App-Bound Encryption with a downloaded "ABE dumper" (`abe.a`) |
| **Defender** | Never detected anything; no exclusions or settings changed by the malware |
| **Other devices** | Desktop's Linux NVMe, analysis-laptop and the USB stick clean. home-server: no malware, but the desktop's SSH key (removed) and password (typed on infected Windows) were exposed |

### Still unknown

- What the attacker actually did during the 14 days. The dumps only cover the last session.
- Whether anything is staged on the desktop's disk. Run `01_report/DESKTOP_PREWIPE_CHECK.ps1.txt`. The cookie vault and keylog appear to be **RAM-only**, so there's probably no record of what was taken.
- The decoded blockchain config, and the `t_id.txt` encoding.
- What served `localhost:49912`.
- Whether anything on the desktop's Linux NVMe was *read* from Windows. Nothing was written from outside Linux, and reading would have needed admin rights plus a WSL mount, but reads leave no trace.
- Whether the router forwards port 22 to home-server from the internet (the stolen key was used via `<ROUTER-IP>` on 11/13).

---

## Repository map

```
akira-lichii/
├── README.md                 this file
├── MANIFEST.sha256           SHA-256 of every file
├── 01_report/                documents for people: checklist, findings, report, IOCs
├── 02_host_evidence/         raw evidence from the infected desktop (unchanged)
│   ├── system/  persistence/  network/  logs/  browser/  files/
├── 03_memory_dumps/          charmap.DMP (RAT), calc.DMP (cloudflared)
├── 04_analysis/              everything derived from the evidence
│   ├── host_triage/  panel_source/  go_metadata/  ghidra/  tools/
│   └── related_sample_joesandbox/
├── 05_archives/              original bundles from the desktop
├── 06_other_devices/         desktop_linux_nvme/  home-server/  analysis-laptop/  yumi_usb/
├── 07_work_in_progress/      raw working files for resuming the analysis
└── 08_windows_offline/       artifacts copied off the infected drive (triage in progress)
```

| Folder | Purpose | Sensitivity |
|---|---|---|
| `01_report/` | Read first: what happened and what to do | Shareable only for `IOCs.txt` |
| `02_host_evidence/` | Collected by script on 11/21 ≈00:30 | `browser/` private |
| `03_memory_dumps/` | Process memory of both malware processes | Private |
| `04_analysis/` | Triage, panel source, Go metadata, decompiled code, tools | Mixed; see folder notes |
| `05_archives/` | Encrypted bundles of samples and dumps | Live malware / private |
| `06_other_devices/` | Clean-checks of every other device | Private (desktop NVMe, home-server) |
| `07_work_in_progress/` | Working files, rebuilt images, full string dumps | Private |
| `08_windows_offline/` | Registry, event logs, MFT, Prefetch from the infected drive | Private |

---

## Folder reference

### Top-level files
| File | What it is |
|---|---|
| `README.md` | This file |
| `MANIFEST.sha256` | SHA-256 of every file. Check integrity with `sha256sum -c MANIFEST.sha256` |

### `01_report/`: documents for people

| File | What it is |
|---|---|
| `ACTION_CHECKLIST.md` | Ordered to-do list with checkboxes: isolate → sign out every session → back up data → wipe → report |
| `FINDINGS_2026-11-21.md` | Results of the memory-dump analysis: the malware's capabilities, what each dump contains, host corroboration, unknowns |
| `INCIDENT_REPORT.md` | The original report written during containment: timeline, infection chain, component hashes, exposure list |
| `IOCs.txt` | Domains, URL paths, IPs, hashes and host artifacts for blocking or searching. The bottom section (added 11/21) has the smart contract, panel name, routes and the cloudflared command line |
| `DESKTOP_PREWIPE_CHECK.ps1.txt` | **Read-only** PowerShell to run on the desktop before wiping (network unplugged; rename to `.ps1`). It lists files the RAT may have staged: `akdb*` temp folders, the `abe*` dumper, `Public\Downloads`, and its own folder. Output contains names and hashes only |
| `HOST_SYSTEM_CHANGELOG.md` | The **infected desktop's** change log (containment steps, kills, copies). It's separate from the analysis laptop's own system changelog |
| `OTHER_DEVICES_2026-11-21.md` | Checks of every other device: the desktop's **Linux NVMe** (clean), **home-server** (no malware; SSH key and password exposed), **analysis-laptop** (clean) and the **YUMI USB stick** (genuine boot path, one corrupted sector). Includes the Windows/Linux 6-hour clock explanation and follow-up steps |

### `02_host_evidence/`: raw evidence from the infected desktop

Unchanged. Collected by a PowerShell script on 11/21 around 00:30. Text files are PowerShell table output; `.csv` files are exports.

#### `system/`: the machine and its processes
| File | What it is |
|---|---|
| `processes.csv` / `processes.txt` | Every running process with PID, parent, start time, path and command line. Shows `Fonts\calc.exe` (21136) and `Fonts\charmap.exe` (21260) |
| `malware_process_threads.txt` | Thread states (all suspended) and loaded DLLs of the two malware processes |
| `installed_programs.txt` | Installed software from the registry uninstall keys |
| `winget_list.txt` | Packages known to winget |
| `defender_status.txt` | Defender state: real-time and tamper protection on, signatures current |
| `local_users.txt` | Local accounts and Administrators members. No attacker-added users |
| `whoami.txt` | The collecting account's user, groups and privileges |
| `systeminfo.txt` | OS build, hardware, hotfixes, network adapters |
| `boot_time.txt` | Last boot time (the clock was ~6 h off right after boot; see the incident report) |

#### `persistence/`: everything that can autostart
| File | What it is |
|---|---|
| `run_keys.txt` | HKCU/HKLM Run and RunOnce values (the malicious one had already been removed) |
| `startup_folders.txt` | Startup-folder items, including the content of `<startup-script>.vbs` |
| `scheduled_tasks.txt` | Every scheduled task with author and action |
| `services.txt` | Every service with state, start mode, account and binary path |
| `wmi_subscriptions.txt` | WMI event subscriptions (only the default SCM one) |
| `winlogon_ifeo_appinit.txt` | Winlogon shell/userinit, AppInit_DLLs, IFEO debuggers (IFEO read was access-denied) |
| `fonts_dir_exes.txt` | Check for `.exe` files in `C:\Windows\Fonts`. **Empty**, which confirms they were deleted after launch |

#### `network/`: connections and configuration
| File | What it is |
|---|---|
| `tcp.txt` / `udp.txt` | Sockets with owning PIDs. Shows cloudflared's metrics port `127.0.0.1:20241`, with nothing on `:49912` |
| `dns_cache.txt` | DNS resolver cache at collection time |
| `ipconfig.txt` | All adapters (Ethernet, Hyper-V, WSL, VMware, Tailscale) |
| `hosts_proxy.txt` | Hosts file (Docker entries only) and WinHTTP/IE proxy (none) |
| `firewall_profiles.txt` | Firewall profile enablement and defaults |
| `arp_routes.txt` | ARP table and routing table |

#### `logs/`: Windows event logs since 2026-11-05
CSV columns: time, ID, provider, level, message.

| File | What it is |
|---|---|
| `Microsoft-Windows-Windows_Defender_Operational.csv` | Defender events. No detections; 5007 config changes are routine |
| `Microsoft-Windows-PowerShell_Operational.csv`, `Windows_PowerShell.csv` | PowerShell engine and script-block events |
| `System.csv`, `Application.csv` | System and application logs |
| `system_service_installs_7045.txt` | Every service installed (event 7045), all from known vendors |
| `Microsoft-Windows-Bits-Client_Operational.csv` | Background downloads (Google/Microsoft only) |
| `OpenSSH_Operational.csv` | SSH server logins (only the owner's laptop key) |
| `Microsoft-Windows-TaskScheduler_Operational.csv` + `.unavailable.txt` | Task Scheduler log. **Empty**: no matching events |
| `System.unavailable.txt` | A note that some System event messages couldn't be rendered |

#### `browser/`: raw browser history databases (**private**)
| File | What it is |
|---|---|
| `chrome-Default-History.sqlite` | Chrome history and downloads. Holds the evidence of the lichii.org visit and download |
| `edge-Default-History.sqlite` | Edge history |
| `firefox-…-places.sqlite` (+ empty `-wal`) | Firefox history and bookmarks |

#### `files/`: file-system evidence
| File | What it is |
|---|---|
| `timeline_2026-11-07_1130-1300.txt` | Every file created or modified during the infection window, the core of the timeline |
| `downloads_listing_with_origin.csv` / `.txt` | Everything in Downloads with the URL it came from (Zone.Identifier) |
| `browser_history_findings.txt` | Relevant extracts from history: the Lichii searches, lichii.org, DS4Windows, the Reddit guide |
| `lichii_zip_listings.txt` | File lists and timestamps inside both lichii zips (shows the added DLLs) |
| `python399_listing.txt` | All 399 files of the fake Python loader folder |
| `hashes_all_samples.txt` | SHA-256 of every sample file |
| `t_id.txt.copy` | The malware's victim/install ID (`25....` + base64 of an obfuscated string, not decoded) |
| `wd.pid.copy` | The file where the RAT stores its own PID (21260) |

### `03_memory_dumps/`: full process memory

**Private.**

| File | What it is |
|---|---|
| `charmap.DMP` (58 MB) | Memory of the **Akira RAT**. Contains the whole program (rebuildable), the embedded panel HTML/CSS/JS, the C2 lists and a captured blockchain reply. **No stolen secrets were found in it** |
| `calc.DMP` (135 MB) | Memory of **cloudflared**. Its log shows the tunnel failing, then "Tunnel not found" from 00:13 to 00:15 CST. No proxied requests survive |

### `04_analysis/`: everything derived from the evidence

#### `host_triage/`: first pass, done on the desktop during containment
| File | What it is |
|---|---|
| `charmap_triage.txt`, `calc_triage.txt` | First parse of each dump: modules, injected-code candidates, URLs, IPs, domains, keywords |
| `mdparse.py.txt` | The minidump parser that produced those (kept as `.txt`) |
| `_processes_before.txt` | Processes captured before the kill: the loader and the two editors holding the folder |
| `_charmap_process.txt` | The RAT process record (PID 21260, parent 14688) |
| `_run_value_backup.txt` | The exact malicious Run-key value that was removed |
| `_sha256.csv` | Hashes of all 399 files in the Python399 loader folder |

#### `panel_source/`: the attacker's control panel, carved from RAT memory

Real source code: what the attacker saw and clicked. Read `app.js.txt` to see every feature.

| File | What it is |
|---|---|
| `main_panel.html.txt` | The panel page (`viewer.html`), titled "Akira Remote \| {{USER_HOST}}": menus for every feature |
| `app.js.txt` | The panel's JavaScript (5,996 lines): **91 API routes + 6 live websockets** covering screen, cam, mic, keys, passwords, tokens, the "Full grab → Telegram", hidden browsers with a cookie vault, files, registry, Defender, miner and SOCKS5 |
| `theme.css.txt` | The panel's stylesheet ("Akira operator UI") |
| `extra_01_1106c4e.txt` | A short piece of that same stylesheet |

#### `go_metadata/`: names recovered from the obfuscated RAT
| File | What it is |
|---|---|
| `charmap_functions_16738.txt` | Every function as `address name`. About 13,300 names were blanked by the obfuscator; the rest survive (Go standard library, libraries, the author's scrambled packages such as `HMxzL1ajr.(*AWD_c4Wf).GetCookies`) |
| `charmap_source_files.txt` | The program's source-file table (794 files, package folders scrambled) |
| `charmap_packages_by_file.txt` | The same files grouped by scrambled package, which shows what each package really is (`net/http`, `database/sql`, …) |
| `rebuilt_image_hashes.txt` | SHA-256 of the RAT image rebuilt from the dump, and of the copy with the Go function-table magic restored |

#### `ghidra/`: decompiled RAT code (Ghidra 12.2 pseudocode)
- **758 of 762 selected functions decompiled.** That's every function touching a malware-specific string, all named functions in the author's packages, and the unnamed author functions they call.
- `INDEX.tsv` is the map: address, recovered name, **why it was selected**, file name and status. Open it in a spreadsheet and filter by the `why_selected` column.
- Each function is one `<address>_<name>.c.txt` file. Its header says why it was picked.
- This is **pseudocode**, not original source. String literals are encrypted by the obfuscator, so many URLs and paths show up as decryption calls rather than text.

#### `tools/`: scripts used in this analysis (all read-only parsers)
| File | What it does |
|---|---|
| `rebuild_pe.py` | Rebuilds a mapped PE image from a minidump into a file-layout PE |
| `pclntab.py` | Reads the Go function table: names and source files |
| `carve.py` | Copies one memory region out of a minidump |
| `secrets_scan.py` | Scans extracted strings for tokens, keys, passwords and seeds, **printing masked values only** |
| `select_funcs.py` + `seeds.txt` | Finds which functions reference malware-specific strings and builds the decompile worklist |
| `DecompileList.java` | Ghidra script: labels recovered names, then decompiles the worklist (used for `ghidra/`) |
| `decode_literal_PgQmfsM1t.py` | Offline, by-hand reproduction of one garble-encrypted string (gives `GrabPasswordsOnly: ABE dumper execution failed`). Pure byte math; executes nothing |
| `TriageDecompile.java` | The first Ghidra script (needed full auto-analysis, which ran out of memory on the 3 GB analysis laptop) |

#### `related_sample_joesandbox/`: the same malware seen elsewhere

A public Joe Sandbox report on another victim's sample. It's the **same malware and operator**: the identical `exec.py` (same SHA-256), the same blockchain contract, Run value, C2 domains and "Akira Remote" panel passphrase. The bait was different: a fake `vscode-bootstrap.cmd` instead of the lichii emulator.

| File | What it is |
|---|---|
| `akira_potential_lead.html` | The saved report page (open it in a browser if you want; it's Joe Sandbox's page, not malware) |
| `akira_potential_lead.txt` | The same report as plain text, for searching |

What it adds: in that sandbox the RAT injected code into Chrome and Edge, uploaded a `DESKTOP-<host>_<user>.zip` to **GoFile**, and downloaded ffmpeg into a `remotevnc` folder. None of those traces appear in this incident's dumps or host evidence (see `01_report/IOCs.txt`).

### `05_archives/`: original bundles

| File | What it is |
|---|---|
| `malware-samples_PASSWORD-infected.7z` (229 MB) | **Live malware**: the lichii zips, DLLs, the loader. Encrypted, including its file list. **Do not extract here** |
| `memory-dumps_SENSITIVE.7z` (33 MB) | Encrypted copy of the memory dumps |
| `incident-report.zip` (7.7 MB) | An earlier bundle of the reports and evidence (65 files: README, IOCs, changelog and the evidence folders, without the dumps or archives) |

### `06_other_devices/`: checks of everything except the infected Windows

All read-only. The findings are written up in `01_report/OTHER_DEVICES_2026-11-21.md`. Logs are kept as `.txt`, and shell scripts as `.sh.txt`.

#### `desktop_linux_nvme/`: the desktop's CachyOS drive (NVMe SSD)
Checked from a live Arch USB.

| File | What it is |
|---|---|
| `01_main_check.log.txt` | First pass of `linux-nvme-check.sh`: disks, superblock, boot files changed, EFI hashes, firmware boot entries, `pacman -Qkk`, persistence, per-user keys, ctime histogram. Its "UNOWNED" list is a false positive (fixed in `02`) |
| `02_journal_pacman_packages_config.log.txt` | Journal boots, pacman log 11/07–11/21, altered-file details, truly unowned files, PAM/sudo/sshd config, kernels and systemd-boot vs packaged copies, all EFI-partition files. Its "1,215,672 outside a boot window" count is **wrong** (journal only keeps boots since 11/17; corrected in `06`) |
| `03_bootmgr_wtmp_unowned.log.txt` | Boot manager hashes, every Linux boot/shutdown from `wtmp`, the 7 unowned programs. **Cut short**: the live RAM disk filled up during the initramfs step (redone in `04`) |
| `04_initramfs_compare.log.txt` | Both initramfs images unpacked and compared file by file with the installed system; `/init` and hooks vs packaged. "NOT ON SYSTEM" fonts and keymaps are a symlink artefact |
| `05_secureboot_busybox_sessions.log.txt` | Secure Boot state (disabled), initramfs `busybox` vs packaged, Linux sessions parsed from `wtmp` |
| `06_changes_while_linux_not_running.log.txt` | **The key test**: files changed while Linux was not running, using clock-corrected sessions. 13 hits, all explained in `07` |
| `07_crashed_session_1120.log.txt` | Shows those 13 belong to the Linux session that crashed on 11/20 (unclean `.journal~`, app timestamps) |
| `08_efi_signatures.txt` | Authenticode check of every Microsoft program on the EFI partition, and of the copies in `C:\Windows\Boot`, against the firmware Secure Boot db: all valid |
| `scripts/` | The scripts that produced these (`linux-nvme-check.sh.txt`, `followup*.sh.txt`, `crashcheck.sh.txt`, `gaptest.py` with the corrected session list, `authenticode.py`) |
| `live_2026-11-21/` | **Live audit** of the running Linux after it was booted from its own drive (11/21 04:20 CST), over SSH in the owner's tmux pane. **Clean**: processes, hidden-process probe, sockets, connections, kernel modules, running programs vs packages, persistence, SSH keys and logins, sudo history, boot-file hashes. `README.txt` has the table and hardening notes (firewall off, SSH password logins on) |

#### `home-server/`
| File | What it is |
|---|---|
| `ssh_logins_and_keys.txt` | `authorized_keys` before and after removing `user@VICTIM-PC`, and every SSH login since 11/01 (server clock is NTP-synced) |
| `login_attribution.txt` | Each login from the desktop labelled **infected Windows / Linux / before infection** (both OSes share `<DESKTOP-LAN-IP>`) |
| `session_2026-11-13_via_router.txt` | What the 11/13 20:47–21:38 session with the stolen key did: <AI-APP> Code project work, no `sudo`, no system changes |

#### `analysis-laptop/` and `yumi_usb/`
| File | What it is |
|---|---|
| `analysis-laptop/checks.txt` | Record of the analysis laptop's checks (IOC names and hashes, Wine prefixes, processes, network, Tailscale, persistence, Chrome sync) |
| `yumi_usb/verification.txt` | Arch ISO checksum and signature, Ventoy EFI partition vs official 1.1.05, and the legacy-BIOS sector analysis (corruption, not tampering) |

### `07_work_in_progress/`: raw working files

Moved here from the temporary scratchpad on 2026-11-21. Everything needed to resume the analysis. All files are read-only with no execute bit. **Private.**

| Folder | What it holds |
|---|---|
| `rebuilt_images_DO_NOT_RUN/` | The RAT rebuilt from `charmap.DMP`, 19.3 MB each. `charmap_rebuilt` is the base for all analysis; `charmap_fixed` has the Go function-table magic restored (for tools that need it); `charmap_ungarbled` is GoStringUngarbler's output (only 3 strings patched) |
| `memory_strings_PRIVATE/` | Every string from both dumps: `*_a` ASCII, `*_w` UTF‑16, `*_all` both. `rpc.txt` is the blockchain `eth_call` request and the 941-byte reply. **Contains your username, PATH and folder names** |
| `go_metadata_raw/` | Raw `pclntab.py` output: functions, source files, packages (the tidy versions are in `04_analysis/go_metadata/`) |
| `ghidra_work/` | Ghidra logs, the decompile worklist and name tables, and before/after hash lists from the folder reorganization |
| `carved_regions/` | The three harmless hidden DLLs carved from the dumps (Windows message-table resources, no code) |
| `string_emulator/` | Work in progress on `04_analysis/tools/emulate_strings.py`: the static call-site survey, a trace/debug script and the failed self-test output. Paused; see FINDINGS section 7 |
| `other_devices_scratch/` | Working files from the other-device checks: `scripts/tmux_run.sh.txt` (runs a command in the live USB's tmux pane so you can watch), the failed OpenSSL Authenticode attempt, `ssh_known_hosts/` for the live USB and home-server, `arch_iso_signature/` (the `.sig`, official `sha256sums.txt` and the keyring used), `efi_binaries_from_desktop/` (the desktop's Microsoft boot programs and the firmware `db`/`KEK`, checked in `06_other_devices/desktop_linux_nvme/08_efi_signatures.txt`), `ventoy_1.1.05_reference/` (the official release tarball, its hash list, the official `core.img`, and the file-by-file hash lists for the stick and the release), `yumi_stick/stick_core_sectors1-2047.bin` (the stick's BIOS boot code with the corrupted sector 34). The final scripts and logs are in `06_other_devices/` |
| `windows_offline_tools/` | Parsers for the offline Windows triage (in progress): `wintime.py` (clock-skew correction), `evtx2jsonl.py`, `evtx_triage.py`, `prefetch.py`, and `requirements.txt` to recreate their Python environment. The raw artifacts they read are in `08_windows_offline/` |

**Not kept** (easy to recreate):
- The Ventoy files unpacked from the release tarball (unpack it again to compare).
- The `dissect` Python environment (see `windows_offline_tools/requirements.txt`).
- The GoStringUngarbler clone (`git clone https://github.com/mandiant/gostringungarbler`, commit `1db869e`) and its Python venv (`python3 -m venv --system-site-packages`, then `pip install lief`).

### `08_windows_offline/`: artifacts copied off the infected drive

Collected 2026-11-21 from the live Arch USB with the drive mounted read-only; nothing on it was changed. Triage in progress. **Private.** See `08_windows_offline/README.txt`.

| Path | What it is |
|---|---|
| `col/raw/` | Event logs (397), Prefetch, SRUM, Amcache, the SOFTWARE and SYSTEM hives, scheduled tasks, the user's NTUSER.DAT / UsrClass.dat, PowerShell history, Recent, Startup, Defender support logs. **SAM/SECURITY not collected** |
| `col/MFT`, `col/UsnJrnl_J.xz` | The NTFS file table and change journal (decompress the journal with `xz -dk` before parsing) |
| `col/SHA256SUMS` | Hashes taken on the live USB at collection time |
| `parsed/` | Event logs as JSONL, per-log date ranges, boots and clock changes, IOC hits, event-log triage, Prefetch runs |

---

## Verifying integrity

From the repo root:

```sh
sha256sum -c MANIFEST.sha256 | grep -v ': OK$'   # prints only failures
```

Regenerate the manifest after any change, including edits to this README.

## Methodology

Everything was **static**: files were read, never run.

1. The RAT was rebuilt from `charmap.DMP` into a PE file, kept outside the evidence folders.
2. REA read its Go build information, which had been wiped.
3. A custom parser recovered the function table, whose magic had been tampered with.
4. Ghidra 12.2 decompiled the selected functions in headless mode, without full analysis.

Panel source and stylesheet were carved byte-for-byte from memory. Secret scans print masked values only.

## Maintenance conventions

- Update this README, `01_report/FINDINGS_2026-11-21.md` and `MANIFEST.sha256` whenever findings change.
- Keep carved or extracted artifacts named `.txt` or `.DO_NOT_RUN.bin`, with no execute bit.
- Never upload the private folders listed under [Safety and privacy](#safety-and-privacy).
- Log system-level changes to the analysis laptop in its own system changelog; the desktop's changes live in `01_report/HOST_SYSTEM_CHANGELOG.md`.
