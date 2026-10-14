#!/usr/bin/env python3
"""A small QR Code encoder (ISO/IEC 18004), written for this site (ideas track 42, 14 Oct 2026) so the build needs no
package and no network. Byte mode, error correction level M, versions 1–10 (up to 213 bytes), all eight masks scored
with the standard penalty rules. Output: a module matrix, an SVG and a 1-bit PNG (zlib only).

Written from the public specification for farazisgiannis.com; no third-party code. "QR Code" is a registered trademark
of DENSO WAVE INCORPORATED. Usage: python3 tools/qr.py "https://farazisgiannis.com/card/" out.svg|out.png
"""
import struct, sys, zlib

# level M: (ec codewords per block, [(blocks, data codewords per block), ...]) for versions 1..10
_M = {1: (10, [(1, 16)]), 2: (16, [(1, 28)]), 3: (26, [(1, 44)]), 4: (18, [(2, 32)]), 5: (24, [(2, 43)]),
      6: (16, [(4, 27)]), 7: (18, [(4, 31)]), 8: (22, [(2, 38), (2, 39)]), 9: (22, [(3, 36), (2, 37)]),
      10: (26, [(4, 43), (1, 44)])}
_ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42],
          9: [6, 26, 46], 10: [6, 28, 50]}
_ECL_M = 0b00

# GF(256) with the QR polynomial x^8 + x^4 + x^3 + x^2 + 1
_EXP = [0] * 512; _LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x; _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100: _x ^= 0x11D
for _i in range(255, 512): _EXP[_i] = _EXP[_i - 255]

def _mul(a, b): return 0 if a == 0 or b == 0 else _EXP[_LOG[a] + _LOG[b]]

def _rs_generator(n):
    g = [1]
    for i in range(n):
        out = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            out[j] ^= c
            out[j + 1] ^= _mul(c, _EXP[i])
        g = out
    return g

def _rs_remainder(data, n):
    g = _rs_generator(n); rem = list(data) + [0] * n
    for i in range(len(data)):
        c = rem[i]
        if c:
            for j in range(1, len(g)): rem[i + j] ^= _mul(g[j], c)
    return rem[len(data):]

def _capacity(v): return sum(b * d for b, d in _M[v][1])

def _codewords(data: bytes):
    for v in range(1, 11):
        count_bits = 8 if v < 10 else 16
        if 4 + count_bits + 8 * len(data) <= 8 * _capacity(v): break
    else:
        raise ValueError('too long for versions 1–10')
    bits = [0, 1, 0, 0] + [(len(data) >> i) & 1 for i in range(count_bits - 1, -1, -1)]
    for byte in data: bits += [(byte >> i) & 1 for i in range(7, -1, -1)]
    cap = 8 * _capacity(v)
    bits += [0] * min(4, cap - len(bits))
    bits += [0] * (-len(bits) % 8)
    cw = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]; k = 0
    while len(cw) < _capacity(v): cw.append(pad[k % 2]); k += 1
    ec_n, groups = _M[v]
    blocks, pos = [], 0
    for nb, nd in groups:
        for _ in range(nb): blocks.append(cw[pos:pos + nd]); pos += nd
    ecs = [_rs_remainder(b, ec_n) for b in blocks]
    out = []
    for i in range(max(len(b) for b in blocks)):
        out += [b[i] for b in blocks if i < len(b)]
    for i in range(ec_n): out += [e[i] for e in ecs]
    return v, out

def _bch(value, poly, total_bits):
    """value followed by its BCH remainder (format and version information)"""
    deg = poly.bit_length() - 1
    rem = value << deg
    while rem.bit_length() > deg:
        rem ^= poly << (rem.bit_length() - 1 - deg)
    return (value << deg) | rem

