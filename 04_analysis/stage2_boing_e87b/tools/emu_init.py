# emu_init.py: emulate init-style functions, executing string-decryptor helper calls for real (Unicorn only).
# usage: emu_init.py image funcs_table addr [addr...]   env: MAX, DEPTH
import sys, re, struct, os, bisect
from unicorn import *
from unicorn.x86_const import *
B = 0x140000000
STACK, STACK_SZ = 0x7f0000000000, 0x200000
HEAP, HEAP_SZ = 0x7e0000000000, 0x4000000
GST = 0x7d0000000000
MAX = int(os.environ.get('MAX', '2000000')); DEPTH = int(os.environ.get('DEPTH', '4'))
RT_LIMIT = 0x140100000; STS = 0x140052680
d = open(sys.argv[1], 'rb').read(); size = (len(d) + 0xfff) & ~0xfff
funcs = sorted(int(l.split()[0], 16) for l in open(sys.argv[2]) if l.startswith('0x')); fs = set(funcs)
uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, size, UC_PROT_ALL); uc.mem_write(B, d)
uc.mem_map(STACK, STACK_SZ); uc.mem_map(HEAP, HEAP_SZ); uc.mem_map(GST, 0x10000)
st = {}; res = {}
RUN = re.compile(rb'[\x20-\x7e]{6,}')
def rd(a, n):
    try: return bytes(uc.mem_read(a, n))
    except UcError: return None
def rec(p, n, tag):
    if 3 <= n <= 600 and (HEAP <= p < HEAP + HEAP_SZ or STACK <= p < STACK + STACK_SZ):
        b = rd(p, n)
        if b:
            for m in RUN.finditer(b): res.setdefault(m.group().decode(), tag)
def on_write(u, acc, addr, sz, val, _):
    if os.environ.get('WR') and st['sh'] and HEAP <= addr < HEAP + HEAP_SZ: print('heapwrite %x sz=%d val=%x depth=%d' % (addr, sz, val & ((1<<(8*sz))-1), len(st['sh'])), file=sys.stderr)
    if B <= addr < B + size:
        for k in range(sz):
            if addr + k not in st['w']: st['w'][addr + k] = bytes(u.mem_read(addr + k, 1))
    return True
def on_unm(u, acc, addr, sz, val, _):
    if addr < 0x10000 or st['extra'] > 64: return False
    try: u.mem_map(addr & ~0xfff, 0x1000); st['extra'] += 1; return True
    except UcError: return False
