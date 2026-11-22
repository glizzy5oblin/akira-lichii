#!/bin/bash
# One-time prep for the malware VM lab. Run:  sudo /home/user/vmlab/prep.sh
# 1) compares the ESP's Windows boot manager with the copy inside the Windows partition (read-only mount)
# 2) builds a small GPT disk image holding a copy of /boot/EFI/Microsoft (the VM's own ESP)
# 3) gives the user READ-ONLY access to /dev/nvme0n1 (ACL, gone at reboot) so QEMU runs unprivileged
# 4) creates the qcow2 overlay whose backing file is the real disk. The real disk is never opened for writing.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 1; }
U=${SUDO_USER:-user}
LAB=/home/user/vmlab
DISK=/dev/nvme0n1
WINP=/dev/nvme0n1p2
mkdir -p "$LAB"; chown "$U" "$LAB"

echo "== 1. boot manager comparison (informational; servicing can legitimately differ)"
MNT=$(mktemp -d)
mount -t ntfs3 -o ro "$WINP" "$MNT"
sha256sum /boot/EFI/Microsoft/Boot/bootmgfw.efi /boot/EFI/Microsoft/Boot/bootmgr.efi 2>/dev/null || true
sha256sum "$MNT/Windows/Boot/EFI/bootmgfw.efi" "$MNT/Windows/Boot/EFI/bootmgr.efi" 2>/dev/null || true
ls -la --time-style=full-iso /boot/EFI/Microsoft/Boot/bootmgfw.efi /boot/EFI/Microsoft/Boot/BCD "$MNT/Windows/Boot/EFI/bootmgfw.efi" 2>/dev/null || true
umount "$MNT"; rmdir "$MNT"
mountpoint -q /mnt/windows && { echo "ERROR: /mnt/windows is mounted; unmount it before running the VM"; exit 1; } || true

echo "== 2. ESP image"
if [ ! -f "$LAB/esp.img" ]; then
  truncate -s 600M "$LAB/esp.img"
  printf 'label: gpt\n,,U\n' | sfdisk -q "$LAB/esp.img"
  LOOP=$(losetup -fP --show "$LAB/esp.img")
  trap 'losetup -d "$LOOP" 2>/dev/null || true' EXIT
  mkfs.vfat -F32 -n LABESP "${LOOP}p1" >/dev/null
  M=$(mktemp -d); mount "${LOOP}p1" "$M"
  mkdir -p "$M/EFI/BOOT"
  cp -a /boot/EFI/Microsoft "$M/EFI/"
  cp /boot/EFI/Microsoft/Boot/bootmgfw.efi "$M/EFI/BOOT/BOOTX64.EFI"
  umount "$M"; rmdir "$M"; losetup -d "$LOOP"; trap - EXIT
  chown "$U" "$LAB/esp.img"
fi

echo "== 3. read-only ACL on $DISK for $U"
setfacl -m "u:$U:r" "$DISK"
getfacl -p "$DISK" | grep "user:$U"

echo "== 4. overlay"
if [ ! -f "$LAB/overlay.qcow2" ]; then
  sudo -u "$U" qemu-img create -q -f qcow2 -b "$DISK" -F raw "$LAB/overlay.qcow2"
fi
sudo -u "$U" qemu-img info "$LAB/overlay.qcow2" | head -8
cp -n /usr/share/edk2/x64/OVMF_VARS.4m.fd "$LAB/OVMF_VARS.fd"; chown "$U" "$LAB/OVMF_VARS.fd"
echo "prep done. Next: $LAB/run-vm.sh offline"