_MASKS = [lambda r, c: (r + c) % 2 == 0, lambda r, c: r % 2 == 0, lambda r, c: c % 3 == 0, lambda r, c: (r + c) % 3 == 0,
          lambda r, c: (r // 2 + c // 3) % 2 == 0, lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
          lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0, lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0]

def _base(v):
    n = 17 + 4 * v
    m = [[0] * n for _ in range(n)]; fn = [[False] * n for _ in range(n)]
    def put(r, c, val):
        if 0 <= r < n and 0 <= c < n: m[r][c] = 1 if val else 0; fn[r][c] = True
    for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                inside = 0 <= dr <= 6 and 0 <= dc <= 6
                ring = inside and (dr in (0, 6) or dc in (0, 6) or (2 <= dr <= 4 and 2 <= dc <= 4))
                put(r0 + dr, c0 + dc, ring)
    for i in range(8, n - 8): put(6, i, i % 2 == 0); put(i, 6, i % 2 == 0)
    a = _ALIGN[v]
    for r in a:
        for c in a:
            if (r == 6 and c == 6) or (r == 6 and c == a[-1]) or (r == a[-1] and c == 6): continue
            for dr in range(-2, 3):
                for dc in range(-2, 3): put(r + dr, c + dc, max(abs(dr), abs(dc)) != 1)
    put(n - 8, 8, 1)  # dark module
    for i in range(9):  # reserve format areas
        for (r, c) in ((8, i), (i, 8)):
            if not fn[r][c]: fn[r][c] = True
    for i in range(8): fn[8][n - 1 - i] = True; fn[n - 1 - i][8] = True
    if v >= 7:
        info = _bch(v, 0x1F25, 18)
        for i in range(18):
            bit = (info >> i) & 1
            put(i // 3, n - 11 + i % 3, bit); put(n - 11 + i % 3, i // 3, bit)
    return m, fn

def _place(m, fn, cw):
    n = len(m); bits = [(b >> i) & 1 for b in cw for i in range(7, -1, -1)]; k = 0
    col = n - 1; up = True
    while col > 0:
        if col == 6: col -= 1
        for i in range(n):
            r = n - 1 - i if up else i
            for c in (col, col - 1):
                if not fn[r][c]:
                    m[r][c] = bits[k] if k < len(bits) else 0; k += 1
        up = not up; col -= 2

def _format(m, mask):
    n = len(m)
    info = _bch((_ECL_M << 3) | mask, 0x537, 15) ^ 0x5412
    bit = lambda i: (info >> i) & 1
    for i in range(6): m[i][8] = bit(i)
    m[7][8] = bit(6); m[8][8] = bit(7); m[8][7] = bit(8)
    for i in range(9, 15): m[8][14 - i] = bit(i)
    for i in range(8): m[8][n - 1 - i] = bit(i)
    for i in range(8, 15): m[n - 15 + i][8] = bit(i)
    m[n - 8][8] = 1

def _penalty(m):
    n = len(m); p = 0
    for grid in (m, [list(x) for x in zip(*m)]):
        for row in grid:
            run, prev = 0, None
            for x in row:
                if x == prev: run += 1
                else:
                    if run >= 5: p += run - 2
                    run, prev = 1, x
            if run >= 5: p += run - 2
            s = ''.join(map(str, row))
            p += 40 * (s.count('10111010000') + s.count('00001011101'))
    for r in range(n - 1):
        for c in range(n - 1):
            if m[r][c] == m[r][c + 1] == m[r + 1][c] == m[r + 1][c + 1]: p += 3
    dark = sum(map(sum, m)); p += 10 * (abs(dark * 20 - n * n * 10) // (n * n))
    return p

def encode(text: str):
    """the module matrix (list of rows of 0/1) for text, UTF-8 bytes, level M"""
    v, cw = _codewords(text.encode('utf-8'))
    best = None
    for mask in range(8):
        m, fn = _base(v)
        _place(m, fn, cw)
        f = _MASKS[mask]
        for r in range(len(m)):
            for c in range(len(m)):
                if not fn[r][c] and f(r, c): m[r][c] ^= 1
        _format(m, mask)
        score = _penalty(m)
        if best is None or score < best[0]: best = (score, m)
    return best[1]

def svg(m, quiet=4, title=''):
    n = len(m) + 2 * quiet
    path = ''.join(f'M{c + quiet} {r + quiet}h1v1h-1z' for r, row in enumerate(m) for c, x in enumerate(row) if x)
    t = f'<title>{title}</title>' if title else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" width="{n * 10}" height="{n * 10}" shape-rendering="crispEdges">'
            f'{t}<rect width="{n}" height="{n}" fill="#fff"/><path d="{path}" fill="#000"/></svg>\n')

def png(m, scale=12, quiet=4):
    n = (len(m) + 2 * quiet) * scale
    rows = []
    for y in range(n):
        r = y // scale - quiet
        bits = []
        for x in range(n):
            c = x // scale - quiet
            dark = 0 <= r < len(m) and 0 <= c < len(m) and m[r][c]
            bits.append(0 if dark else 1)
        bits += [1] * (-len(bits) % 8)
        rows.append(b'\x00' + bytes(int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)))
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 1, 0, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b''.join(rows), 9)) + chunk(b'IEND', b''))

if __name__ == '__main__':
    text, out = sys.argv[1], sys.argv[2]
    q = encode(text)
    if out.endswith('.png'): open(out, 'wb').write(png(q))
    else: open(out, 'w').write(svg(q))
    print(f'{out}: {len(q)}×{len(q)} modules')
