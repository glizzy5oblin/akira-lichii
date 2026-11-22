# Dump guest RAM (ELF, for Volatility3 / strings) or save/restore a snapshot through the QEMU monitor socket.
# usage: python3 -I vm-dump.py mem [outfile]   |   python3 -I vm-dump.py snap NAME   |   python3 -I vm-dump.py cmd "<monitor command>"
import socket, sys, time
S = '/home/user/vmlab/mon.sock'
def mon(c):
    s = socket.socket(socket.AF_UNIX); s.connect(S); s.settimeout(3)
    try: s.recv(4096)
    except Exception: pass
    s.sendall((c + '\n').encode()); time.sleep(1)
    out = b''
    try:
        while True:
            d = s.recv(65536)
            if not d: break
            out += d
    except Exception: pass
    return out.decode(errors='replace')
a = sys.argv[1:]
if a[:1] == ['mem']:
    f = a[1] if len(a) > 1 else '/home/user/vmlab/mem-%d.elf' % time.time()
    print(mon('dump-guest-memory ' + f), 'writing', f, '(8 GB; check df first, then ls -la)')
elif a[:1] == ['snap']:
    print(mon('savevm ' + a[1]))
elif a[:1] == ['cmd']:
    print(mon(a[1]))
else: print(__doc__)
