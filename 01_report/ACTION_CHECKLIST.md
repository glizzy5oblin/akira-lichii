# Action checklist

Work top to bottom. Do steps 2–4 **from a clean device** (this laptop is fine), never from the infected desktop.

## 1. Isolate (now)
- [ ] Unplug the desktop's network cable or turn off its Wi‑Fi. DNS blocking does not stop cloudflared, which connects to Cloudflare by IP.
- [ ] In the Tailscale admin console, **remove the desktop from the tailnet** and check which node owns `<TAILSCALE-IP>`. (`desktop-linux` is the desktop's *Linux* install, which was checked and is clean; see `OTHER_DEVICES_2026-11-21.md`.)

## 2. Cut off sessions (most urgent: the RAT can reuse your cookies)
For each account: **sign out of all sessions / revoke devices**, then change the password, then confirm 2FA uses an app or key (not SMS).
- [ ] Email accounts (all of them), and any password manager
- [ ] Crypto: move funds to a **new wallet created on a clean device** (don't reuse the seed)
- [ ] Banking / PayPal / cards saved in the browser (the panel had a "Cards" view)
- [ ] GitHub: revoke the `gh` token and personal access tokens, remove the desktop's SSH keys, review recent activity
- [ ] Discord (the panel extracts tokens with email/phone/2FA/billing), Steam, Epic
- [ ] Google / Microsoft accounts and their device lists
- [ ] API keys: <AI-VENDOR>, OpenAI/Codex, Gemini, Hermes `.env` bot tokens, any keys in env/config files
- [ ] Tailscale, Docker Hub, any self-hosted services
- [ ] **home-server:** change the `user` password (it was typed on infected Windows on 11/07 and 11/08), and the sudo password if it's the same. The desktop's SSH key was already removed on 11/21
- [ ] Wi‑Fi password (the panel recovers saved Wi‑Fi keys)
- [ ] Anything saved in **Windows Credential Manager** (network shares, RDP, websites): the RAT reads it through `vaultcli.dll`

## 3. Before wiping (optional, for answers)
- [ ] Copy off your own data files only (documents; push git repos). **No** programs, AppData or browser profiles.
- [ ] Run `DESKTOP_PREWIPE_CHECK.ps1.txt` (read-only; rename to `.ps1`) with the network unplugged. It lists staged payloads (`akdb*`, `abe*`, `C:\Users\Public\Downloads`). The cookie vault and keylog were most likely RAM-only, so expect no record of what was taken.
- [ ] Kill the suspended processes once you're done: `Stop-Process -Id 21136,21260 -Force`.

## 4. Wipe and rebuild
- [ ] Reinstall Windows from official media (format the system drive).
- [ ] Reinstall apps from official sources only. Get emulators from the real project (`github.com/Frizti/Fritchii`), not "official website" search results.
- [ ] Don't restore old browser profiles; sign in fresh.
- [ ] **Unplug the Samsung (Linux) NVMe while reinstalling Windows**, so Windows gets its own EFI partition instead of sharing the Linux drive's. **Don't wipe the Linux drive**: it was checked and is clean.
  - Afterwards, from CachyOS: remove the old `EFI/Microsoft/` folder from the Linux drive's EFI partition (`/boot`; back it up first), and delete the stale "Windows Boot Manager" firmware entry that points at it (`efibootmgr` shows two once the new one exists).
- [ ] On the new Windows, set `HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation\RealTimeIsUniversal` = DWORD `1`, so both OSes agree on the clock.
- [ ] Turn **Secure Boot** on in the firmware (it's off). For CachyOS with systemd-boot, sign its boot files first (e.g. `sbctl`).

## 4b. Other devices (see `OTHER_DEVICES_2026-11-21.md`)
- [ ] home-server: delete `~/.ssh/authorized_keys.bak-20261121-pre-VICTIM-PC-removal` (it still holds the stolen key) once you're sure you don't need it.
- [ ] home-server: consider `PasswordAuthentication no` in `/etc/ssh/sshd_config.d/`, and check `/root/.ssh/authorized_keys` and `fail2ban-client status sshd` (both need sudo).
- [ ] Router: confirm port 22 is **not** forwarded to home-server from the internet.
- [ ] On the Linux install, rotate any secret that was *also* used on Windows (same passwords, synced browser, shared keys).
- [ ] YUMI USB stick: replace it (one boot sector is corrupted and it throws I/O errors), or at least run `Ventoy2Disk.sh -u` from the official 1.1.05 release.

## 5. Report (optional)
- [ ] `lichii.org`: Google Safe Browsing report and the domain's registrar
- [ ] The trycloudflare hostname: Cloudflare abuse
- [ ] Hashes and IOCs: VirusTotal / MalwareBazaar (share only the lichii.org zips, never the dumps or browser files)
- [ ] GoFile abuse report, if GoFile turns up on the desktop (the related sample exfiltrated `DESKTOP-<host>_<user>.zip` there)
- [ ] When reporting, cite the related public sample: Joe Sandbox analyses 2004039 / 2004448 (`vscode-bootstrap.cmd`, same `exec.py` hash)
- [ ] BNB Smart Chain contract `0xF97CB22B8dBd52790493e962d4684B3FDB08A2Be`: BscScan report

## 6. This analysis folder
- [ ] Keep `02_host_evidence/browser/`, `03_memory_dumps/`, `06_other_devices/desktop_linux_nvme/`, `06_other_devices/home-server/` and the `.7z` archives private.
- [ ] Never extract `malware-samples_PASSWORD-infected.7z` on this laptop (Wine is installed; its auto-launch handler is disabled, but `wine` can still run a sample).
