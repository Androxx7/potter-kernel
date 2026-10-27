#!/usr/bin/env python3
"""Enxerta kernel novo em boot.img Android v0, preservando ramdisk.

python3 repack.py base.img Image.gz saida.img
"""
import struct, sys, hashlib

def ru(n, p): return (n + p - 1) // p * p

def main():
    base, kern_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
    d = bytearray(open(base, "rb").read())
    ksz, kaddr, rsz, raddr, ssz, saddr, tags, page = struct.unpack("<IIIIIIII", d[8:40])

    k_off = page
    r_off = page + ru(ksz, page)
    s_off = r_off + ru(rsz, page)
    second = bytes(d[s_off:s_off + ssz])
    tail = bytes(d[s_off + ru(ssz, page):])          # dtb extra / assinatura

    kern = bytearray(open(kern_p, "rb").read())
    if kern[:2] != b"\x1f\x8b":
        kern = bytearray(b"\x1f\x8b\x08") + kern

    new = bytearray(d[:page])                          # header+cmdline+id
    new += kern
    new += b"\x00" * ((-len(kern)) % page)
    new += d[r_off:s_off]
    new += b"\x00" * ((-ssz) % page)
    new += second
    new += b"\x00" * ((-ssz) % page)
    new += tail

    new[8:12] = struct.pack("<I", len(kern))

    # id sha1 estilo mkbootimg (legado; o bootloader do potter ignora)
    h = hashlib.sha1()
    h.update(bytes(kern)); h.update(struct.pack("<I", len(kern)))
    h.update(bytes(d[r_off:s_off])); h.update(struct.pack("<I", rsz))
    h.update(second); h.update(struct.pack("<I", ssz))
    new[576:576 + 20] = h.digest()

    open(out_p, "wb").write(new)
    print("base  ksz=%-9d rsz=%-8d page=%d" % (ksz, rsz, page))
    print("novo  ksz=%-9d (%+d)  tam=%d" % (len(kern), len(kern) - ksz, len(new)))
    print("md5   %s" % hashlib.md5(bytes(new)).hexdigest())

main()
