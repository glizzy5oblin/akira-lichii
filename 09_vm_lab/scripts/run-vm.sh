#!/bin/bash
# Boot the copy-on-write overlay of the infected Windows install. Runs as your user.
#   run-vm.sh offline   no network reachable by the guest (QEMU user-net with restrict=on); pcap still written
#   run-vm.sh online    guest on the isolated bridge made by net-up.sh (LAN blocked, egress limited); run net-up.sh first
#   run-vm.sh reset     throw away all guest changes (deletes the overlay and NVRAM; run prep.sh again afterwards)
set -euo pipefail
LAB=/home/user/vmlab
MODE=${1:-offline}
cd "$LAB"
if [ "$MODE" = reset ]; then rm -f overlay.qcow2 OVMF_VARS.fd; rm -rf tpm; echo "overlay removed. Run: sudo $LAB/prep.sh"; exit 0; fi
[ -f overlay.qcow2 ] || { echo "run prep.sh first"; exit 1; }
[ -r /dev/nvme0n1 ] || { echo "no read access to /dev/nvme0n1 (ACL gone after reboot?). Run prep.sh again"; exit 1; }
if mount | grep -q '^/dev/nvme0n1'; then echo "refusing: a partition of nvme0n1 is mounted on the host"; exit 1; fi
RUN=run-$(date +%Y%m%d-%H%M%S); mkdir -p "$RUN"

mkdir -p tpm
swtpm socket --tpmstate dir=tpm --ctrl type=unixio,path=tpm/sock --tpm2 --daemon --pid file=tpm/pid
[ -f tpm/.init ] || { swtpm_setup --tpmstate tpm --tpm2 --createek --create-ek-cert --create-platform-cert --lock-nvram >/dev/null 2>&1 || true; touch tpm/.init; }
WD=
trap 'kill $(cat tpm/pid 2>/dev/null) $WD 2>/dev/null || true' EXIT

if [ "$MODE" = online ]; then
  NET=(-netdev tap,id=n0,ifname=labtap0,script=no,downscript=no)
else
  NET=(-netdev user,id=n0,restrict=on)
fi

echo "run dir: $LAB/$RUN   (pcap: $RUN/guest.pcap, monitor: $LAB/mon.sock)"
"$LAB/watchdog.sh" "$LAB/overlay.qcow2" 30 40 & WD=$!
echo "disk watchdog on: pauses guest at 30 GB overlay or <50 GB host free, quits at 40 GB or <30 GB (log: $LAB/watchdog.log)"
qemu-system-x86_64 \
  -machine q35,accel=kvm,x-oem-id=ALASKA,x-oem-table-id="A M I" -cpu host,kvm=off,-hypervisor -smp 4 -m 8G \
  -smbios type=0,vendor="American Megatrends International,, LLC.",version="1802" \
  -smbios type=1,manufacturer="ASUSTeK COMPUTER INC.",product="System Product Name",serial="System Serial Number" \
  -smbios type=2,manufacturer="ASUSTeK COMPUTER INC.",product="ROG STRIX X670E-F GAMING WIFI" \
  -rtc base=localtime \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
  -drive if=pflash,format=raw,file=OVMF_VARS.fd \
  -chardev socket,id=chrtpm,path=tpm/sock -tpmdev emulator,id=tpm0,chardev=chrtpm -device tpm-tis,tpmdev=tpm0 \
  -drive if=none,id=esp,format=raw,file=esp.img -device nvme,drive=esp,serial=ESP00001,model="Samsung SSD 980 PRO 1TB",bootindex=0 \
  -drive if=none,id=sys,format=qcow2,file=overlay.qcow2,werror=stop,rerror=stop -device nvme,drive=sys,serial=S6WWNJ0T123456,model="Samsung SSD 980 PRO 1TB",bootindex=1 \
  -drive if=none,id=labtools,format=raw,file=collect.img,readonly=on \
  "${NET[@]}" -device e1000e,netdev=n0,mac=<MAC> \
  -object filter-dump,id=f0,netdev=n0,file="$RUN/guest.pcap" \
  -device qemu-xhci -device usb-tablet -device usb-kbd -device usb-storage,drive=labtools,removable=on -vga std -display gtk \
  -monitor unix:"$LAB/mon.sock",server,nowait \
  -name malware-lab
