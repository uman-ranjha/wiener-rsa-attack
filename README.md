# Wiener's Attack on a Weak RSA Key

Recovering an RSA private key from its public key alone, when the private
exponent `d` was chosen too small. Done as a cryptography exercise for
FCM 741 against a deliberately weakened key on a class server.

The target key has a **64-bit private exponent on a 2048-bit modulus**,
far below the security bound, so the full private key can be reconstructed
from the public `(e, n)` in well under a second using only continued
fractions.

## What's here

| File | Purpose |
|------|---------|
| `wiener_attack.py` | The attack. Pure Python standard library, no dependencies. |
| `wiener_small_d_2048_ranjhauman.pub` | The vulnerable RSA public key it targets. |
| `METHOD.md` | The math: why a small `d` leaks, and how continued fractions recover it. |

## Running it

```bash
python3 wiener_attack.py
```

It reads the `.pub` file next to it, parses `e` and `n` out of the SSH
wire format, runs the attack, and prints a summary:

```
key type: ssh-rsa
e bits: 2045
n bits: 2048
n hex start: 0x903720341bdb61d7db...
convergents: 689
SUCCESS convergent: 45
k: 0x151bf5d591...
d bits: 64
d hex start: 0xa511...
p bits: 1024 q bits: 1024
p hex start: 0xccf3d6c36f...
q hex start: 0xb42291e866...
e*d % phi = 1
p*q == n: True
Done. Full values are not printed and not saved.
```

**Note:** `e` is 2045 bits, almost as large as `n`. That inversion (a
huge public exponent) is the visible fingerprint of a tiny `d`, since
`e · d ≡ 1 (mod φ(n))` forces one to grow as the other shrinks.

## Redaction

This script recovers a *private* key, so it is written to leak nothing.
It prints only bit-lengths and short truncated hex prefixes, and it never
writes the full `d`, `p`, or `q` to disk. The verification checks
(`p·q == n`, `e·d ≡ 1 mod φ`) prove the recovery succeeded without exposing
the secret values.

The full FCM 741 report is not in this repo. It shows the recovered `d` in
full, so it stays out. Same for the private key file, the params file from
the original run, and the class authorized_keys file.

## AI collaboration

This was an AI-assisted cryptanalysis exercise (the assignment encouraged
using AI). I used an LLM to implement Wiener's attack and reconstruct the
key, then verified the result independently four ways so I was never
trusting the model's output on faith:

1. **Public key round-trip.** Rebuilt the SSH public key from the
   recovered private key and confirmed it matched the published `.pub`
   file.
2. **Factorization.** Confirmed `p · q == n` with both primes at 1024 bits.
3. **Key relation.** Confirmed `e · d ≡ 1 (mod φ(n))`.
4. **Live login.** Logged in as mrweakkeys on the class server with the
   recovered key on Nov 19, 2026, and `whoami` printed mrweakkeys.

What the model got wrong: the first script had a dead loop in the
convergents function, cleaned up here, and it could not test the live login
from its own workspace, so I verified that myself.

The takeaway: an LLM gets you to a candidate answer fast, but in crypto a
candidate is worthless until it's checked against the math. The
verification is the real work.

## The lesson

RSA is only as strong as its parameters. A 2048-bit modulus is unbreakable
in practice, but this key chose a small `d` (presumably for faster
decryption), and that single choice throws the entire key away. See
`METHOD.md` for why.

---
Uman Ranjha · [github.com/uman-ranjha](https://github.com/uman-ranjha) · FCM 741
