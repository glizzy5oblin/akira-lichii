# 09 · Virtual-machine lab (2026-11-21)

**In one sentence:** we booted a *copy* of the infected Windows install inside a sandboxed virtual machine, once with no internet and once with a tightly limited internet connection, to see whether the malware was still active and who it would talk to.

> **Short answer:** in about 9 online minutes the machine contacted nothing malicious. That is reassuring but **not proof of a clean system**. The boot-time persistence had already been removed during containment, so a quiet boot was expected, and the one real test (starting the emulator) was too short to settle anything. [Details and limits](RESULTS.md#what-this-does-not-prove).

## Why we did it

Static analysis (reading the malware's code) tells us what it *can* do. It cannot tell us whether the machine is *still* doing something, or whether anything is still calling out. A lab boot answers that safely: the real disk is never written, the network is fenced in, and everything the guest sends is recorded.

## What happened, in plain terms

| Boot | Network | What we looked at | Result |
|---|---|---|---|
| **Offline** (from ≈21:00 until the host ran out of disk ≈21:34) | None: all outgoing traffic blocked | Process list, autostart entries, loader folder, Defender, a full packet capture | Nothing running that shouldn't be. **No** payload left the guest: no data packets, no completed connections, no DNS answers |
| **Online** (22:02–22:13) | Limited: web ports only, no home network, miner-pool names blocked | Same, plus every DNS lookup and every connection | **No** contact with the malware's servers, the blockchain "dead drop", Telegram, tunnels or miner pools |

Between the two boots the host computer ran out of disk space and restarted (see [SETUP.md](SETUP.md#the-disk-full-incident)). A disk guard was added afterwards.

## Where to read next

| You want | Open |
|---|---|
| The findings, boot by boot, with caveats | [`RESULTS.md`](RESULTS.md) |
| How the lab was built, how it stayed safe, what it cannot hide | [`SETUP.md`](SETUP.md) |
| Every website the guest looked up (names only) | [`results/dns_names_online_run.txt`](results/dns_names_online_run.txt) |
| The scripts that built and ran the lab | [`scripts/`](scripts/README.md) |
| Raw guest output and packet captures | `evidence_PRIVATE/` (private, not published) |

## Safety notes

- **The real disk was never written.** The VM works on a copy-on-write overlay; the physical drive was made read-only to the VM user.
- **Never reuse the guest's files on a machine you care about.** They are malware evidence (process names, window titles, system details). Treat them as data: read them, don't run anything from them.
- **Credentials from the real machine should still be treated as exposed.** A quiet lab boot says nothing about the 14 days before containment; see [`01_report/ACTION_CHECKLIST.md`](../01_report/ACTION_CHECKLIST.md).