def on_code(u, addr, sz, _):
    st['n'] += 1
    if st['n'] > MAX: u.emu_stop(); return
    b = bytes(u.mem_read(addr, 2))
    if b[0] == 0xE8:
        tgt = (addr + 5 + struct.unpack('<i', bytes(u.mem_read(addr + 1, 4)))[0]) & 0xffffffffffffffff
        if tgt == STS:
            u.reg_write(UC_X86_REG_RAX, u.reg_read(UC_X86_REG_RBX)); u.reg_write(UC_X86_REG_RBX, u.reg_read(UC_X86_REG_RCX))
            rec(u.reg_read(UC_X86_REG_RAX), u.reg_read(UC_X86_REG_RBX), hex(st['cur']))
            u.reg_write(UC_X86_REG_RIP, addr + 5); return
        if (0x14006f420 <= tgt < 0x14006f940) and len(st['sh']) < DEPTH + 4:
            st['sh'].append((addr + 5, tgt)); return           # duffzero/duffcopy: run for real
        if tgt in fs and tgt >= RT_LIMIT and len(st['sh']) < DEPTH:
            st['sh'].append((addr + 5, tgt))
            if os.environ.get('DBG'): print('real call %x args rax=%x rbx=%x rcx=%x rdi=%x' % (tgt, u.reg_read(UC_X86_REG_RAX), u.reg_read(UC_X86_REG_RBX), u.reg_read(UC_X86_REG_RCX), u.reg_read(UC_X86_REG_RDI)), file=sys.stderr)
            return          # execute for real
        p = st['heap']; st['heap'] += 0x200
        u.reg_write(UC_X86_REG_RAX, p); u.reg_write(UC_X86_REG_RIP, addr + 5)
    elif (b[0] == 0xFF and (b[1] & 0xF8) == 0xD0) or (b[0] == 0x41 and b[1] == 0xFF):
        rec(u.reg_read(UC_X86_REG_RAX), u.reg_read(UC_X86_REG_RBX), 'callreg')
        if os.environ.get('DBG'): print('callreg rax=%x rbx=%x %r' % (u.reg_read(UC_X86_REG_RAX), u.reg_read(UC_X86_REG_RBX), rd(u.reg_read(UC_X86_REG_RAX), min(u.reg_read(UC_X86_REG_RBX), 80))), file=sys.stderr)
        p = st['heap']; st['heap'] += 0x200
        u.reg_write(UC_X86_REG_RAX, p); u.reg_write(UC_X86_REG_RIP, addr + (2 if b[0] == 0xFF else 3))
    elif b[0] == 0xC3:
        if st['sh']:
            ret, tgt = st['sh'].pop()
            rec(u.reg_read(UC_X86_REG_RAX), u.reg_read(UC_X86_REG_RBX), 'helper_%x' % tgt)
            if os.environ.get('DBG'): print('ret helper %x rax=%x rbx=%x rcx=%x n=%d %r' % (tgt, u.reg_read(UC_X86_REG_RAX), u.reg_read(UC_X86_REG_RBX), u.reg_read(UC_X86_REG_RCX), st['n'], rd(u.reg_read(UC_X86_REG_RAX), min(u.reg_read(UC_X86_REG_RBX), 64))), file=sys.stderr)
        else: u.emu_stop()
uc.hook_add(UC_HOOK_CODE, on_code); uc.hook_add(UC_HOOK_MEM_WRITE, on_write)
uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, on_unm)
LIST = [int(x, 16) for x in (open(os.environ['LIST']).read().split() if os.environ.get('LIST') else sys.argv[3:])]
for start in LIST:
    a = start; st.update(n=0, heap=HEAP, w={}, extra=0, sh=[], cur=start)
    uc.mem_write(STACK, b'\0' * STACK_SZ); uc.mem_write(GST, b'\0' * 0x10000); uc.mem_write(HEAP, b'\0' * 0x100000)
    for r in (UC_X86_REG_RAX, UC_X86_REG_RBX, UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_RSI, UC_X86_REG_RDI, UC_X86_REG_R8, UC_X86_REG_R9, UC_X86_REG_R10, UC_X86_REG_R11, UC_X86_REG_R12, UC_X86_REG_R13, UC_X86_REG_R15):
        uc.reg_write(r, 0)
    sp = STACK + STACK_SZ // 2
    uc.reg_write(UC_X86_REG_RSP, sp); uc.reg_write(UC_X86_REG_RBP, sp + 0x800); uc.reg_write(UC_X86_REG_R14, GST)
    try: uc.emu_start(start, 0, timeout=20000000, count=MAX + 10)
    except UcError as e: print('#', hex(start), 'stopped:', e, 'after', st['n'], file=sys.stderr)
    # global string headers written into .data by this run
    for k in sorted(st['w']):
        pass
    for g in range(0x141179e80, 0x141179e80 + 0x400, 8):
        pass
    print('== run', hex(start), 'insns', st['n'], file=sys.stderr)
    # scan modified .data for (ptr,len) headers
    for off in range(0x108f000, 0x108f000 + 0x13f910, 8):
        a = B + off
        p = struct.unpack_from('<Q', bytes(uc.mem_read(a, 16)), 0)[0]; n = struct.unpack_from('<Q', bytes(uc.mem_read(a, 16)), 8)[0]
        if (HEAP <= p < HEAP + HEAP_SZ) and 3 <= n <= 400: rec(p, n, 'global_%x' % a)
    for k, v in st['w'].items(): uc.mem_write(k, v)
    for s_, t_ in sorted(res.items(), key=lambda kv: kv[1]): print(hex(start), t_, s_, flush=True)
    res.clear()
