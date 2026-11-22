# Glossary

Plain-language meanings of the terms used in this repo. Ordered by theme, not alphabet.

## The attack

| Term | Meaning |
|---|---|
| **Malware / trojan** | Harmful software. A *trojan* pretends to be something useful (here, an emulator). |
| **RAT (remote-access trojan)** | Malware that lets someone control a computer from afar. Here: "Akira Remote". |
| **Trojanized** | A real program with malware added. |
| **Loader** | The small first stage that starts the real malware. |
| **Persistence** | How malware comes back after a restart. Here: an autostart entry. |
| **Run key** | A Windows setting that starts a program at login. |
| **Process hollowing** | Starting a legitimate program, then replacing its insides with other code so it looks innocent in the task list. |
| **Go / garble** | Go is the programming language of the RAT; *garble* scrambles its names and text to make it hard to read. |
| **Stealer** | A part that collects saved passwords, cookies and similar data. |
| **Keylogger** | Records what is typed. |
| **Exfiltration** | Sending stolen data out. |
| **Miner** | Software that uses your computer to make cryptocurrency for someone else. |

## Reaching the attacker

| Term | Meaning |
|---|---|
| **C2 / command-and-control** | The servers that give the malware instructions. |
| **Domain** | A website name such as `example.com`. |
| **Cloudflare tunnel / cloudflared** | A legitimate tool that exposes a local service to the internet. Misused here to publish the control panel. |
| **Dead drop (blockchain)** | A public blockchain record the malware reads to learn where to connect. It can be changed anytime and cannot be taken down. |
| **Smart contract / BNB Smart Chain** | A program stored on a public blockchain; the "mailbox" above. |
| **Telegram** | A chat service the malware used to send stolen data out. |
| **DNS** | The internet's phone book: turns a website name into an address. A DNS log shows which names a computer asked about. |
| **Packet capture (pcap)** | A recording of network traffic. |

## Evidence and tools

| Term | Meaning |
|---|---|
| **IOC (indicator of compromise)** | A clue that identifies the malware: a file hash, a domain, a file name. See [`IOCs.txt`](../01_report/IOCs.txt). |
| **Hash (SHA-256)** | A fingerprint of a file. Same file, same hash. |
| **Memory dump (`.DMP`)** | A snapshot of a running program's memory, taken while the malware was alive. |
| **Static analysis** | Studying malware by reading it, never running it. |
| **Decompiler / Ghidra** | A tool that turns a program back into readable code. |
| **Emulator** | Here, two meanings: the game-console emulator ("Lichii") that carried the malware; and a Python tool that imitates the malware's decryption steps. Context tells which. |
| **Defender** | Windows' built-in antivirus. |
| **Event log / Prefetch / MFT / USN journal / SRUM / Amcache** | Windows records of what ran, when and what files changed. Used to rebuild the timeline offline. |
| **Registry** | Windows' settings database; where autostart entries live. |

## The lab

| Term | Meaning |
|---|---|
| **VM (virtual machine)** | A computer simulated inside another one. |
| **QEMU/KVM** | The software that ran the VM. |
| **Overlay (copy-on-write)** | A scratch layer on top of the real disk: changes go to the layer; the real disk is untouched. Delete the layer to reset. |
| **Offline / online boot** | The VM with no internet / with a fenced internet connection. |
| **Egress** | Traffic leaving the VM. |
| **Sinkhole** | Answering a name with a dead address so nothing can connect. |
| **Watchdog** | A script that pauses the VM if disk space runs low. |
| **Hardening (a VM)** | Making a VM look like real hardware so malware does not detect it. See [`SETUP.md`](../09_vm_lab/SETUP.md#what-the-vm-cannot-hide). |

## The repo

| Term | Meaning |
|---|---|
| **Private / public copy** | `private/` is the full record. `public/` is an automatically cleaned copy with personal data removed; rebuilt by `make public`. |
| **MANIFEST** | A list of every file with its hash, to detect changes. |
| **Withheld** | A folder whose content stays private; only a short README appears in the public copy. |
