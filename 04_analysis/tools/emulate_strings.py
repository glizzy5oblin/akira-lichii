# emulate_strings.py: recover garble-encrypted string literals from the rebuilt Akira RAT image.
#
# SAFETY: this never runs the program. Short code snippets (the inline decryption blocks) are executed
# inside the Unicorn CPU emulator, which has no operating system: no files, no network, no Windows API.
# Every direct call is skipped (faked) except the string conversion we want to observe.
#
# How it works:
#   Each decrypted literal ends in a call to runtime.slicebytetostring (0x140052680), directly or through a
#   tiny per-literal closure. For each such call site, emulate from the start of its block (just after the
#   previous real call), follow closure calls, fake every other call, and read (RBX=ptr, RCX=len) at the
#   moment slicebytetostring is called.
#
# Usage: python3 -I emulate_strings.py <rebuilt_image.bin> <charmap_functions_16738.txt> <out.tsv> [--test]
import sys, struct, collections
from unicorn import *
from unicorn.x86_const import *
from capstone import *

B = 0x140000000
SLICEBYTETOSTRING = 0x140052680
NEWOBJECT = 0x1400153a0
STACK, STACK_SZ = 0x7f0000000000, 0x100000
HEAP, HEAP_SZ = 0x7e0000000000, 0x4000000
GSTRUCT = 0x7d0000000000
MAX_INSNS = 40000

img_path, funcs_path, out_path = sys.argv[1:4]
TEST = '--test' in sys.argv
d = open(img_path, 'rb').read()
size = (len(d) + 0xfff) & ~0xfff

funcs = []
for l in open(funcs_path):
    p = l.split(None, 1)
    if p and p[0].startswith('0x'):
        funcs.append((int(p[0], 16), p[1].strip() if len(p) > 1 else ''))
funcs.sort()
fend = {a: (funcs[i + 1][0] if i + 1 < len(funcs) else a + 0x100) for i, (a, _) in enumerate(funcs)}
fname = dict(funcs)

md = Cs(CS_ARCH_X86, CS_MODE_64)
REGS = {'rax','rbx','rcx','rdx','rsi','rdi','r8','r9','r10','r11','r12','r13','r15'}

# ---- static pass: find call sites and the start candidates of their blocks ----
sites = []   # (site_addr, func_addr, [start candidates])
for fa, _ in funcs:
    fe = fend[fa]
    if fe - fa > 0x40000:
        continue
    ins = list(md.disasm(d[fa - B:fe - B], fa))
    jt = set()
    for x in ins:
        if x.mnemonic.startswith('j') and x.op_str.startswith('0x'):
            jt.add(int(x.op_str, 16))
    last_call_end = ins[0].address if ins else fa
    for i, x in enumerate(ins):
        if x.mnemonic != 'call':
            continue
        tgt = int(x.op_str, 16) if x.op_str.startswith('0x') else None
        is_site = tgt == SLICEBYTETOSTRING
        if not is_site and x.op_str in REGS:
            for y in ins[max(0, i - 5):i]:
                if y.mnemonic == 'mov' and 'rip + ' in y.op_str and y.op_str.startswith('rdx'):
                    is_site = True
        if is_site:
            cands = [last_call_end] + sorted(a for a in jt if last_call_end < a < x.address)
            for j in range(i - 1, -1, -1):
                y = ins[j]
                if y.address < last_call_end:
                    break
                if y.mnemonic.startswith('j') and y.mnemonic != 'jmp' and j + 1 < len(ins):
                    cands.append(ins[j + 1].address)
            seen = []
            for c in cands:
                if c not in seen:
                    seen.append(c)
            sites.append((x.address, fa, seen[:8]))
        if tgt != NEWOBJECT:
            last_call_end = x.address + x.size

if TEST:
    sites = [s for s in sites if s[0] == 0x1404a2286]
print(f'{len(sites)} call sites to examine', file=sys.stderr)

# ---- emulator ----
uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, size, UC_PROT_ALL)
uc.mem_write(B, d)
uc.mem_map(STACK, STACK_SZ)
uc.mem_map(HEAP, HEAP_SZ)
uc.mem_map(GSTRUCT, 0x10000)
mapped_extra = []

st = {}
def reset(site):
    st.update(site=site, reached=False, result=None, depth=0, n=0, heap=HEAP, img_writes={}, extra=0)

