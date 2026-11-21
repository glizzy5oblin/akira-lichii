# Other devices: were they touched? (2026-11-21)

This report covers everything checked besides the infected Windows install. All checks were **read-only**; nothing on the checked machines was changed except the one SSH key edit on home-server described below. Raw outputs are in [`06_other_devices/`](../06_other_devices/).

## Verdict

| Device | Verdict | Evidence |
|---|---|---|
| **Desktop's Linux NVMe** (NVMe SSD, CachyOS, Tailscale name `desktop-linux`) | ✅ **Clean**: no sign Windows or the malware touched it, offline (from the live USB) or live (booted, §1b) | `desktop_linux_nvme/` (withheld) |
| **home-server** (`<LAN-HOST-B>`) | ✅ No malware. ⚠️ **SSH access was exposed**: the infected PC's key was authorized, and its password was typed on infected Windows | `home-server/` (withheld) |
| **analysis-laptop** (the analysis laptop) | ✅ Clean. Only link: Chrome history synced from the desktop | [`analysis-laptop/checks.txt`](../06_other_devices/analysis-laptop/checks.txt) |
| **YUMI USB stick** (used to boot the live Arch session) | ✅ Boot path genuine. ⚠️ One **corrupted** (not tampered) sector in its legacy-BIOS boot code; the flash looks unreliable | [`yumi_usb/verification.txt`](../06_other_devices/yumi_usb/verification.txt) |

---

## 1. The desktop's Linux NVMe

The desktop dual-boots. Windows is on the WD SN850X (`nvme0n1`); CachyOS is on the NVMe SSD (`nvme1n1`: 2 GB EFI partition + 464 GB btrfs, **not encrypted**). The drive was checked from a verified Arch Linux live USB (UEFI boot), mounted read-only (`btrfs -o ro,norecovery`), with Windows not running.

### Could the malware have reached it?
The RAT has no Linux features (no ext4/btrfs, WSL or raw-disk code among its 16,738 recovered functions), and Windows can't read btrfs on its own. Reaching this drive would have needed the operator to act by hand with **admin rights**: `wsl --mount`, raw disk writes, or writes to the EFI partition. The malware ran unelevated, and no admin-only traces were left behind (see `FINDINGS_2026-11-21.md` §3).

### What was checked

| Check | Result |
|---|---|
| **Files changed while Linux wasn't running** (the key test) | **None.** 1,388,146 files changed on the drive after 11/07 18:00Z. After correcting the clocks (below), every one falls inside a Linux session. The last 13 (11/20 22:09–22:14Z) are the owner's own apps (a <AI-APP> Code skill sync and `optimaizr`) just before that session crashed. → `06_changes_while_linux_not_running.log.txt` (withheld), `07_crashed_session_1120.log.txt` (withheld) |
| systemd-boot on the EFI partition | Byte-identical to the packaged `systemd-bootx64.efi` (`08a90dd9…0035`) |
| Kernels on the EFI partition | Both identical to the packaged `vmlinuz` (7.3.4-1-cachyos, 6.18.60-2-cachyos-lts) |
| initramfs (both) | `/init`, `init_functions` and all hooks (keymap, plymouth, udev) identical to the packaged versions. Every program and module inside matches the installed copy; `busybox` matches `/usr/lib/initcpio/busybox`. Only the 5 module index files differ, which `mkinitcpio` regenerates (expected) |
| Microsoft programs on the shared EFI partition | `bootmgfw.efi` (build 10.0.28000.342), `bootmgr.efi`, `memtest.efi`, `SecureBootRecovery.efi`: **valid Microsoft signatures**. The signed hash matches each file, and each chains to a CA in the PC's own firmware Secure Boot db ("Windows UEFI CA 2023" / "Microsoft Windows Production PCA 2011"). → `08_efi_signatures.txt` (withheld) |
| Packaged files (`pacman -Qkk`) | No modified program files. Differences are normal drift: VLC plugin cache, CachyOS `lsb-release`, symlinks and ownership, config files |
| Files no package owns (system paths) | 7, all the owner's: `<AI-APP>` and `pnpm` (npm globals), `optimaizr`, `/usr/local/bin/code` (VS Code link), `remove-nvidia` (CachyOS installer script), `nvidia-vaapi.sh` |
| sshd, PAM, sudo | Stock. No extra PAM modules. `sudoers.d` holds only the installer's `%wheel` rule |
| `~/.ssh/authorized_keys` | Only `user@analysis-laptop` (ED25519 `R/5t5I…`) |
| Persistence (systemd, cron, autostart, profile.d, ld.so.preload, udev) | Only package-owned files or the owner's own (`hermes-gateway.service`, `librepods.desktop`); no `ld.so.preload` |
| Windows-made files (`Zone.Identifier`, stray `.exe`/`.ps1`) | None beyond normal package contents |

