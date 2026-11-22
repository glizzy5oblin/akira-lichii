# akira-lichii: a fake emulator that gave a stranger remote control of a PC

In November 2026 a Windows desktop was infected by a trojanized download of the "Lichii" game emulator. It carried a Go remote-access trojan ("Akira Remote") that ran for about two weeks. This repo holds the evidence, the analysis, the response documents and a sandbox test of the infected install.

| | |
|---|---|
| **Infected** | 2026-11-07, after downloading `lichii-win64.zip` from the fake site `lichii.org` |
| **Contained** | 2026-11-21: autostart removed, both malware processes suspended and saved |
| **Exposure** | About 14 days of possible remote control: screen, webcam, microphone, keystrokes, files, saved browser data |
| **Analysis** | Static only. The malware was never run on the analysis computer. A copy of the infected install was booted in a fenced-in VM |
| **Status** | Contained. The lab saw no contact with the malware's servers in ≈9 online minutes, which is reassuring but not proof of a clean system. Credentials should be treated as exposed |

---

## New here? Start with these three

| # | Open | You get |
|---|---|---|
| 1 | [`00_start_here/WHAT_HAPPENED.md`](00_start_here/WHAT_HAPPENED.md) | The whole story in plain English |
| 2 | [`01_report/ACTION_CHECKLIST.md`](01_report/ACTION_CHECKLIST.md) | What to do now |
| 3 | [`09_vm_lab/README.md`](09_vm_lab/README.md) | What the sandbox test showed, and what it does not prove |

Stuck on a word? [`GLOSSARY.md`](00_start_here/GLOSSARY.md). Lost in the folders? [`FOLDER_MAP.md`](00_start_here/FOLDER_MAP.md). Wondering what is unsettled? [`OPEN_QUESTIONS.md`](00_start_here/OPEN_QUESTIONS.md).

## I want to…

| Goal | Open |
|---|---|
| Understand what the malware is and can do | [`01_report/FINDINGS_2026-11-21.md`](01_report/FINDINGS_2026-11-21.md) |
| See how the infection happened: timeline, hashes | [`01_report/INCIDENT_REPORT.md`](01_report/INCIDENT_REPORT.md) |
| Get indicators to block or search for | [`01_report/IOCs.txt`](01_report/IOCs.txt) |
| Check whether other devices were touched | [`01_report/OTHER_DEVICES_2026-11-21.md`](01_report/OTHER_DEVICES_2026-11-21.md) |
| Read the attacker's control-panel source | [`04_analysis/panel_source/`](04_analysis/panel_source/) |
| See the panel rendered with fake data | [`04_analysis/panel_render/`](04_analysis/panel_render/) |
| Read the decompiled malware code | [`04_analysis/ghidra/INDEX.tsv`](04_analysis/ghidra/INDEX.tsv) |
| See what the downloaded `boing` payload is | [`04_analysis/stage2_boing_e87b/`](04_analysis/stage2_boing_e87b/README.md) |
| Repeat or review the VM lab | [`09_vm_lab/SETUP.md`](09_vm_lab/SETUP.md) |

---

## Safety

> **Read this before opening anything.**

- `05_archives/malware-samples_PASSWORD-infected.7z` holds real samples. **Extract it only in an isolated VM, never on a machine you care about.**
- Wine is installed. Its binfmt handler was disabled on 2026-11-21, so double-clicking a `.exe` no longer launches it, but `wine file.exe` still would.
- Every carved or extracted item ends in `.txt` or `.DO_NOT_RUN.bin` (or `.py`/`.java` for scripts). Nothing has the execute bit.
- `07_work_in_progress/rebuilt_images_DO_NOT_RUN/` is the RAT's real code rebuilt from memory and is detectable as malware. Never rename it to `.exe`, run it through `wine`, or upload it.
- Files from the VM lab (`09_vm_lab/evidence_PRIVATE/`) are guest output: read them as text, never run anything from them.

