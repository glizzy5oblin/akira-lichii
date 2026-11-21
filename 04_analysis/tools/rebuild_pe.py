# Rebuild a mapped PE image from a minidump into a file-layout PE (raw offset = RVA). Read-only on the dump.
import struct,sys
dmp,base,size,out=sys.argv[1],int(sys.argv[2],16),int(sys.argv[3],16),sys.argv[4]
f=open(dmp,'rb'); sig,ver,n,rva=struct.unpack('<4sIII',f.read(16))
f.seek(rva); dirs=[struct.unpack('<III',f.read(12)) for _ in range(n)]
img=bytearray(size); have=0
for t,sz,r in dirs:
    if t!=9: continue
    f.seek(r); cnt,boff=struct.unpack('<QQ',f.read(16))
    regs=[struct.unpack('<QQ',f.read(16)) for _ in range(cnt)]
    off=boff
    for start,rs in regs:
        lo=max(start,base); hi=min(start+rs,base+size)
        if lo<hi:
            f.seek(off+(lo-start)); img[lo-base:hi-base]=f.read(hi-lo); have+=hi-lo
        off+=rs
print('recovered bytes',have,'of',size)
e=struct.unpack_from('<I',img,0x3c)[0]
ns=struct.unpack_from('<H',img,e+6)[0]; so=e+24+struct.unpack_from('<H',img,e+20)[0]
for i in range(ns):
    p=so+40*i; vs,va=struct.unpack_from('<II',img,p+8)
    struct.pack_into('<II',img,p+16,vs,va)  # SizeOfRawData, PointerToRawData
    print(img[p:p+8].rstrip(b'\0'),hex(va),hex(vs))
open(out,'wb').write(img)
