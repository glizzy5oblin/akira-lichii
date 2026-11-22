#!/bin/bash
# Read files out of the stopped guest (overlay + real disk, combined view) READ-ONLY.
#   sudo extract.sh mount     -> Windows volume at /mnt/labwin (read-only)
#   sudo extract.sh umount    -> detach
# Copy what you need into /home/user/vmlab/loot/ with plain cp. Treat everything as malware: never execute or open it
# in Office/PDF/browser apps on this host. Never run this while the VM is running.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 1; }
OV=/home/user/vmlab/overlay.qcow2; MP=/mnt/labwin; NBD=/dev/nbd0
case "${1:-}" in
mount)
  pgrep -f 'qemu-system-x86_64.*malware-lab' >/dev/null && { echo "refusing: the VM is still running"; exit 1; }
  mountpoint -q /mnt/windows && { echo "refusing: /mnt/windows is mounted"; exit 1; }
  modprobe nbd max_part=8
  qemu-nbd -r -c $NBD "$OV"     # -r = read-only: nothing can be written to overlay or disk
  sleep 1; partprobe $NBD 2>/dev/null || true; sleep 1
  mkdir -p $MP /home/user/vmlab/loot; chown user /home/user/vmlab/loot
  mount -t ntfs3 -o ro,noexec,nosuid,nodev ${NBD}p2 $MP
  echo "mounted read-only at $MP. Example:  cp -r $MP/lab_out /home/user/vmlab/loot/"
  ;;
umount)
  umount $MP 2>/dev/null || true
  qemu-nbd -d $NBD 2>/dev/null || true
  echo detached ;;
*) echo "usage: sudo $0 mount|umount"; exit 1 ;;
esac
