# How Wiener's Attack Works

A walkthrough of the math behind `wiener_attack.py`, from the setup to the
recovered primes.

## Setup

An RSA key picks two primes `p` and `q`, sets `n = p·q`, and chooses a
public exponent `e` and private exponent `d` so that:

```
e · d ≡ 1 (mod φ(n))        where  φ(n) = (p-1)(q-1)
```

Normally `e` is small (65537) and `d` is large. This key did the opposite:
it chose a **small `d`**, which forces a **large `e`** to satisfy the
equation above. That large `e` is the warning sign. In this key, `e` is
2045 bits against a 2048-bit `n`.

## Wiener's bound

Wiener (1990) proved that if

```
d < (1/3) · n^(1/4)
```

then `d` can be recovered from the public key alone. For a 2048-bit `n`,
`n^(1/4)` is about 512 bits, so any `d` under roughly 510 bits is exposed.
The `d` in this key is **64 bits**, not even close to safe.

## The key idea: a very good approximation

Start from the defining relation and write it with an explicit multiple `k`:

```
e · d − k · φ(n) = 1
```

Divide through by `d · φ(n)`:

```
e / φ(n) − k / d = 1 / (d · φ(n))
```

Because `φ(n) = n − (p + q) + 1` and `p + q` is tiny next to `n`, we have
`φ(n) ≈ n`. So `e / n` is an extremely close approximation of the fraction
`k / d`:

```
| e / n − k / d |  is very small
```

## Continued fractions find it

A theorem of continued fractions says that any fraction `k/d` approximating
`e/n` this closely **must appear as one of the convergents** of the
continued fraction expansion of `e/n`. There are only a few hundred
convergents (689 for this key), so we can simply test each one.

For each convergent `(k, d)`:

1. Skip it if `k = 0` or if `(e·d − 1)` is not divisible by `k`.
2. Compute the candidate totient: `φ = (e·d − 1) / k`.
3. If this `φ` is correct, then `p` and `q` are the two roots of:

   ```
   x² − (n − φ + 1)·x + n = 0
   ```

   Let `s = n − φ + 1`. The discriminant is `s² − 4n`. If it's a perfect
   square `r²`, the roots are:

   ```
   p = (s + r) / 2        q = (s − r) / 2
   ```

4. Confirm by checking `p · q == n`. If it holds, the key is broken.

For this key, the winning convergent is **number 45**. Once `p` and `q`
are known, every remaining private value (`d`, the CRT exponents, the
coefficient) follows directly.

## Why it matters

The attack does no factoring in the hard sense. No trial division, no
sieving. It's a short, deterministic continued-fraction computation that
finishes instantly. The 2048-bit modulus never mattered; the small `d`
handed everything over. The fix is equally simple: never choose `d`
directly. Pick a standard `e` (65537) and let `d` come out large.

## Reference

M. Wiener, "Cryptanalysis of short RSA secret exponents," *IEEE
Transactions on Information Theory*, 1990.
