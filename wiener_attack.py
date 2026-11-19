#!/usr/bin/env python3
"""Break a weak RSA key with Wiener's attack.

The public key in this repo has a 64-bit private exponent, far too small
for a 2048-bit modulus. Wiener's attack recovers it from the continued
fraction expansion of e/n.

Usage: python3 wiener_attack.py
It reads wiener_small_d_2048_ranjhauman.pub from the same folder.
It needs only the Python standard library.

Only truncated values are printed. The full recovered values are never
printed and never written to disk by this script.
"""

import base64
import math
import struct
import sys
from pathlib import Path


def trunc_hex(value, chars=12):
    h = hex(value)
    return h[:chars] + "..." if len(h) > chars else h


def read_mpint(data, off):
    ln = struct.unpack(">I", data[off:off + 4])[0]
    off += 4
    val = int.from_bytes(data[off:off + ln], "big")
    return val, off + ln


def read_string(data, off):
    ln = struct.unpack(">I", data[off:off + 4])[0]
    off += 4
    return data[off:off + ln], off + ln


def parse_public_key(path):
    parts = path.read_text().strip().split()
    if len(parts) < 2 or parts[0] != "ssh-rsa":
        print("Expected an ssh-rsa public key file.")
        sys.exit(1)
    blob = base64.b64decode(parts[1])
    off = 0
    typ, off = read_string(blob, off)
    e, off = read_mpint(blob, off)
    n, off = read_mpint(blob, off)
    return typ.decode(), e, n


def cont_frac(num, den):
    cf = []
    while den:
        q = num // den
        cf.append(q)
        num, den = den, num - q * den
    return cf


def convergents(cf):
    convs = []
    n0, n1 = 0, 1
    d0, d1 = 1, 0
    for a in cf:
        n0, n1 = n1, a * n1 + n0
        d0, d1 = d1, a * d1 + d0
        convs.append((n1, d1))
    return convs


def is_square(x):
    r = math.isqrt(x)
    return r * r == x, r


def main():
    key_path = Path(__file__).with_name("wiener_small_d_2048_ranjhauman.pub")
    if not key_path.exists():
        print("Public key file not found next to this script.")
        sys.exit(1)
    typ, e, n = parse_public_key(key_path)
    print("key type:", typ)
    print("e bits:", e.bit_length())
    print("n bits:", n.bit_length())
    print("n hex start:", trunc_hex(n, 20))

    cf = cont_frac(e, n)
    convs = convergents(cf)
    print("convergents:", len(convs))

    found = None
    for idx, (k, d) in enumerate(convs):
        if k == 0:
            continue
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        s = n - phi + 1
        disc = s * s - 4 * n
        if disc < 0:
            continue
        ok, r = is_square(disc)
        if not ok:
            continue
        if (s + r) % 2 != 0:
            continue
        p = (s + r) // 2
        q = (s - r) // 2
        if p * q == n:
            found = (idx, k, d, p, q, phi)
            break

    if not found:
        print("Wiener failed on convergents")
        sys.exit(1)

    idx, k, d, p, q, phi = found
    print("SUCCESS convergent:", idx)
    print("k:", trunc_hex(k))
    print("d bits:", d.bit_length())
    print("d hex start:", trunc_hex(d, 6))
    print("p bits:", p.bit_length(), "q bits:", q.bit_length())
    print("p hex start:", trunc_hex(p))
    print("q hex start:", trunc_hex(q))
    print("e*d % phi =", (e * d) % phi)
    print("p*q == n:", p * q == n)
    print("Done. Full values are not printed and not saved.")


if __name__ == "__main__":
    main()
