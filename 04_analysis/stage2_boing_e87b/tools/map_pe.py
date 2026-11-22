import struct,sys
d=open(sys.argv[1],'rb').read(); out=sys.argv[2]
pe=struct.unpack_from('<I',d,0x3c)[0]; nsec=struct.unpack_from('<H',d,pe+6)[0]; opt=struct.unpack_from('<H',d,pe+20)[0]
soi=struct.unpack_from('<I',d,pe+24+56)[0]; shdr=struct.unpack_from('<I',d,pe+24+60)[0]
img=bytearray(soi); img[:shdr]=d[:shdr]
for i in range(nsec):
    o=pe+24+opt+40*i; n=d[o:o+8].rstrip(b'\0').decode(); vs,va,rs,ro=struct.unpack_from('<IIII',d,o+8)
    img[va:va+min(vs,rs)]=d[ro:ro+min(vs,rs)]
    print("%-8s rva=0x%x vsize=0x%x rawsize=0x%x"%(n,va,vs,rs))
open(out,'wb').write(img)
print("sizeofimage=0x%x"%soi)
