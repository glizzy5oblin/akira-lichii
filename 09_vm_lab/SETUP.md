# Lab setup, safety design and limits

How the lab was built, why it was safe to run, and honestly what it cannot hide. The commands are in [`scripts/`](scripts/README.md).

## Contents

[Design](#design) · [How it stayed safe](#how-it-stayed-safe) · [What the VM cannot hide](#what-the-vm-cannot-hide) · [The disk-full incident](#the-disk-full-incident) · [How evidence got out](#how-evidence-got-out) · [Tool-run order](#tool-run-order)

---

## Design

| Piece | Choice | Why |
|---|---|---|
| Hypervisor | QEMU/KVM, modern PC chipset (q35), UEFI firmware, emulated TPM 2.0 | The real install is a UEFI/TPM Windows; it must boot unmodified |
| Guest disk | A **copy-on-write overlay** on top of the real drive, which the VM user can only read | The real disk is never written. Delete the overlay and the lab resets |
| Boot files | A small virtual EFI partition built from the Microsoft folder of the real EFI partition | The real EFI partition is shared with the Linux boot loader; a separate image with only Microsoft's files lets the guest boot Windows on its own |
| Network card | Emulated Intel e1000e, realistic MAC prefix | Windows has an in-box driver; looks like real hardware |
| Evidence tools | A read-only USB stick image with three batch files | Hot-plugging a USB disk is the simplest way to get tools into the guest without network |

## How it stayed safe

**Offline boot.** User-mode networking with outbound access switched off, plus a packet capture on the virtual cable. The guest could talk to nothing.

**Online boot.** A dedicated bridge network with strict firewall rules on the host:

- The guest could not reach the host (except for its address and DNS service), the home network, the VPN, or any private address range.
- Only web ports were allowed out: TCP 80/443/7844 and UDP 443/7844. That is enough for the malware's known channels (HTTPS, the blockchain RPC, GitHub, a Cloudflare tunnel) but rules out mail, scanning, SSH and most abuse.
- The two miner-pool domains were answered with a dead address by the lab's DNS.
- All DNS went through the lab's own forwarder, which logged every query.
- The host's Docker firewall policy (which drops forwarded traffic by default) needed an explicit allow for the lab traffic; removing the lab removes those rules.

**Host protection.** A watchdog ([`scripts/watchdog.sh`](scripts/watchdog.sh)) watches the overlay size and the host's free space. At 30 GB of overlay (or under 50 GB free) it **pauses** the guest; at 40 GB (or under 30 GB free) it quits it. The overlay drive also stops the guest on a write error, instead of retrying forever.

**Analysis rules.** The sample was never run on the analysis computer. Output from the guest was treated as hostile data: read with text tools and `python3 -I`, never executed.

## What the VM cannot hide

A careful program can often tell it is inside a virtual machine. What this lab does and does not hide:

**Hidden**
- The "I am a hypervisor" CPU flag and the KVM signature.
- Firmware identity: motherboard and BIOS strings imitate a real consumer board.
- Disk model (shown as a common retail NVMe drive) and ACPI table owner (a real BIOS vendor's).
- The network card vendor.
- The malware's *known* checks, found in the analysis: a pipe named `\\.\pipe\sandbox`, VirtualBox/VMware/Xen/Hyper-V driver and service names, and debugger process names. None of these exist in a QEMU guest, so none can trigger.

**Not hidden**
- USB device names still say "QEMU".
- The virtual graphics adapter is a generic display device, and there is no real GPU.
- Open-source firmware strings, the emulated chipset's device IDs.
- Timing: virtualization overhead on privileged instructions can be measured.

**Consequence.** If the sample misbehaved here, that would be real evidence. If it stayed silent, that proves much less: it may simply have declined to run. This is why [RESULTS.md](RESULTS.md) treats a quiet run as weak evidence.

## The disk-full incident

During the first offline boot the host ran out of disk and restarted.

| | |
|---|---|
| Symptom | The overlay grew to about 60–65 GB; the host reported no space at ≈21:34 and restarted at 21:38:59 |
| Likely cause | **Hypothesis only:** Windows background maintenance (defrag, disk cleanup, servicing, Defender scan) started ≈21:27 and rewrote large parts of the disk. We did not capture proof |
| Data affected | The overlay only. The real drive was unchanged and the overlay was discarded afterwards |
| Fixes | The watchdog (above); the drive stops on write errors; a guest-side prep script ([`lab_prep.bat`](scripts/collector/lab_prep.bat)) disables maintenance, updates, servicing and search before anything else |
| Follow-up needed | After a host restart the read-only permission on the real drive is reset; the prep script re-applies it |

## How evidence got out

The guest wrote its output to a folder on its own drive. After shutdown, the overlay was attached read-only on the host (network block device, NTFS read-only mount), the folder copied into `evidence_PRIVATE/`, then unmounted. This works only with the VM stopped. A hard window-close leaves Windows with an unclean shutdown; the read-only mount still worked.

## Tool-run order

For repeating the run (details in `scripts/`):

1. Host: reset overlay → prep (permissions, TPM state, overlay, boot image) → network up → capture → start VM.
2. Guest (administrator command prompt): `lab_prep.bat` (stops maintenance) → `lab_close.bat` (snapshots the process list *then* closes user apps; it deliberately does **not** close Python, so a loader would be recorded, not killed) → idle ~10 minutes → `collect.bat watch` → run the emulator → `collect.bat watch` again.
3. Host: shut the guest down → mount read-only → copy out → unmount → network down.
