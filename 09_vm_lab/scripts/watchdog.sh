#!/bin/bash
# Disk guard for the lab VM. Started automatically by run-vm.sh.
#   - Soft limit: overlay bigger than SOFT GB, or host free space below MINFREE_SOFT GB  -> PAUSE the guest (monitor "stop")
#   - Hard limit: overlay bigger than HARD GB, or host free space below MINFREE_HARD GB  -> QUIT the guest
# A paused guest can be resumed with:  python3 -I /home/user/vmlab/vm-dump.py cmd cont
# usage: watchdog.sh <overlay.qcow2> [SOFT_GB] [HARD_GB]
OV=${1:?overlay path}; SOFT=${2:-30}; HARD=${3:-40}; MINFREE_SOFT=50; MINFREE_HARD=30
LAB=/home/user/vmlab; LOG=$LAB/watchdog.log
GB=1073741824
mon() { python3 -I "$LAB/vm-dump.py" cmd "$1" >/dev/null 2>&1; }
say() { echo "[watchdog $(date +%T)] $*" | tee -a "$LOG" >&2; command -v notify-send >/dev/null && notify-send -u critical "Lab VM watchdog" "$*" 2>/dev/null; }
for _ in $(seq 60); do pgrep -f 'qemu-system-x86_64.*malware-lab' >/dev/null && break; sleep 1; done
tripped=0
while pgrep -f 'qemu-system-x86_64.*malware-lab' >/dev/null; do
  used=$(( $(stat -c %b "$OV") * $(stat -c %B "$OV") / GB ))
  free=$(( $(df -B1 --output=avail "$OV" | tail -1) / GB ))
  if [ "$used" -ge "$HARD" ] || [ "$free" -le "$MINFREE_HARD" ]; then
    say "HARD limit (overlay ${used} GB, host free ${free} GB): quitting the guest"; mon quit; exit 0
  fi
  if [ "$tripped" = 0 ] && { [ "$used" -ge "$SOFT" ] || [ "$free" -le "$MINFREE_SOFT" ]; }; then
    mon stop; tripped=1
    say "SOFT limit (overlay ${used} GB, host free ${free} GB): guest PAUSED. Resume: python3 -I $LAB/vm-dump.py cmd cont"
  fi
  sleep 2
done
