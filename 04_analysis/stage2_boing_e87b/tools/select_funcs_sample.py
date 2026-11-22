# Static: map malware-specific strings -> referencing Go functions via rip-relative LEA, plus unnamed direct callees.
import struct,re,bisect,sys,collections
img=open(sys.argv[1],'rb').read(); funcs_txt=sys.argv[2]; out=sys.argv[3]
BASE=0x140000000; TEXT=(0x1000,0x1000+0xa39f11); RDATA=(0xa3b000,0xa3b000+0x6536f0); DATA=(0x108f000,0x108f000+0x13f910)
ents=[];names={}
for l in open(funcs_txt):
    p=l.rstrip('\n').split(' ',1); a=int(p[0],16)-BASE; ents.append(a); names[a]=p[1] if len(p)>1 else ''
ents=sorted(set(ents))
def func_of(rva):
    i=bisect.bisect_right(ents,rva)-1
    return ents[i] if i>=0 else None
# scan LEA r64,[rip+disp32]: (48|4C) 8D modrm(mod=00,rm=101)
refs=collections.defaultdict(list)
t=img[TEXT[0]:TEXT[1]]
for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]',t):
    o=m.start(); disp=struct.unpack_from('<i',t,o+3)[0]; nxt=TEXT[0]+o+7; tgt=nxt+disp
    if RDATA[0]<=tgt<DATA[1]: refs[tgt].append(TEXT[0]+o)
reft=sorted(refs)
SEEDS=open(sys.argv[4]).read().split('\n')
why=collections.defaultdict(set)
for s in SEEDS:
    if not s: continue
    b=s.encode(); pos=RDATA[0]
    while True:
        f=img.find(b,pos,DATA[1])
        if f<0: break
        i=bisect.bisect_right(reft,f)-1
        if i>=0 and f-reft[i]<=64:
            tag=s if reft[i]==f else s+' (approx)'
            for site in refs[reft[i]]:
                fn=func_of(site)
                if fn is not None: why[fn].add(tag)
        pos=f+1
# callees: E8 rel32 inside selected funcs
sel=dict(why)
for fn in list(why):
    i=ents.index(fn); end=ents[i+1] if i+1<len(ents) else TEXT[1]
    code=img[fn:end]
    for m in re.finditer(rb'\xe8',code):
        o=m.start()
        if o+5>len(code): break
        tgt=fn+o+5+struct.unpack_from('<i',code,o+1)[0]
        if tgt in names and (names[tgt]=='' ) and tgt not in sel:
            sel.setdefault(tgt,set()).add('callee of 0x%x'%(BASE+fn))
with open(out,'w') as w:
    for fn in sorted(sel, key=lambda a:(-len([x for x in sel[a] if not x.startswith('callee')]),a)):
        w.write('0x%x\t%s\t%s\n'%(BASE+fn,names.get(fn,'') or '-', '; '.join(sorted(sel[fn]))[:400]))
print('direct',len(why),'with callees',len(sel))
