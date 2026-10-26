import json, struct, sys, os
src, out = sys.argv[1], sys.argv[2]
f = open(src, 'rb')
d = f.read(16)
hlen = struct.unpack('<I', d[12:16])[0]
hdr = json.loads(f.read(hlen))
base = 16 + ((hlen + 3) & ~3) - 0
# asar: pickle header size at [4:8]; data starts at 8 + that size
psize = struct.unpack('<I', d[4:8])[0]
base = 8 + psize

def walk(node, path):
    for k, v in node.get('files', {}).items():
        p = path + '/' + k
        if 'files' in v:
            walk(v, p)
        elif 'offset' in v:
            print(v['size'], p)
            if not v.get('unpacked'):
                f.seek(base + int(v['offset']))
                dst = os.path.join(out, p.lstrip('/'))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'wb').write(f.read(v['size']))
walk(hdr, '')
