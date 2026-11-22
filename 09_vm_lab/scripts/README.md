# Lab scripts

These are **copies** of the scripts used on the analysis computer. They contain that computer's paths (`/home/user/vmlab/…`) and device names, so treat them as a reference to adapt, not a turnkey tool. None of them executes malware; the malware is whatever sits on the disk image being booted.

## Host side (Linux, need `sudo` where noted)

| File | What it does |
|---|---|
| `prep.sh` (sudo) | Hashes the boot managers, builds the virtual boot partition, makes the real drive read-only for the VM user, creates the overlay and the firmware variable store |
| `net-up.sh` (sudo) | `up` / `down`: builds the fenced network (bridge, firewall rules, DNS forwarder with logging). Also `dns` (restart only DNS) and `status` |
| `run-vm.sh` | Starts the VM: `offline`, `online` or `reset`. Also starts the disk watchdog and the packet capture |
| `watchdog.sh` | Pauses the guest at 30 GB of overlay (or < 50 GB host free) and quits it at 40 GB (or < 30 GB free) |
| `extract.sh` (sudo) | `mount` / `umount`: attaches the stopped guest's overlay read-only so output can be copied out |
| `vm-dump.py` | Talks to the VM's control socket: screenshots and monitor commands (e.g. hot-plug the tools USB disk) |

## Guest side (`collector/`, Windows batch)

| File | What it does |
|---|---|
| `lab_prep.bat` | Run first, as administrator. Turns off background maintenance, updates, servicing and search in the *throw-away* overlay only |
| `lab_close.bat` | Records the process list and connections, then closes user apps. Leaves Python alone on purpose |
| `collect.bat` | Collects volatile state, persistence entries, loader-folder listings and hashes, system and Defender status into `C:\lab_out`. `watch` adds process/connection snapshots every 20 s |

## Notes

- Private address ranges in `net-up.sh` are written as `${B172}.16.0.0/12` and `${B192}.168.0.0/16` so the publishing script does not rewrite them. At run time they expand to the usual ranges.
- Nothing here needs network access except `net-up.sh online`'s deliberately limited egress.
