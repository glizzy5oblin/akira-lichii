# Lab results

Dates are 2026-11-21, local time of the analysis computer. "Guest" means the virtual copy of the infected Windows install. Read [README.md](README.md) first for the plain-language summary.

## Contents

[Offline boot](#offline-boot) · [Online boot](#online-boot) · [The emulator test](#the-emulator-test) · [Things we could not explain](#things-we-could-not-explain) · [What this does not prove](#what-this-does-not-prove) · [Open items](#open-items)

---

## Offline boot

**Setup:** guest network restricted to nothing (outgoing traffic dropped), every packet captured.

| Check | Result |
|---|---|
| Loader process (`python.exe` from `Programs\Python…`), the hollowed `calc.exe`/`charmap.exe` pair | **Not running** |
| The fake Python folder (`%LOCALAPPDATA%\Programs\Python399`) | Empty (hash list identical in both boots) |
| Autostart: Run / RunOnce / Winlogon / Startup folders | Ordinary entries only. The malicious `Microsoft Display Driver Manager` Run value is **gone**, as expected: it was removed during containment on 11/21 |
| Windows Defender | No detection tied to this incident. One older detection (FileZilla, July) |
| Packet capture | **No payload.** No data packets, no completed handshakes, no DNS answers |
| One name worth noting | `dmu0adc7oht39.cloudfront.net` in the guest's DNS cache. Not tied to a program (see below) |

**Reading:** with its autostart removed, the infection did not re-establish itself on a plain boot.

## Online boot

**Setup:** the guest got a real (NATed) connection with tight limits: web ports only (TCP 80/443/7844, UDP 443/7844), nothing reachable on the home network, VPN or private ranges, and the two miner-pool names blocked in DNS. Everything was logged. About **9 minutes** online (22:02–22:11 for the guest's capture, DNS log to 22:13).

| Check | Result |
|---|---|
| DNS lookups | 222 lookups, 78 distinct names. **None** were the malware's C2 mirrors, blockchain RPC hosts, tunnel, Telegram, GoFile, IP-geolocation or miner-pool names. Full list: [`results/dns_names_online_run.txt`](results/dns_names_online_run.txt) |
| What the traffic was | Ordinary software calling home: Windows Update and certificate checks, GPU and peripheral software, game launchers and chat, a VPN client, package registries, an AI-agent app and its model providers |
| Connections with no DNS lookup first | 51 destinations (mostly repeated attempts on port 443 to VPS addresses). The pattern matches the VPN client's relay probing, but the encrypted handshake hides the names, so this is **likely, not confirmed** |
| Autostart, hosts file, loader folder hashes, victim-ID files | **Identical** to the offline boot. The two leftover files from the real infection (`t_id.txt`, `wd.pid`) were not refreshed, so no new session was started |
| Processes | The only Python was the AI-agent app's own bundled interpreter (under `AppData\Local\hermes\tools\`). The only `updater.exe` was Google's, finishing a scheduled wake-up |
| Services | Differences from the offline boot are our own lab settings (update and search services switched off) and normal start/stop churn |

## The emulator test

The goal was to run the Lichii emulator in the guest and watch for the loader reinstalling itself and calling out.

- `lichii.exe` appeared in **one** of the recorded rounds (PID 12552, about 1 second of CPU, no network sockets) and was gone in the next.
- After it started, the DNS log gained **one** new name: a Windows Update host.
- So the emulator produced **no visible network activity** during the observation.

**Why that is not conclusive.** The collector was cut off after 10 of its 18 rounds (about 3½ minutes) when the VM was closed, and the guest had been up only ~6 minutes when collection began. A program that exits after one second may have done its job, failed for ordinary reasons, or declined to run in a VM (see [SETUP.md](SETUP.md#what-the-vm-cannot-hide)). We did not compare this `lichii.exe` with the trojanized build we analyzed, which is the obvious next check.

## Things we could not explain

| Item | What we know | What would settle it |
|---|---|---|
| `dmu0adc7oht39.cloudfront.net` | Seen in both boots. Looked up alongside peripheral-software, game-launcher and AI-agent traffic. No process in the snapshots owns it | A public lookup of the name, or a longer online boot with per-process connection logging. **No lookup was made** |
| `u05srooyhc.execute-api.us-east-1.amazonaws.com` | Seen twice (22:03:53, 22:07:23), same company as above | Same as above |
| The 51 no-DNS destinations | Probably VPN relays (see above) | A capture with the TLS names visible, or the VPN's relay list |
| The boot manager on the shared EFI partition | `bootmgfw.efi` is version 10.0.28000.342, validly Microsoft-signed (Windows UEFI CA 2023), dated 2026-06-10. It matches **no file on the Windows partition**, whose own copies are version 10.0.19041.6456. It is a genuine, newer Microsoft file; where it came from is unexplained | Whether the owner used newer Windows media or a Secure Boot certificate update; a hash lookup against Microsoft's catalogs (needs permission to query outward) |

## What this does not prove

- **No attacker contact in ~9 minutes** is not "never contacted". The operator may only connect at certain times, or may have lost access when the Cloudflare tunnel stopped working (the memory dump shows "Tunnel not found" errors).
- **A quiet boot was expected.** The autostart was removed during containment. The boot test mainly confirms nothing *else* brings the malware back.
- **The 14 days of exposure are unaffected.** A clean lab boot does not undo possible credential theft before containment. Rotate credentials.
- **The VM is not invisible** to a careful program; see [SETUP.md](SETUP.md#what-the-vm-cannot-hide). Silence is weaker evidence than a positive sighting would be.
- **Short runs.** Both boots were brief and the emulator was observed for seconds.

## Open items

- [ ] Hash `lichii.exe` from the guest disk and compare it with the analyzed trojanized sample (read-only mount; no VM needed).
- [ ] Find where the newer `bootmgfw.efi` came from (owner's recollection; Microsoft hash lookup).
- [ ] Confirm with the owner that the AI-agent app (installed 2026-11-15, after the infection) was reinstalled by them, and what the autostart task "Start VMware VM" is.
- [ ] Services and `\Microsoft\` scheduled-task pass over the collected lists.
- [ ] Decode `t_id.txt`.
- [ ] Optional longer online boot with the emulator running 10+ minutes and per-process network logging.
- [ ] Optional live query of the blockchain contract (needs permission; the sample's current instructions could differ from the stored copy).
