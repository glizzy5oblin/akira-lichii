# akira-lichii: trojanized "Lichii" emulator → "Akira Remote" RAT

Evidence, analysis and response documents for a 14-day compromise of a Windows desktop. A Go remote-access trojan arrived through a fake emulator download site and was exposed to the internet through a Cloudflare tunnel.

| | |
|---|---|
| **Infected machine** | `VICTIM-PC`: Windows 10 Pro N 19045, account `User` (local administrator) |
| **Infected** | 2026-11-07 ≈12:00 CST, after downloading `lichii-win64.zip` from the fake site `lichii.org` |
| **Contained** | 2026-11-21 ≈00:30 CST: persistence removed, both malware processes suspended |
| **Exposure** | ~14 days of full remote control: screen, webcam, mic, keylogger, files, browser sessions |
| **Analysis** | Static only, on `analysis-laptop`. The malware was never executed |
| **Status** | Containment done. Offline Windows triage: first pass done (FINDINGS §10), a few registry and history artifacts remain. String-decryption emulator paused (FINDINGS §7) |

**Contents:** [Start here](#start-here) · [Safety](#safety) · [Incident summary](#incident-summary) · [Layout](#layout) · [Folder reference](#folder-reference) · [Working with this repo](#working-with-this-repo)

---

## Start here

| If you want to… | Open |
|---|---|
| Know **what to do now**, step by step | [`01_report/ACTION_CHECKLIST.md`](01_report/ACTION_CHECKLIST.md) |
| Understand **what the malware is and can do** | [`01_report/FINDINGS_2026-11-21.md`](01_report/FINDINGS_2026-11-21.md) |
| See **how the infection happened**: timeline, hashes | [`01_report/INCIDENT_REPORT.md`](01_report/INCIDENT_REPORT.md) |
| Get **indicators to block or search for** | [`01_report/IOCs.txt`](01_report/IOCs.txt) |
| Check whether **other devices** were touched (server, laptop, USB stick, Linux drive) | [`01_report/OTHER_DEVICES_2026-11-21.md`](01_report/OTHER_DEVICES_2026-11-21.md) |
| Read the **attacker's control-panel source** | [`04_analysis/panel_source/`](04_analysis/panel_source/) |
| See the **panel rendered** with fake data | [`04_analysis/panel_render/`](04_analysis/panel_render/) |
| Read the **decompiled malware code** | [`04_analysis/ghidra/INDEX.tsv`](04_analysis/ghidra/INDEX.tsv) |

---

## Safety

> **Read this before opening anything.**

### Live malware

- `05_archives/malware-samples_PASSWORD-infected.7z` holds real samples. **Extract it only in an isolated VM, never on a machine you care about.**
- Wine is installed. Its binfmt handler was **disabled on 2026-11-21**, so double-clicking a `.exe` no longer launches it, but `wine file.exe` still would.
- Every carved or extracted item ends in `.txt` or `.DO_NOT_RUN.bin` (or `.py`/`.java` for my own scripts). Nothing has the execute bit.
- `07_work_in_progress/rebuilt_images_DO_NOT_RUN/` is the RAT's real code rebuilt from memory and is detectable as malware. It isn't runnable as stored. Never rename it to `.exe`, run it through `wine`, or upload it.

---

## Incident summary

### The story in 60 seconds

1. A Google search for "Lichii" led to `lichii.org`, a fake "official website". It served a **trojanized emulator zip** with two added DLLs (`opengl64x.dll`, `opengl64x_h.dll`) and a modified `lichii.exe`.
2. Running it planted a fake Python install (`%LOCALAPPDATA%\Programs\Python\Python399\`) and a Run key named **"Microsoft Display Driver Manager"**.
3. At every logon the loader started two genuine Windows programs, `calc.exe` and `charmap.exe`, replaced their code in memory (process hollowing) and disguised their paths as `C:\Windows\Fonts\…`. No file was ever written to Fonts.
   - **`charmap.exe`** is the **"Akira Remote" RAT**: a Go program obfuscated with garble, with a stealer and a full web control panel built in.
   - **`calc.exe`** is a stock **cloudflared**. It published that panel on the internet through a Cloudflare quick tunnel, **with no password**.
4. The RAT finds its C2 servers through six domains and a **BNB Smart Chain smart contract** (a "blockchain dead drop").
5. At logon it copied the browsers' password, cookie, autofill and history databases to `%TEMP%\akdb*` and deleted the copies within milliseconds. The disk shows this for the last logon only; earlier logons are outside the change journal.
6. Defender never raised a detection. The malware was found on 11/21, and both processes were suspended and dumped.

### Key facts

| | |
|---|---|
| **Delivery** | `https://lichii.org/downloads/lichii-win64.zip` (the real project is `github.com/Frizti/Fritchii`) |
| **Persistence** | HKCU Run `Microsoft Display Driver Manager` → `Python399\python3\pythonw.exe exec.py` |
| **RAT** | "Akira Remote", Go + garble, inside a hollowed `System32\charmap.exe` that shows as `C:\Windows\Fonts\charmap.exe` |
| **Tunnel** | cloudflared inside a hollowed `System32\calc.exe` (shows as `C:\Windows\Fonts\calc.exe`), run as `tunnel --url http://localhost:49912` → `included-comprehensive-electro-organizations.trycloudflare.com` |
| **C2 domains** | `dpdc737.dpdatacenter.com`, `dongphucasian.com`, `waterseas.xyz`, `atomicplanets.cc`, `cosmicsky.cc`, `seaofstar.st` |
| **Dead drop** | BNB Smart Chain contract `0xF97CB22B8dBd52790493e962d4684B3FDB08A2Be` (`get()`) |
| **Exfiltration** | Telegram ("Full grab") and the C2 domains |
| **Also steals** | Windows Credential Manager (`vaultcli.dll`). Bypasses Chrome App-Bound Encryption with a downloaded "ABE dumper" (`abe.a`) |
| **Defender** | No detection, and the malware changed no exclusions or settings. Its behaviour monitor did mark the loader's child processes as "tainted" (FINDINGS §10) |
| **Other devices** | Desktop's Linux NVMe, analysis-laptop and the USB stick: clean. home-server: no malware, but the desktop's SSH key (since removed) and a password typed on the infected Windows were exposed |

### Still unknown

**Attacker activity**
- What the attacker did during the 14 days. The dumps cover only the last session, the change journal only its last 7.5 hours, and SRUM kept no network data.

**On the desktop**
- Whether anything is staged on disk. The offline file table shows no Fonts executable and no leftover `akdb*` folder, but run `01_report/DESKTOP_PREWIPE_CHECK.ps1.txt` to be thorough. The cookie vault and keylog appear to be **RAM-only**. The logon grab of 17 browser databases is visible on disk, but what was read from them isn't.
- What the loader's short-lived `cmd.exe`, `chrome.exe` (probably injected) and `dllhost.exe` did at each logon, and where the `python.zip` it unpacks over itself comes from.
- What served `localhost:49912`.

**The malware's internals**
- The decoded blockchain config and the `t_id.txt` encoding.

**Other devices**
- Whether anything on the desktop's Linux NVMe was *read* from Windows. Nothing was written from outside Linux, and reading would have needed admin rights plus a WSL mount, but reads leave no trace.
- Whether the router forwards port 22 to home-server from the internet. The stolen key was used via `<ROUTER-IP>` on 11/13.

---

## Layout

```
akira-lichii/
├── README.md                 this file
├── MANIFEST.sha256           SHA-256 of every file
├── 01_report/                documents for people: checklist, findings, report, IOCs
├── 02_host_evidence/         raw evidence from the infected desktop (unchanged)
│   └── system/  persistence/  network/  logs/  browser/  files/
├── 03_memory_dumps/          charmap.DMP (RAT), calc.DMP (cloudflared)
├── 04_analysis/              everything derived from the evidence
│   └── host_triage/  panel_source/  panel_render/  go_metadata/  ghidra/  tools/
│       related_sample_joesandbox/
├── 05_archives/              original bundles from the desktop
├── 06_other_devices/         desktop_linux_nvme/  home-server/  analysis-laptop/  yumi_usb/
├── 07_work_in_progress/      raw working files for resuming the analysis
└── 08_windows_offline/       artifacts copied off the infected drive
```

| Folder | Purpose | Sensitivity |
|---|---|---|
| `01_report/` | Read first: what happened and what to do | Private, except `IOCs.txt` |
| `02_host_evidence/` | Collected by script on 11/21 ≈00:30 | Private: `browser/` is full browsing history |
| `03_memory_dumps/` | Process memory of both malware processes (usernames, paths, project names) | **Private** |
| `04_analysis/` | Triage, panel source, Go metadata, decompiled code, tools | Mixed; see folder notes |
| `05_archives/` | Encrypted bundles of samples and dumps | **Live malware** / private |
| `06_other_devices/` | Clean-checks of every other device | **Private**: `desktop_linux_nvme/` and `home-server/` hold file paths, project names and login history |
| `07_work_in_progress/` | Rebuilt RAT images, every string from both dumps, scratch | **Private** |
| `08_windows_offline/` | Registry, event logs, PowerShell history, MFT, Prefetch from the infected drive | **Private** |

---

## Folder reference

Each section opens to show its files.

<details>
<summary><b>Top-level files</b></summary>

| File | What it is |
|---|---|
| `README.md` | This file |
| `MANIFEST.sha256` | SHA-256 of every file (see [Verifying integrity](#verifying-integrity)) |
| `.gitignore` | Keeps live malware and large binaries out of version control |

</details>

<details>
<summary><b><code>01_report/</code>: documents for people</b></summary>

| File | What it is |
|---|---|
| `ACTION_CHECKLIST.md` | Ordered to-do list with checkboxes: isolate → sign out every session → back up data → wipe → report |
| `FINDINGS_2026-11-21.md` | Memory-dump analysis: the malware's capabilities, what each dump contains, host corroboration, unknowns, Ghidra results, offline triage (§10) |
| `INCIDENT_REPORT.md` | The original containment report: timeline, infection chain, component hashes, exposure list |
| `IOCs.txt` | Domains, URL paths, IPs, hashes and host artifacts. The bottom section (added 11/21) has the smart contract, panel name, routes and cloudflared command line |
| `DESKTOP_PREWIPE_CHECK.ps1.txt` | **Read-only** PowerShell to run on the desktop before wiping, with the network unplugged (rename to `.ps1`). Lists files the RAT may have staged: `akdb*` temp folders, the `abe*` dumper, `Public\Downloads`, its own folder. Output is names and hashes only |
| `HOST_SYSTEM_CHANGELOG.md` | The **infected desktop's** change log: containment steps, kills, copies. Separate from the analysis laptop's own system changelog |
| `OTHER_DEVICES_2026-11-21.md` | Checks of every other device: Linux NVMe (clean), home-server (no malware; SSH key and password exposed), analysis-laptop (clean), YUMI USB stick (genuine boot path, one corrupted sector). Includes the 6-hour Windows/Linux clock explanation and follow-ups |

</details>

<details>
<summary><b><code>02_host_evidence/</code>: raw evidence from the infected desktop</b></summary>

Unchanged. Collected by a PowerShell script on 11/21 around 00:30. Text files are PowerShell table output; `.csv` files are exports.

**`system/`: the machine and its processes**

| File | What it is |
|---|---|
| `processes.csv` / `.txt` | Every running process with PID, parent, start time, path, command line. Shows `Fonts\calc.exe` (21136) and `Fonts\charmap.exe` (21260) |
| `malware_process_threads.txt` | Thread states (all suspended) and loaded DLLs of the two malware processes |
| `installed_programs.txt`, `winget_list.txt` | Installed software (registry uninstall keys) and winget packages |
| `defender_status.txt` | Real-time and tamper protection on, signatures current |
| `local_users.txt` | Local accounts and Administrators members. No attacker-added users |
| `whoami.txt`, `systeminfo.txt` | Collecting account's groups and privileges; OS build, hardware, hotfixes, adapters |
| `boot_time.txt` | Last boot time (the clock was ~6 h off right after boot; see the incident report) |

**`persistence/`: everything that can autostart**

| File | What it is |
|---|---|
| `run_keys.txt` | HKCU/HKLM Run and RunOnce values (the malicious one was already removed) |
| `startup_folders.txt` | Startup-folder items, including the content of `<startup-script>.vbs` |
| `scheduled_tasks.txt`, `services.txt` | Every task (author, action) and every service (state, account, binary path) |
| `wmi_subscriptions.txt` | WMI event subscriptions (only the default SCM one) |
| `winlogon_ifeo_appinit.txt` | Winlogon shell/userinit, AppInit_DLLs, IFEO debuggers (IFEO read was access-denied) |
| `fonts_dir_exes.txt` | `.exe` files in `C:\Windows\Fonts`. **Empty**: the processes were hollowed System32 programs with disguised paths (FINDINGS §10) |

**`network/`: connections and configuration**

| File | What it is |
|---|---|
| `tcp.txt` / `udp.txt` | Sockets with owning PIDs. Shows cloudflared's metrics port `127.0.0.1:20241` and nothing on `:49912` |
| `dns_cache.txt` | DNS resolver cache at collection time |
| `ipconfig.txt` | All adapters (Ethernet, Hyper-V, WSL, VMware, Tailscale) |
| `hosts_proxy.txt` | Hosts file (Docker entries only) and WinHTTP/IE proxy (none) |
| `firewall_profiles.txt`, `arp_routes.txt` | Firewall profile defaults; ARP and routing tables |

**`logs/`: Windows event logs since 2026-11-05** (CSV: time, ID, provider, level, message)

| File | What it is |
|---|---|
| `Microsoft-Windows-Windows_Defender_Operational.csv` | No detections; 5007 config changes are routine |
| `Microsoft-Windows-PowerShell_Operational.csv`, `Windows_PowerShell.csv` | PowerShell engine and script-block events |
| `System.csv`, `Application.csv` | System and application logs |
| `system_service_installs_7045.txt` | Every service installed (event 7045), all from known vendors |
| `Microsoft-Windows-Bits-Client_Operational.csv` | Background downloads (Google/Microsoft only) |
| `OpenSSH_Operational.csv` | SSH server logins (only the owner's laptop key) |
| `Microsoft-Windows-TaskScheduler_Operational.csv` | **Empty**: no matching events (see its `.unavailable.txt`) |
| `System.unavailable.txt` | Note that some System event messages couldn't be rendered |

**`browser/`: raw history databases (private)**

| File | What it is |
|---|---|
| `chrome-Default-History.sqlite` | Chrome history and downloads. Holds the evidence of the lichii.org visit and download |
| `edge-Default-History.sqlite` | Edge history |
| `firefox-…-places.sqlite` (+ empty `-wal`) | Firefox history and bookmarks |

**`files/`: file-system evidence**

| File | What it is |
|---|---|
| `timeline_2026-11-07_1130-1300.txt` | Every file created or modified during the infection window: the core of the timeline |
| `downloads_listing_with_origin.csv` / `.txt` | Everything in Downloads with its source URL (Zone.Identifier) |
| `browser_history_findings.txt` | Relevant history extracts: the Lichii searches, lichii.org, DS4Windows, the Reddit guide |
| `lichii_zip_listings.txt` | File lists and timestamps inside both lichii zips (shows the added DLLs) |
| `python399_listing.txt` | All 399 files of the fake Python loader folder |
| `hashes_all_samples.txt` | SHA-256 of every sample file |
| `t_id.txt.copy` | The malware's victim/install ID (`25....` + base64 of an obfuscated string, not decoded) |
| `wd.pid.copy` | The file where the RAT stores its own PID (21260) |

</details>

<details>
<summary><b><code>03_memory_dumps/</code>: full process memory</b> (private)</summary>

| File | What it is |
|---|---|
| `charmap.DMP` (58 MB) | Memory of the **Akira RAT**: the whole program (rebuildable), the embedded panel HTML/CSS/JS, the C2 lists and a captured blockchain reply. **No stolen secrets were found in it** |
| `calc.DMP` (135 MB) | Memory of **cloudflared**. Its log shows the tunnel failing, then "Tunnel not found" from 00:13 to 00:15 CST. No proxied requests survive |

</details>

<details>
<summary><b><code>04_analysis/</code>: everything derived from the evidence</b></summary>

**`host_triage/`: first pass, done on the desktop during containment**

| File | What it is |
|---|---|
| `charmap_triage.txt`, `calc_triage.txt` | First parse of each dump: modules, injected-code candidates, URLs, IPs, domains, keywords |
| `mdparse.py.txt` | The minidump parser that produced those |
| `_processes_before.txt` | Processes captured before the kill: the loader and the two editors holding the folder |
| `_charmap_process.txt` | The RAT process record (PID 21260, parent 14688) |
| `_run_value_backup.txt` | The exact malicious Run-key value that was removed |
| `_sha256.csv` | Hashes of all 399 files in the Python399 loader folder |

**`panel_source/`: the attacker's control panel, carved from RAT memory**

Real source: what the attacker saw and clicked. Read `app.js.txt` to see every feature.

| File | What it is |
|---|---|
| `main_panel.html.txt` | The panel page (`viewer.html`), titled "Akira Remote \| {{USER_HOST}}", with menus for every feature |
| `app.js.txt` | The panel's JavaScript (5,996 lines): **91 API routes + 6 live websockets** covering screen, cam, mic, keys, passwords, tokens, "Full grab → Telegram", hidden browsers with a cookie vault, files, registry, Defender, miner and SOCKS5 |
| `theme.css.txt` | The stylesheet. Actually the panel's `viewer.css` |
| `extra_01_1106c4e.txt` | The panel's real `theme.css` (design tokens) |

**`panel_render/`: the carved panel, running on fake data**

Everything here uses FAKE data (`example.test`, `203.0.113.x`, `FAKE-…` strings). The mock server binds `127.0.0.1` and makes no outbound connections; only the Font Awesome icon CSS comes from cdnjs. Has its own `README.md`.

| Path | What it is |
|---|---|
| `mock/server.mjs` | Serves the carved panel from `../panel_source` and answers `/api/*` with fake data. No websockets |
| `mock/shoot.mjs` | Headless Chrome via CDP: opens each tool and writes PNGs to `screenshots/` |
| `screenshots/` | One PNG per panel tool (main, sysinfo, task manager, files, keylogger, passwords, registry, Defender, …) |
| `panel_view.html`, `theme.css`, `panel_screenshot.png` | Older JS-less static copy. The mock is better |

Run it with `node mock/server.mjs &`, then open `http://127.0.0.1:8765/`, or run `node mock/shoot.mjs` to regenerate the screenshots.

**`go_metadata/`: names recovered from the obfuscated RAT**

| File | What it is |
|---|---|
| `charmap_functions_16738.txt` | Every function as `address name`. About 13,300 names were blanked by the obfuscator. The rest survive: Go standard library, libraries, the author's scrambled packages such as `HMxzL1ajr.(*AWD_c4Wf).GetCookies` |
| `charmap_source_files.txt` | The source-file table (794 files, package folders scrambled) |
| `charmap_packages_by_file.txt` | The same files grouped by scrambled package, showing what each really is (`net/http`, `database/sql`, …) |
| `rebuilt_image_hashes.txt` | SHA-256 of the RAT image rebuilt from the dump, and of the copy with the Go function-table magic restored |

**`ghidra/`: decompiled RAT code** (Ghidra 12.2 pseudocode)

- **758 of 762 selected functions decompiled**: every function touching a malware-specific string, all named functions in the author's packages, and the unnamed author functions they call.
- `INDEX.tsv` is the map: address, recovered name, **why it was selected**, file name, status. Open it in a spreadsheet and filter on `why_selected`.
- Each function is one `<address>_<name>.c.txt` file whose header says why it was picked.
- This is **pseudocode**, not original source. The obfuscator encrypts string literals, so many URLs and paths appear as decryption calls rather than text.

**`tools/`: scripts used in this analysis** (read-only parsers; none execute malware)

| File | What it does |
|---|---|
| `rebuild_pe.py` | Rebuilds a mapped PE image from a minidump into a file-layout PE |
| `pclntab.py` | Reads the Go function table: names and source files |
| `carve.py` | Copies one memory region out of a minidump |
| `secrets_scan.py` | Scans extracted strings for tokens, keys, passwords and seeds, **printing masked values only** |
| `select_funcs.py` + `seeds.txt` | Finds which functions reference malware-specific strings and builds the decompile worklist |
| `DecompileList.java` | Ghidra script: labels recovered names, then decompiles the worklist (used for `ghidra/`) |
| `TriageDecompile.java` | The first Ghidra script. It needed full auto-analysis, which ran out of memory on the 3 GB laptop |
| `decode_literal_PgQmfsM1t.py` | Hand reproduction of one garble-encrypted string (gives `GrabPasswordsOnly: ABE dumper execution failed`). Pure byte math |
| `emulate_strings.py` | Attempt at automated string decryption. Paused; working files in `07_work_in_progress/string_emulator/` (FINDINGS §7) |

**`related_sample_joesandbox/`: the same malware seen elsewhere**

A public Joe Sandbox report on another victim's sample: the **same malware and operator**. It has the identical `exec.py` (same SHA-256), blockchain contract, Run value, C2 domains and "Akira Remote" panel passphrase. Only the bait differed: a fake `vscode-bootstrap.cmd` instead of the lichii emulator.

| File | What it is |
|---|---|
| `akira_potential_lead.html` | The saved report page. It's Joe Sandbox's page, not malware |
| `akira_potential_lead.txt` | The same report as plain text, for searching |

In that sandbox the RAT injected code into Chrome and Edge, uploaded a `DESKTOP-<host>_<user>.zip` to **GoFile**, and downloaded ffmpeg into a `remotevnc` folder. None of those traces appear in this incident's dumps or host evidence (see `01_report/IOCs.txt`).

</details>

<details>
<summary><b><code>05_archives/</code>: original bundles</b></summary>

| File | What it is |
|---|---|
| `malware-samples_PASSWORD-infected.7z` (229 MB) | **Live malware**: the lichii zips, DLLs, the loader. Encrypted, including its file list. **Do not extract here** |
| `memory-dumps_SENSITIVE.7z` (33 MB) | Encrypted copy of the memory dumps |
| `incident-report.zip` (7.7 MB) | Earlier bundle of the reports and evidence: 65 files (README, IOCs, changelog, evidence folders; no dumps or archives) |

</details>

<details>
<summary><b><code>06_other_devices/</code>: checks of everything except the infected Windows</b></summary>

All read-only. Findings are written up in `01_report/OTHER_DEVICES_2026-11-21.md`. Logs are kept as `.txt` and shell scripts as `.sh.txt`.

**`desktop_linux_nvme/`: the desktop's CachyOS drive (NVMe SSD)**, checked from a live Arch USB

| File | What it is |
|---|---|
| `01_main_check.log.txt` | First pass of `linux-nvme-check.sh`: disks, superblock, changed boot files, EFI hashes, firmware boot entries, `pacman -Qkk`, persistence, per-user keys, ctime histogram. Its "UNOWNED" list is a false positive (fixed in `02`) |
| `02_journal_pacman_packages_config.log.txt` | Journal boots, pacman log 11/07–11/21, altered files, truly unowned files, PAM/sudo/sshd config, kernels, EFI files. Its "1,215,672 outside a boot window" count is **wrong** (the journal only keeps boots since 11/17; corrected in `06`) |
| `03_bootmgr_wtmp_unowned.log.txt` | Boot manager hashes, every Linux boot/shutdown from `wtmp`, the 7 unowned programs. **Cut short** when the live RAM disk filled during the initramfs step (redone in `04`) |
| `04_initramfs_compare.log.txt` | Both initramfs images unpacked and compared file by file with the installed system. "NOT ON SYSTEM" fonts and keymaps are a symlink artefact |
| `05_secureboot_busybox_sessions.log.txt` | Secure Boot state (disabled), initramfs `busybox` vs packaged, Linux sessions from `wtmp` |
| `06_changes_while_linux_not_running.log.txt` | **The key test**: files changed while Linux was not running, using clock-corrected sessions. 13 hits, all explained in `07` |
| `07_crashed_session_1120.log.txt` | Shows those 13 belong to the Linux session that crashed on 11/20 (unclean `.journal~`, app timestamps) |
| `08_efi_signatures.txt` | Authenticode check of every Microsoft program on the EFI partition, and the copies in `C:\Windows\Boot`, against the firmware Secure Boot db: all valid |
| `scripts/` | The scripts behind these: `linux-nvme-check.sh.txt`, `followup*.sh.txt`, `crashcheck.sh.txt`, `gaptest.py` (with the corrected session list), `authenticode.py` |
| `live_2026-11-21/` | **Live audit** of the running Linux, booted from its own drive (11/21 04:20 CST) and driven over SSH in the owner's tmux pane. **Clean**: processes, hidden-process probe, sockets, connections, kernel modules, programs vs packages, persistence, SSH keys and logins, sudo history, boot-file hashes. `README.txt` has the table and hardening notes (firewall off, SSH password logins on) |

**`home-server/`**

| File | What it is |
|---|---|
| `ssh_logins_and_keys.txt` | `authorized_keys` before and after removing `user@VICTIM-PC`, and every SSH login since 11/01 (server clock is NTP-synced) |
| `login_attribution.txt` | Each login from the desktop labelled **infected Windows / Linux / before infection** (both OSes share `<DESKTOP-LAN-IP>`) |
| `session_2026-11-13_via_router.txt` | What the 11/13 20:47–21:38 session with the stolen key did: coding-assistant project work, no `sudo`, no system changes |

**`analysis-laptop/` and `yumi_usb/`**

| File | What it is |
|---|---|
| `analysis-laptop/checks.txt` | The analysis laptop's checks: IOC names and hashes, Wine prefixes, processes, network, Tailscale, persistence, Chrome sync |
| `yumi_usb/verification.txt` | Arch ISO checksum and signature, Ventoy EFI partition vs official 1.1.05, legacy-BIOS sector analysis (corruption, not tampering) |

</details>

<details>
<summary><b><code>07_work_in_progress/</code>: raw working files</b> (private)</summary>

Moved here from the temporary scratchpad on 2026-11-21. Everything needed to resume the analysis. All files are read-only with no execute bit.

| Folder | What it holds |
|---|---|
| `rebuilt_images_DO_NOT_RUN/` | The RAT rebuilt from `charmap.DMP`, 19.3 MB each. `charmap_rebuilt` is the base for all analysis; `charmap_fixed` has the Go function-table magic restored; `charmap_ungarbled` is GoStringUngarbler's output (only 3 strings patched) |
| `memory_strings_PRIVATE/` | Every string from both dumps: `*_a` ASCII, `*_w` UTF‑16, `*_all` both. `rpc.txt` is the blockchain `eth_call` request and the 941-byte reply. **Contains your username, PATH and folder names** |
| `go_metadata_raw/` | Raw `pclntab.py` output: functions, source files, packages (tidy versions are in `04_analysis/go_metadata/`) |
| `ghidra_work/` | Ghidra logs, the decompile worklist and name tables, before/after hash lists from the folder reorganization |
| `carved_regions/` | The three harmless hidden DLLs carved from the dumps (Windows message-table resources, no code) |
| `string_emulator/` | Paused work on `04_analysis/tools/emulate_strings.py`: static call-site survey, trace/debug script, failed self-test output (FINDINGS §7) |
| `windows_offline_tools/` | Parsers for the offline Windows triage: `wintime.py` (clock-skew correction, with the ambiguous bands), `evtx2jsonl.py`, `evtx_triage.py`, `prefetch.py`, `srum_dump.py`, `mft_parse.py`, `usn_parse.py`, `reg_bam.py`, `amcache.py`, and `requirements.txt` to recreate their Python environment. They read `08_windows_offline/` |
| `other_devices_scratch/` | Working files from the other-device checks (below). The final scripts and logs are in `06_other_devices/` |

**Inside `other_devices_scratch/`**

- `scripts/tmux_run.sh.txt`: runs a command in the live USB's tmux pane so you can watch
- `ssh_known_hosts/`: host keys for the live USB and home-server
- `arch_iso_signature/`: the `.sig`, official `sha256sums.txt` and the keyring used
- `efi_binaries_from_desktop/`: the desktop's Microsoft boot programs and firmware `db`/`KEK`, checked in `06_other_devices/desktop_linux_nvme/08_efi_signatures.txt`
- `ventoy_1.1.05_reference/`: the official release tarball, its hash list, the official `core.img`, and file-by-file hash lists for the stick and the release
- `yumi_stick/stick_core_sectors1-2047.bin`: the stick's BIOS boot code, including the corrupted sector 34
- the failed OpenSSL Authenticode attempt

**Not kept** (easy to recreate):

- The Ventoy files unpacked from the release tarball: unpack it again to compare.
- The `dissect` Python environment: see `windows_offline_tools/requirements.txt`.
- The GoStringUngarbler clone and its venv: `git clone https://github.com/mandiant/gostringungarbler` (commit `1db869e`), then `python3 -m venv --system-site-packages` and `pip install lief`.

</details>

<details>
<summary><b><code>08_windows_offline/</code>: artifacts copied off the infected drive</b> (private)</summary>

Collected 2026-11-21 from the live Arch USB with the drive mounted read-only; nothing on it was changed. First-pass triage is done (FINDINGS §10). `README.txt` has the collection details. `README.md` is a stub that marks the folder as withheld from any public copy.

| Path | What it is |
|---|---|
| `col/raw/` | Event logs (397), Prefetch, SRUM, Amcache, the SOFTWARE and SYSTEM hives, scheduled tasks, the user's NTUSER.DAT / UsrClass.dat, PowerShell history, Recent, Startup, Defender support logs. **SAM and SECURITY were deliberately not collected** |
| `col/MFT`, `col/UsnJrnl_J.xz` | The NTFS file table and change journal. Decompress the journal with `xz -dk` before parsing |
| `col/SHA256SUMS` | Hashes taken on the live USB at collection time |
| `parsed/` | Event logs as JSONL, per-log date ranges, boots and clock changes, IOC hits, event-log triage, Prefetch runs, SRUM tables (`srum/`), the parsed MFT (`mft.tsv.gz`), the change journal with paths and corrected times (`usn.tsv.gz`), BAM, Amcache, the Defender log extract |

Windows ran its clock 6 h fast after every boot that followed Linux, until its first time sync. `parsed/boots_timechanges.txt` lists the boots and syncs, and `wintime.py` corrects for them.

No malware binaries were collected, but never run anything from here.

</details>

---

## Working with this repo

### Verifying integrity

From this folder:

```sh
sha256sum -c MANIFEST.sha256 | grep -v ': OK$'   # prints only failures
```

### Methodology

Everything was **static**: files were read, never run.

1. The RAT was rebuilt from `charmap.DMP` into a PE file, kept outside the evidence folders.
2. REA read its Go build information, which had been wiped.
3. A custom parser recovered the function table, whose magic had been tampered with.
4. Ghidra 12.2 decompiled the selected functions headless, without full analysis.

The panel source and stylesheet were carved byte-for-byte from memory. Secret scans print masked values only.

