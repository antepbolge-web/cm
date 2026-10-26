"""sadakat.net'teki Akçiçek tercümesi sayfalarından (Mektubat-ı Rabbani Tam Metin Tercümesi, Abdülkadir Akçiçek,
Çile Yayınları 1979) mektup metnini çıkarır. Sitede numaralar tek sıra: 1-313 = 1. cilt, 314-412 = 2. cilt, 413-534 = 3. cilt.
Kullanım: python -I akcicek_cikar.py <ham_klasör> <çıktı.json>   → {"2:1": metin, ..., "3:N": metin}
Kişisel kullanım içindir; çıktı herkese açık depoya konmaz (.gitignore: akcicek/)."""
import sys, os, re, html, json

def metin(v, no):
    a = re.search(r'%d\s*[.,](?:\s|&nbsp;|<[^>]+>)*MEKTUP' % no, v)   # bazı sayfalarda "528." ile "MEKTUP" arasında etiket, 524'te virgül var
    assert a, ('başlık yok', no)
    e = v.find('<ul class="pager', a.end())
    if e < 0:
        e = v.find('</article>', a.end())
    g = v[a.end():e]
    g = re.sub(r'<!--.*?-->', '', g, flags=re.S)
    g = re.sub(r'(?i)</p>|<br\s*/?>|</div>|</h\d>', '\n\n', g)
    g = html.unescape(re.sub(r'<[^>]+>', '', g)).replace('\xa0', ' ')
    pars = []
    for p in re.split(r'\n\s*\n', g):
        p = re.sub(r'\s+', ' ', p).strip()
        if p and not re.fullmatch(r'[*\s]+', p):
            pars.append(p)
    return '\n\n'.join(pars)

def main(ham, cikti):
    son = {}
    for f in sorted(os.listdir(ham)):
        m = re.match(r'\d+-(\d+)\.?mektup\.html$', f, re.I)
        if not m:
            continue
        no = int(m.group(1))
        k = '2:%d' % (no - 313) if no <= 412 else '3:%d' % (no - 412)
        t = metin(open(os.path.join(ham, f), encoding='utf-8').read(), no)
        if k in son:   # sitede aynı numara iki sayfada (ör. 152): birleştir
            t = son[k] + '\n\n' + t
        son[k] = t
    json.dump(son, open(cikti, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(son), 'mektup;', sum(len(t) for t in son.values()), 'karakter')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
