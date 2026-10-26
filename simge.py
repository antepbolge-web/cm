"""Cafer Hepsi simgesini (altın zemin, turkuaz hilal, beyaz yıldız) başka renklere boyar; ek kütüphane gerektirmez.
Kullanım: python -I simge.py <kaynak_res> <hedef_res> <tema>
Tema: vakit (turkuaz zemin, altın hilal), notlar (mor zemin, altın hilal), merkez (lacivert zemin, beyaz hilal, altın yıldız).
Gölge ve kenar yumuşaklığı korunur: her piksel kendi parlaklığı oranında yeni renge çevrilir."""
import sys, os, zlib, struct

def oku(yol):
    d = open(yol, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n'
    i, idat, w = 8, b'', None
    while i < len(d):
        n, t = struct.unpack('>I4s', d[i:i + 8]); c = d[i + 8:i + 8 + n]; i += 12 + n
        if t == b'IHDR':
            w, h, bit, ct, _, _, il = struct.unpack('>IIBBBBB', c)
            assert bit == 8 and ct in (2, 6) and il == 0, (yol, bit, ct, il)
        elif t == b'IDAT':
            idat += c
    bpp = 4 if ct == 6 else 3
    ham, sat, onc = zlib.decompress(idat), w * bpp, bytearray(w * bpp)
    px = []
    for y in range(h):
        f, s = ham[y * (sat + 1)], bytearray(ham[y * (sat + 1) + 1:(y + 1) * (sat + 1)])
        for x in range(sat):
            a = s[x - bpp] if x >= bpp else 0; b = onc[x]; c = onc[x - bpp] if x >= bpp else 0
            if f == 1: s[x] = (s[x] + a) & 255
            elif f == 2: s[x] = (s[x] + b) & 255
            elif f == 3: s[x] = (s[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                s[x] = (s[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        onc = s
        px.append([tuple(s[x:x + bpp]) + ((255,) if bpp == 3 else ()) for x in range(0, sat, bpp)])
    return w, h, px

def yaz(yol, w, h, px):
    ham = b''.join(b'\x00' + bytes(v for p in sat for v in p) for sat in px)
    ch = lambda t, c: struct.pack('>I', len(c)) + t + c + struct.pack('>I', zlib.crc32(t + c) & 0xffffffff)
    open(yol, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + ch(b'IDAT', zlib.compress(ham, 9)) + ch(b'IEND', b''))

TEMA = {   # zemin üst, zemin alt, hilal, yıldız (None = olduğu gibi beyaz)
    'vakit':  ((18, 140, 128), (7, 82, 75), (232, 182, 48), None),
    'notlar': ((126, 74, 168), (74, 38, 110), (232, 182, 48), None),
    'merkez': ((44, 98, 186), (18, 52, 112), (255, 255, 255), (240, 190, 50)),
}
ALTIN, TURKUAZ = (236, 186, 60), (12, 96, 98)   # kaynak simgedeki ortalama renkler
lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def boya(px, h, tema):
    ust, alt, hilal, yildiz = TEMA[tema]
    out = []
    for y, sat in enumerate(px):
        k = y / max(1, h - 1); zemin = tuple(ust[i] + (alt[i] - ust[i]) * k for i in range(3))
        yeni = []
        for r, g, b, a in sat:
            if a == 0: yeni.append((0, 0, 0, 0)); continue
            mx, mn = max(r, g, b), min(r, g, b)
            if mx - mn < 45:                      # beyaz/gri: yıldız ve gölgesi
                hedef, oran = (yildiz, lum((r, g, b)) / 255) if yildiz and mx > 150 else (None, 1)
            elif g > r and b > r:                 # turkuaz: hilal
                hedef, oran = hilal, lum((r, g, b)) / lum(TURKUAZ)
            else:                                 # altın: zemin
                hedef, oran = zemin, lum((r, g, b)) / lum(ALTIN)
            if hedef is None: yeni.append((r, g, b, a)); continue
            if hedef == (255, 255, 255): oran = min(oran, 1)
            yeni.append(tuple(max(0, min(255, int(v * oran))) for v in hedef) + (a,))
        out.append(yeni)
    return out

kaynak, hedef, tema = sys.argv[1], sys.argv[2], sys.argv[3]
for kl in sorted(os.listdir(kaynak)):
    if not kl.startswith('mipmap-') or kl.endswith('v26'): continue
    for ad in os.listdir(os.path.join(kaynak, kl)):
        if not ad.endswith('.png'): continue
        w, h, px = oku(os.path.join(kaynak, kl, ad))
        yaz(os.path.join(hedef, kl, ad), w, h, boya(px, h, tema))
print(tema, 'simgeleri yazıldı ->', hedef)