---

## The 60-second story

1. A search for "Lichii" led to `lichii.org`, a fake "official site". Its zip was a **trojanized emulator** with two added DLLs and a modified `lichii.exe`.
2. Running it planted a fake Python install and an autostart entry named **"Microsoft Display Driver Manager"**.
3. At every login the loader started `calc.exe` and `charmap.exe`, replaced their code in memory (process hollowing) and disguised their paths.
   - **`charmap.exe`** became the **RAT**: stealer, keylogger and a web control panel.
   - **`calc.exe`** became a stock **cloudflared** tunnel that put that panel on the internet **with no password**.
4. The RAT finds its servers through six domains and a **blockchain smart contract** (a "dead drop").
5. At login it copied the browsers' password, cookie, autofill and history databases for milliseconds, then deleted the copies.
6. Defender never raised a detection. The malware was found on 11/21.

## Key facts

| | |
|---|---|
| **Delivery** | `https://lichii.org/downloads/lichii-win64.zip` (the real project is `github.com/Frizti/Fritchii`) |
| **Persistence** | HKCU Run `Microsoft Display Driver Manager` → fake `Python399` → `pythonw.exe exec.py` |
| **RAT** | "Akira Remote", Go + garble, inside a hollowed `charmap.exe` |
| **Tunnel** | cloudflared inside a hollowed `calc.exe` → a `trycloudflare.com` address |
| **C2 domains** | `dpdc737.dpdatacenter.com`, `dongphucasian.com`, `waterseas.xyz`, `atomicplanets.cc`, `cosmicsky.cc`, `seaofstar.st` |
| **Dead drop** | BNB Smart Chain contract `0xF97CB22B8dBd52790493e962d4684B3FDB08A2Be` (`get()`) |
| **Exfiltration** | Telegram and the C2 domains |
| **Also steals** | Windows Credential Manager; bypasses Chrome App-Bound Encryption with a downloaded "ABE dumper" |
| **Defender** | No detection; no exclusions or settings changed |
| **Other devices** | Linux NVMe, laptop, USB stick: clean. Server: no malware, but a copied SSH key (since removed) and a password typed on the infected Windows were exposed |
| **VM lab** | Offline and online boots of a copy of the infected install: nothing malicious contacted; limits in [`RESULTS.md`](09_vm_lab/RESULTS.md#what-this-does-not-prove) |

What is still unknown is in [`OPEN_QUESTIONS.md`](00_start_here/OPEN_QUESTIONS.md).

---

## Folders at a glance

| Folder | What is in it |
|---|---|
| [`00_start_here/`](00_start_here/) | Plain-English guides: story, glossary, folder map, open questions |
| [`01_report/`](01_report/) | Documents for people: checklist, findings, incident report, IOCs |
| `02_host_evidence/` | Raw evidence from the infected desktop |
| `03_memory_dumps/` | Memory of the two malware processes |
| [`04_analysis/`](04_analysis/) | Everything derived from the evidence: decompiled code, panel, tools |
| `05_archives/` | Original bundles, including the live malware (encrypted) |
| `06_other_devices/` | Clean-checks of every other device |
| `07_work_in_progress/` | Raw working files, rebuilt images, old drafts |
| `08_windows_offline/` | Logs and registry copied off the infected drive |
| [`09_vm_lab/`](09_vm_lab/) | The sandbox boots of the infected install: results, setup, scripts |

Full per-file reference and sensitivity: [`FOLDER_MAP.md`](00_start_here/FOLDER_MAP.md).

---

## Working with this repo

**Verify integrity** (from this folder):

```sh
sha256sum -c MANIFEST.sha256 | grep -v ': OK$'   # prints only failures
```

**Method.** Everything was static: files were read, never run. The RAT was rebuilt from `charmap.DMP`, its wiped Go build information was read, a custom parser recovered the tampered function table, and Ghidra decompiled selected functions headless. Secret scans print masked values only.

