# Offline reproduction of one garble-encrypted string literal from HMxzL1ajr.PgQmfsM1t_ (0x1404a1a80).
# Pure byte arithmetic copied from Ghidra pseudocode; reads two key bytes from the rebuilt image's .data. Executes nothing.
# Usage: python3 -I decode_literal_PgQmfsM1t.py <rebuilt_image.bin>   -> b'GrabPasswordsOnly: ABE dumper execution failed'
import sys,struct
d=open(sys.argv[1],'rb').read(); B=0x140000000
g=d[0x14119f378-B]; ptr=struct.unpack_from('<Q',d,0x14119f360-B)[0]; c5=d[ptr+0x71-B]
key=bytearray(0x32)
for i,v in {0:40,1:g+10,2:8,3:0x27,4:-0x69,5:79,6:78,7:-0x55,8:-0x3f,9:1,10:-0x20,11:-0x30,12:-0x2d,13:0x1b,14:-0x50,15:36,16:-0x37,17:35}.items(): key[i]=v&0xff
struct.pack_into('<Q',key,0x12,0x77e3c657df|(((-0x69-g)&0xff)<<40)|(0x4a3b<<48))
for o,v in [(0x1a,0x301b14ab8314bdfc),(0x22,0x528b6223ac9acea5),(0x2a,0x7481f349af7af3c6)]: struct.pack_into('<Q',key,o,v)
p=bytearray(0x32)
for o,v in [(0,0x1ec1b0e78969036f),(2,0x5d381ec1b0e78969),(10,0xf742901e6a463452),(0x12,0xb7b00e97280898ff),(0x1a,0x93808c8aa30f226c),(0x22,0xb3f182911b03421a),(0x2a,0xb32bce4413df5f2f)]: struct.pack_into('<Q',p,o,v)
p[0x1e]^=0x9a; p[1]=(p[1]+102)&0xff; p[0x11]=(p[0x11]+102)&0xff; p[9]=(p[9]-g)&0xff; p[0x1c]=(p[0x1c]+c5)&0xff
print(bytes((p[i]-key[i])&0xff for i in range(0x32))[:46])