### The clock problem (and why it matters for the timeline)
Windows keeps the PC's hardware clock in local time; Linux reads it as UTC. So whichever OS boots second is **6 hours off until it syncs**:
- **Linux after Windows** records its boot 6 h early. Example: Windows shut down at 11/17 00:26:46Z; Linux logged its boot at "11/16 18:27:13", i.e. 00:27:13Z.
- **Windows after Linux** runs 6 h ahead, often for the whole session (Windows syncs rarely). This is why the desktop's own logs show "02:31" for the 20:31 logon.

The real Linux sessions (UTC) used for the test:
`11/07 21:48–21:55`, `11/08 17:53 – 11/10 06:07`, `11/16 01:52–03:13`, `11/17 00:27–14:31`, `11/19 07:06 – 11/20 03:27`, `11/20 14:04 – ≈22:15` (crashed), `11/20 23:31–23:47`, `11/21 00:31–02:31`.

### Limits
- **Reads leave no trace.** This shows nothing was *written* from outside Linux; it can't prove no file was *read*. Reading would still have needed admin rights plus a WSL mount, and nothing shows either.
- `03_bootmgr_wtmp_unowned.log.txt` is **cut short**: the live session's 256 MB RAM disk filled up while unpacking the initramfs. Its initramfs section was redone in `04_initramfs_compare.log.txt`. Ignore the "DIFFERS: …plymouth…png" lines in `03`, which are truncated files.
- `04_initramfs_compare.log.txt` lists ~300 "NOT ON SYSTEM" fonts and keyboard maps. That's an artefact: those paths are absolute symlinks, which resolved against the live USB instead of the NVMe.
- The first pass in `02_…log.txt` reported "1,215,672 changed outside a Linux boot window" because the journal only keeps boots from 11/17. That number is wrong; `06_…log.txt` is the corrected test.

### 1b. Live check after booting it (2026-11-21 04:20 CST)
Once the desktop was booted from its own drive, the running system was audited over SSH from analysis-laptop, in the owner's tmux session (sudo typed by the owner). It was read-only. Details: `live_2026-11-21/README.txt` (withheld).

- **Running state is clean.** Every one of the 426 processes is a normal app or system daemon. None runs from a temp folder or a deleted file, and none has `LD_PRELOAD`. A PID-by-PID probe found **no hidden processes**. The 80 running programs come from 49 packages, and `pacman -Qkk` finds no altered files in them. Only the NVIDIA modules taint the kernel.
- **Network is clean.** Every socket has a known owner. Outbound traffic goes only to Chrome, Discord, Steam and Tailscale's servers. There are no IOC addresses, no tunnel port 7844 and no trycloudflare.
- **Persistence, accounts and keys match the offline check.** No unowned systemd units, only the laptop's key in `authorized_keys`, and none of the desktop's SSH keys is the stolen Windows key.
- **Logins and sudo are all the owner's.** Since 11/18, SSH logins came only from analysis-laptop, plus one self-login during the 11/19 key setup. Today at 03:54–03:55, the binfmt masking and the unicorn/capstone install were also done here over SSH from the laptop. They aren't in the desktop's own changelog yet.
- **Boot files are unchanged** since the offline check: systemd-boot, bootmgfw.efi and the BCD timestamp all match.
- **To harden:** the firewall is off (`ufw` inactive, INPUT accept), and sshd listens on all interfaces with password logins allowed. If this Linux password was ever typed on the infected Windows, change it. Consider keys-only SSH and enabling `ufw`.

---

## 2. home-server

### What it trusted
- **The infected PC's key** `user@VICTIM-PC` (RSA 3072, `SHA256:<KEY-FINGERPRINT>`) was in `~/.ssh/authorized_keys`. The stealer took the desktop's `~/.ssh`, so treat the key as stolen. **Removed 2026-11-21 01:15 CST** (backup: `~/.ssh/authorized_keys.bak-20261121-pre-VICTIM-PC-removal`, which still contains it; delete when done). Logged in analysis-laptop's `~/SYSTEM_CHANGELOG.md`.
- **Password logins are enabled**, and the password was typed **on infected Windows** on 11/07 (16:24–17:49 CST) and 11/08 (03:05–04:09 CST). With a keylogger in the RAT, assume it is known.

