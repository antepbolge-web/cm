"""Android mipmap ic_launcher.png dosyalarından (48-192 px) Windows .ico üretir; PNG'ler olduğu gibi gömülür.
Kullanım: python -I ico.py <res_klasoru> <cikti.ico>"""
import sys, os, struct
res, cikti = sys.argv[1], sys.argv[2]
pngs = []
for kl in ['mipmap-mdpi', 'mipmap-hdpi', 'mipmap-xhdpi', 'mipmap-xxhdpi', 'mipmap-xxxhdpi']:
    d = open(os.path.join(res, kl, 'ic_launcher.png'), 'rb').read()
    w, h = struct.unpack('>II', d[16:24])
    pngs.append((w, h, d))
bas = struct.pack('<HHH', 0, 1, len(pngs))
yer = 6 + 16 * len(pngs)
dizin, veri = b'', b''
for w, h, d in pngs:
    dizin += struct.pack('<BBBBHHII', w % 256, h % 256, 0, 0, 1, 32, len(d), yer + len(veri))
    veri += d
open(cikti, 'wb').write(bas + dizin + veri)
print(cikti, [p[0] for p in pngs])
