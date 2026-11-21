# Parse Go 1.20+ pclntab (magic 0xfffffff1) from a file-layout PE: list function names and source files.
import struct,sys,collections
d=open(sys.argv[1],'rb').read(); out=sys.argv[2]
for magic in (b"\xde\xda|\xb0\x00\x00\x01\x08",):
    i=d.find(magic)
    while i!=-1:
        nfunc,nfiles=struct.unpack_from('<QQ',d,i+8)
        if 1000<nfunc<500000: break
        i=d.find(magic,i+1)
    if i!=-1: break
print('pclntab at',hex(i),'nfunc',nfunc,'nfiles',nfiles)
textStart,funcnameOff,cuOff,filetabOff,pctabOff,pclnOff=struct.unpack_from('<6Q',d,i+24)
ftab=i+pclnOff
names=[]; 
for k in range(nfunc):
    entry,foff=struct.unpack_from('<II',d,ftab+8*k)
    fo=ftab+foff
    nameOff=struct.unpack_from('<i',d,fo+4)[0]
    s=i+funcnameOff+nameOff; e=d.index(b'\0',s)
    names.append((textStart+entry,d[s:e].decode('utf-8','replace')))
# file table
ft=i+filetabOff; files=set(); p=ft
end=i+pctabOff
while p<end:
    e=d.index(b'\0',p); 
    if e>p: files.add(d[p:e].decode('utf-8','replace'))
    p=e+1
with open(out,'w') as f:
    for a,n in names: f.write(f'{a:#x} {n}\n')
open(out+'.files','w').write('\n'.join(sorted(files)))
pk=collections.Counter(n.split('.')[0] if '/' not in n.split('.')[0] else n.rsplit('/',1)[0]+'/'+n.rsplit('/',1)[1].split('.')[0] for a,n in names)
for k,v in pk.most_common(80): print(v,k)
print('files',len(files))
