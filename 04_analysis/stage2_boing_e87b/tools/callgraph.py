import sys, struct, bisect, collections
img=open(sys.argv[1],'rb').read(); B=0x140000000
funcs=sorted(int(l.split()[0],16) for l in open(sys.argv[2]) if l.startswith('0x'))
names={int(l.split()[0],16):(l.split()[1] if len(l.split())>1 else '') for l in open(sys.argv[2]) if l.startswith('0x')}
text=img[0x1000:0x1000+0xa39f11]
fs=set(funcs); callers=collections.defaultdict(set)
for i in range(len(text)-5):
    if text[i]==0xE8:
        rel=struct.unpack_from('<i',text,i+1)[0]; src=B+0x1000+i; tgt=src+5+rel
        if tgt in fs:
            k=bisect.bisect_right(funcs,src)-1
            if k>=0: callers[tgt].add(funcs[k])
import json
json.dump({hex(k):sorted(hex(x) for x in v) for k,v in callers.items()},open(sys.argv[3],'w'))
for t in sys.argv[4:]:
    t=int(t,16); print(hex(t),names.get(t,''),'<-',[ (hex(c),names.get(c,'')) for c in sorted(callers[t])])
