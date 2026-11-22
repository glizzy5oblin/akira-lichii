# Decode the 941-byte on-chain config string returned by the dead-drop contract's get() (as carried in charmap.DMP).
# Every byte is shifted -4; the result is six base64 chunks (each ends in '='), each an XZ stream holding one mirror URL.
# usage: python3 -I decode_chain_config.py onchain_config_payload.bin
import sys, base64, lzma, re
s = bytes((c - 4) & 255 for c in open(sys.argv[1], 'rb').read())
for chunk in re.findall(rb'[A-Za-z0-9+/]+=*', s):
    print(lzma.decompress(base64.b64decode(chunk)).decode())
