import struct,sys
path,va,out=sys.argv[1],int(sys.argv[2],16),sys.argv[3]
f=open(path,'rb'); h=f.read(32)
sig,ver,nstreams,rva=struct.unpack('<4sIII',h[:16])
f.seek(rva); dirs=[struct.unpack('<III',f.read(12)) for _ in range(nstreams)]
for t,size,r in dirs:
    if t==9:
        f.seek(r); n,base=struct.unpack('<QQ',f.read(16))
        regs=[struct.unpack('<QQ',f.read(16)) for _ in range(n)]
        off=base; data=b''; cur=None
        for start,sz in regs:
            if start<=va<start+sz or (cur is not None and start==cur):
                f.seek(off); data+=f.read(sz); cur=start+sz
            elif cur is not None: break
            off+=sz
        open(out,'wb').write(data); print('carved',hex(va),len(data))
