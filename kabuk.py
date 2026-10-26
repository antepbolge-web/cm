"""Hepsi index.html'den gömülü P_* parçalarını ayırır: kabuk.html (parçalar yerine yer tutucu) + parca_<id>.html"""
import sys, os, base64
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
t = open(src, 'rb').read()
kabuk = bytearray()
i = 0
while True:
    a = t.find(b'<script type="text/plain" id="P_', i)
    if a < 0:
        kabuk += t[i:]
        break
    b = t.find(b'>', a) + 1
    e = t.find(b'</script>', b)
    pid = t[a + len(b'<script type="text/plain" id="P_'):t.find(b'"', a + 33)].decode()
    open(os.path.join(out, 'parca_' + pid + '.html'), 'wb').write(base64.b64decode(t[b:e].strip()))
    kabuk += t[i:b] + b'@@' + pid.encode() + b'@@'
    i = e
open(os.path.join(out, 'kabuk.html'), 'wb').write(kabuk)
print(len(kabuk), 'bayt kabuk')