### Who logged in
Both of the desktop's OSes share one network card, so they get the **same IPv4 address, `<DESKTOP-LAN-IP>`**. `fe80::a25d:c1c:9f43:bfbd` is the Windows-only link-local address. Each login was matched against the corrected Linux sessions → `login_attribution.txt` (withheld):
- **Infected Windows:** 11/07 16:24 → 11/08 04:09 CST (key and password), and **11/13 20:47–21:38 CST** (key, arriving via the router `<ROUTER-IP>`).
- **The desktop's Linux:** the password logins on 11/08 12:48 and 14:43–14:48, 11/09 23:26 and 11/20 19:13. Corroboration: Linux installed FileZilla at 12:47:43 on 11/08, and the logins started 52 s later.
- No logins from unknown addresses since 11/01; only 2 failed passwords (the owner's iPhone over Tailscale).

### The 11/13 session through the router
It used the stolen key while infected Windows was running, so it was checked → `session_2026-11-13_via_router.txt` (withheld). It looks like the owner's normal work: <AI-APP> Code on `hotschedules-automated` (repo prep, project memory notes), `gh` login data refreshed at 21:20. There was **no `sudo`** and **no changes under `/etc`, `/usr/local`, `/opt` or cron**. The same key also came in via `<ROUTER-IP>` on 11/04, before the infection, so this routing is a pre-existing habit. Still worth confirming the router doesn't forward port 22 from the internet.

### Checks with nothing found
- No IOC files anywhere on the disk.
- No IOC SHA-256 match.
- No matching processes.
- No connections to the tunnel or C2 addresses.
- Persistence is all the owner's (docker, caddy, paypulse, hotschedules, download-bot…).
- The `cloudflared` log in `~/vscode_projects/file-transfer` is from a different, named tunnel on another Windows PC (2026-08-23), copied over on 11/08.
- `sudo` history 11/07–11/21 is routine service management.
- Not checked (needs sudo): `/root/.ssh/authorized_keys` and fail2ban status.

---

## 3. analysis-laptop and the USB stick
- **Laptop:** see [`analysis-laptop/checks.txt`](../06_other_devices/analysis-laptop/checks.txt). Chrome Sync copied the desktop's 11/07 history here (marked SYNCED; there were no downloads here). That means the desktop's Chrome uses the same Google account, whose sessions should be treated as stolen. The laptop's SSH key was trusted *by* the desktop, but its private key never left the laptop.
- **YUMI stick:** see [`yumi_usb/verification.txt`](../06_other_devices/yumi_usb/verification.txt).
  - The Arch ISO matches the official 2025.10.01 checksum and has a good Arch signature.
  - The Ventoy EFI partition is byte-identical to official 1.1.05.
  - One sector of its legacy-BIOS GRUB core is corrupted. It's a broken compressed stream, which tampering wouldn't produce, and the stick also threw USB I/O errors. That code wasn't used: the desktop booted the stick via UEFI (`BootCurrent 0006`).

## 4. What follows from this
- **Don't wipe the Linux NVMe.** Do rotate any secret that was *also* used or typed on Windows (same passwords, synced browsers, shared SSH keys).
- **Give Windows its own EFI partition.** Today Windows boots from the Linux drive's EFI partition, so a future Windows compromise could reach the Linux boot files. Evidence (checked 2026-11-21):
  - The WD drive has **no EFI partition**: `nvme0n1p1` is Microsoft reserved (16 MB), `p2` is Windows (927 GB), `p3` is a 4 GB NTFS data partition with no boot files.
  - `bootmgfw.efi`, the `BCD` and 139 Microsoft files sit in `nvme1n1p1/EFI/Microsoft/`, next to systemd-boot.
  - Firmware entry Boot0000 "Windows Boot Manager" points at PARTUUID `cffbebf9…` (`nvme1n1p1`).
  - systemd-boot's automatic Windows menu entry only works because `bootmgfw.efi` is on its own EFI partition.
  - Windows last rewrote that `BCD` on 11/21 01:22 CST, which is normal at boot.

  Fix: unplug the Samsung drive while reinstalling Windows, then delete `EFI/Microsoft/` from `nvme1n1p1`. After that, use the firmware boot menu or a manual systemd-boot entry for Windows.
- **Turn Secure Boot on.** It's currently **disabled** (`SecureBoot=0`, not in setup mode). With systemd-boot, sign your own boot files (e.g. `sbctl`).
- **Fix the clock mismatch:** on the new Windows, set `HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation\RealTimeIsUniversal` = DWORD 1.
- **home-server:** change the password from a clean device, consider `PasswordAuthentication no`, delete the `authorized_keys` backup, check the router for a port-22 forward.
- **USB stick:** replace it, or at least rewrite its boot code with `Ventoy2Disk.sh -u` from the verified release.
