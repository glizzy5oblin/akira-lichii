# emu_func.py: emulate selected functions from entry (Unicorn only; never executes natively), faking all calls,
# and collect printable runs from stack+heap at every call and at the end. Static analysis aid.
# usage: emu_func.py image.bin addr [addr...]
import sys, re, struct
from unicorn import *
from unicorn.x86_const import *

B = 0x140000000
STACK, STACK_SZ = 0x7f0000000000, 0x100000
HEAP, HEAP_SZ = 0x7e0000000000, 0x2000000
GST = 0x7d0000000000
MAX = 120000
d = open(sys.argv[1], 'rb').read()
FUNCS, SHARD, NSH, OUT = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
size = (len(d) + 0xfff) & ~0xfff
uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, size, UC_PROT_ALL); uc.mem_write(B, d)
uc.mem_map(STACK, STACK_SZ); uc.mem_map(HEAP, HEAP_SZ); uc.mem_map(GST, 0x10000)
st = {}
found = set()
RUN = re.compile(rb'[\x20-\x7e]{6,}')

def collect():
    sp = uc.reg_read(UC_X86_REG_RSP)
    for lo, hi in ((max(sp - 0x400, STACK), min(sp + 0x2000, STACK + STACK_SZ)), (HEAP, min(st['heap'], HEAP + HEAP_SZ))):
        if hi > lo:
            for m in RUN.finditer(bytes(uc.mem_read(lo, hi - lo))):
                found.add(m.group().decode())

def on_write(u, acc, addr, sz, val, _):
    if B <= addr < B + size:
        for k in range(sz):
            a = addr + k
            if a not in st['w']:
                st['w'][a] = bytes(u.mem_read(a, 1))
    return True

def on_unm(u, acc, addr, sz, val, _):
    if addr < 0x10000 or st['extra'] > 64:
        return False
    try:
        u.mem_map(addr & ~0xfff, 0x1000); st['extra'] += 1; return True
    except UcError:
        return False

def on_code(u, addr, sz, _):
    st['n'] += 1
    if st['n'] > MAX:
        u.emu_stop(); return
    b = u.mem_read(addr, 2)
    if b[0] == 0xE8 or (b[0] == 0xFF and (b[1] & 0xF8) == 0xD0) or (b[0] == 0x41 and b[1] == 0xFF):
        collect()
        p = st['heap']; st['heap'] += 0x200
        u.reg_write(UC_X86_REG_RAX, p)
        u.reg_write(UC_X86_REG_RIP, addr + (5 if b[0] == 0xE8 else sz))
    elif b[0] == 0xC3:
        u.emu_stop()

uc.hook_add(UC_HOOK_CODE, on_code)
uc.hook_add(UC_HOOK_MEM_WRITE, on_write)
uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, on_unm)


ents = sorted(int(l.split()[0], 16) for l in open(FUNCS))
todo = [a for a in ents if 0x140100000 <= a < 0x140b00000][SHARD::NSH]
out = open(OUT, 'w', encoding='utf-8')
for start in todo:
    st.update(n=0, heap=HEAP, w={}, extra=0)
    uc.mem_write(STACK + STACK_SZ // 4, b'\0' * (STACK_SZ // 2)); uc.mem_write(GST, b'\0' * 0x10000)
    uc.mem_write(HEAP, b'\0' * 0x40000)
    for r in (UC_X86_REG_RAX, UC_X86_REG_RBX, UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_RSI, UC_X86_REG_RDI,
              UC_X86_REG_R8, UC_X86_REG_R9, UC_X86_REG_R10, UC_X86_REG_R11, UC_X86_REG_R12, UC_X86_REG_R13, UC_X86_REG_R15):
        uc.reg_write(r, 0)
    sp = STACK + STACK_SZ // 2
    uc.reg_write(UC_X86_REG_RSP, sp); uc.reg_write(UC_X86_REG_RBP, sp + 0x800); uc.reg_write(UC_X86_REG_R14, GST)
    found.clear()
    try:
        uc.emu_start(start, 0, timeout=1500000, count=MAX + 10)
    except UcError:
        pass
    collect()
    for k, v in st['w'].items():
        uc.mem_write(k, v)
    for s in found:
        out.write('%#x\t%d\t%s\n' % (start, st['n'], s.replace('\t', ' ')))
    out.flush()