def alloc(n=0x400):
    p = st['heap']; st['heap'] += (n + 0xf) & ~0xf
    if st['heap'] >= HEAP + HEAP_SZ:
        raise UcError(UC_ERR_NOMEM)
    return p

def on_write(uc_, access, addr, sz, val, _):
    if B <= addr < B + size:
        for k in range(sz):
            a = addr + k
            if a not in st['img_writes']:
                st['img_writes'][a] = bytes(uc_.mem_read(a, 1))
    return True

def on_unmapped(uc_, access, addr, sz, val, _):
    if st['extra'] > 32 or addr < 0x10000:
        return False
    page = addr & ~0xfff
    try:
        uc_.mem_map(page, 0x1000); mapped_extra.append(page); st['extra'] += 1
        return True
    except UcError:
        return False

def on_code(uc_, addr, sz, _):
    st['n'] += 1
    if st['n'] > MAX_INSNS:
        uc_.emu_stop(); return
    if addr == st['site']:
        st['reached'] = True
    b = uc_.mem_read(addr, 2)
    if b[0] == 0xE8:                                       # direct call
        tgt = (addr + 5 + struct.unpack('<i', uc_.mem_read(addr + 1, 4))[0]) & 0xffffffffffffffff
        if tgt == SLICEBYTETOSTRING:
            if st['reached']:
                ptr = uc_.reg_read(UC_X86_REG_RBX); n = uc_.reg_read(UC_X86_REG_RCX)
                if 0 < n < 0x10000:
                    try:
                        st['result'] = bytes(uc_.mem_read(ptr, n))
                    except UcError:
                        pass
                uc_.emu_stop(); return
        # fake the call: return a fresh zeroed heap pointer
        uc_.reg_write(UC_X86_REG_RAX, alloc())
        uc_.reg_write(UC_X86_REG_RIP, addr + 5)
    elif b[0] == 0xC3:                                     # ret
        st['depth'] -= 1
        if st['depth'] < 0:
            uc_.emu_stop()
    elif (b[0] == 0xFF and (b[1] & 0xF8) == 0xD0) or (b[0] == 0x41 and b[1] == 0xFF):
        st['depth'] += 1                                  # call reg: follow into the closure

uc.hook_add(UC_HOOK_CODE, on_code)
uc.hook_add(UC_HOOK_MEM_WRITE, on_write)
uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, on_unmapped)

def run(site, start):
    reset(site)
    uc.mem_write(STACK, b'\0' * STACK_SZ)
    uc.mem_write(GSTRUCT, b'\0' * 0x10000)
    for r in (UC_X86_REG_RAX, UC_X86_REG_RBX, UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_RSI, UC_X86_REG_RDI,
              UC_X86_REG_R8, UC_X86_REG_R9, UC_X86_REG_R10, UC_X86_REG_R11, UC_X86_REG_R12, UC_X86_REG_R13, UC_X86_REG_R15):
        uc.reg_write(r, 0)
    sp = STACK + STACK_SZ // 2
    uc.reg_write(UC_X86_REG_RSP, sp); uc.reg_write(UC_X86_REG_RBP, sp + 0x800)
    uc.reg_write(UC_X86_REG_R14, GSTRUCT)                  # Go's g: stackguard0 = 0, so stack checks pass
    try:
        uc.emu_start(start, 0, count=MAX_INSNS + 10)
    except UcError:
        pass
    for a, v in st['img_writes'].items():                  # undo any writes to the image
        uc.mem_write(a, v)
    return st['result']

def printable(s):
    try:
        t = s.decode('utf-8')
    except UnicodeDecodeError:
        return False
    return sum(c.isprintable() or c in '\r\n\t' for c in t) >= 0.9 * len(t)

stats = collections.Counter()
with open(out_path, 'w', encoding='utf-8') as out:
    out.write('site\tfunction\tlen\tprintable\tstring\n')
    for k, (site, fa, cands) in enumerate(sites):
        res = None
        for c in cands:
            res = run(site, c)
            if res is not None:
                break
        if res is None:
            stats['failed'] += 1; continue
        p = printable(res)
        stats['printable' if p else 'binary'] += 1
        out.write(f'{site:#x}\t{fname.get(fa) or hex(fa)}\t{len(res)}\t{int(p)}\t{res!r}\n')
        if k % 250 == 0:
            print(f'{k}/{len(sites)} {dict(stats)}', file=sys.stderr, flush=True)
print('done', dict(stats), file=sys.stderr)
