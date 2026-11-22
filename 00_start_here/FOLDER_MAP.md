# Folder map

The full tour of what is where. If you are new, read [`../README.md`](../README.md) and [`WHAT_HAPPENED.md`](WHAT_HAPPENED.md) first; come here when you need to find something.

## Which folder do I need?

| I want… | Go to |
|---|---|
| To know what to do now | [`01_report/ACTION_CHECKLIST.md`](../01_report/ACTION_CHECKLIST.md) |
| To understand what the malware does | [`01_report/FINDINGS_2026-11-21.md`](../01_report/FINDINGS_2026-11-21.md) |
| The raw proof from the infected PC | `02_host_evidence/` |
| To see whether the machine is still active | [`09_vm_lab/`](../09_vm_lab/README.md) |
| Indicators to block or search for | [`01_report/IOCs.txt`](../01_report/IOCs.txt) |
| To check other devices | `06_other_devices/` |
| The decompiled code and tools | `04_analysis/` |

---

## Folder tree

```
akira-lichii/
├── README.md                 short entry page
├── MANIFEST.sha256           SHA-256 of every file
├── 00_start_here/            plain-English guides: what happened, glossary, folder map, open questions
├── 01_report/                documents for people: checklist, findings, report, IOCs
├── 02_host_evidence/         raw evidence from the infected desktop (unchanged)
│   └── system/  persistence/  network/  logs/  browser/  files/
├── 03_memory_dumps/          charmap.DMP (RAT), calc.DMP (cloudflared)
├── 04_analysis/              everything derived from the evidence
│   └── host_triage/  panel_source/  panel_render/  go_metadata/  ghidra/  tools/
│       related_sample_joesandbox/  stage2_boing_e87b/
├── 05_archives/              original bundles from the desktop
├── 06_other_devices/         desktop_linux_nvme/  home-server/  analysis-laptop/  yumi_usb/
├── 07_work_in_progress/      raw working files for resuming the analysis
├── 08_windows_offline/       artifacts copied off the infected drive
└── 09_vm_lab/                lab boots of a copy of the infected install: results, setup, scripts
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
| `09_vm_lab/` | What happened when a copy of the infected install was booted in a sandboxed VM, offline and online | Results and scripts are shareable; `evidence_PRIVATE/` is **private** |

---

## Folder reference

Each section opens to show its files.

<details>
<summary><b>Top-level files</b></summary>

| File | What it is |
|---|---|
| `README.md` | The short entry page |
| `MANIFEST.sha256` | SHA-256 of every file (verify with `sha256sum -c MANIFEST.sha256`, see [the README](../README.md#working-with-this-repo)) |
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

<details>
<summary><b><code>09_vm_lab/</code>: lab boots of a copy of the infected install</b></summary>

Read `09_vm_lab/README.md` first. The VM used an overlay on the real drive; the real drive was never written.

| Path | What it is |
|---|---|
| `README.md` | Plain-language summary of both boots |
| `RESULTS.md` | Findings per boot, the emulator test, unexplained items, what the lab does not prove, open items |
| `SETUP.md` | Design, how the network and host stayed safe, what a VM cannot hide, the disk-full incident |
| `results/dns_names_online_run.txt` | Every name the guest looked up online (names and counts only), checked against the known indicators |
| `scripts/` | Host scripts (prep, network, run, watchdog, extract) and the guest batch files (`collector/`) |
| `evidence_PRIVATE/` | Raw guest output and packet captures. Private; not published |

</details>

<details>
<summary><b><code>00_start_here/</code>: plain-English guides</b></summary>

| File | What it is |
|---|---|
| `WHAT_HAPPENED.md` | The incident explained without jargon, with a diagram |
| `GLOSSARY.md` | Every technical term used in this repo, in plain words |
| `FOLDER_MAP.md` | This file |
| `OPEN_QUESTIONS.md` | What is still unknown, by area, with what would answer it |

</details>
