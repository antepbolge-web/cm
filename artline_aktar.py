"""Artline Notepad (com.artline.notepad) yedeğini (backup_*.zip: notes.json, folders.json, attachments.zip)
Cafer Notlar'ın "Yedek yükle" biçimine çevirir: {v:2, notes:[...], folders:[...]}.
İçe aktarma birleştirir: mevcut notlar silinmez; aynı numaralı notta daha yeni olan kalır (tekrar yüklemek güvenli).
- Normal notlar → kendi klasörü (yoksa "Genel")
- Silinmiş (DELETED) ve kalıcı silinmiş (TERMINATED) notlar → Çöp (kullanıcı oradan geri alır ya da boşaltır)
- Resim ekleri notun sonuna gömülür (data: adresi); zengin nottaki telefon yoluna bağlı <img>'ler çıkarılır.
Kullanım: python -I artline_aktar.py <backup.zip> <cikti.json>   (not metni ekrana yazılmaz)"""
import zipfile, json, sys, base64, html, re, io, collections, time
SIMDI = int(time.time() * 1000)
kaynak, cikti = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(kaynak)
N = json.loads(z.read('notes.json'))
K = json.loads(z.read('folders.json'))
ekler = {}
if 'attachments.zip' in z.namelist():
    ez = zipfile.ZipFile(io.BytesIO(z.read('attachments.zip')))
    ekler = {i.filename.rsplit('/', 1)[-1]: ez.read(i) for i in ez.infolist() if not i.is_dir()}

klasorler = [k['title'].strip() or 'Klasör' for k in sorted(K.values(), key=lambda k: k.get('order', 0))]
kad = {kid: (k['title'].strip() or 'Klasör') for kid, k in K.items()}
notlar, say = [], collections.Counter()
for n in N:
    b = n['body']
    metin = b.get('text') or ''
    if b.get('isRich'):
        govde = re.sub(r'<img\b[^>]*>', '', metin, flags=re.I)
    else:
        govde = html.escape(metin).replace('\r\n', '\n').replace('\n', '<br>')
    for e in sorted(n['attachmentMap'].values(), key=lambda e: e.get('order', 0)):
        veri = ekler.get(e['id'])
        if veri and str(e.get('mimeType', '')).startswith('image/'):
            govde += '<p><img src="data:%s;base64,%s" alt="%s" style="max-width:100%%"></p>' % (e['mimeType'], base64.b64encode(veri).decode(), html.escape(e.get('fileName', '')))
            say['resim'] += 1
        elif veri:   # PDF vb.: notun içinde indirilebilir bağlantı
            ad = html.escape(e.get('fileName', 'dosya'))
            govde += '<p>📎 <a href="data:%s;base64,%s" download="%s">%s</a></p>' % (e.get('mimeType') or 'application/octet-stream', base64.b64encode(veri).decode(), ad, ad)
            say['dosya eki'] += 1
        else:
            govde += '<p>[Ek yedekte yok: %s]</p>' % html.escape(e.get('fileName', 'dosya'))
            say['eksik ek'] += 1
    baslik = n['title'].strip()
    if not baslik:
        ilk = re.sub(r'<[^>]+>', ' ', metin).strip().split('\n')[0].strip()
        baslik = ilk[:60] or '(başlıksız)'
    silindi = n['status'] in ('DELETED', 'TERMINATED')
    notlar.append({
        'id': 'artline-' + n['id'],
        'baslik': baslik,
        'html': govde,
        'klasor': kad.get(n['folderId'], 'Genel'),
        'etiket': ['Artline'] + [str(t) for t in n.get('tags') or []],
        'sabit': bool(n['isPinned']),
        'olusturma': n['createdTime'],
        'guncel': n['editedTime'] or n['createdTime'],
        # Notlar açılışta 30 günden eski çöpü kalıcı siler: çöpe atılma = aktarma anı, 30 gün geri alınabilir kalsın
        'cop': SIMDI if silindi else 0,
    })
    say['çöpe' if silindi else 'not'] += 1
    say['klasör: ' + notlar[-1]['klasor']] += 1
json.dump({'v': 2, 't': max(x['guncel'] for x in notlar), 'notes': notlar, 'tasks': [], 'folders': ['Genel'] + [k for k in klasorler if k != 'Genel'], 'klasorKilit': {}},
          open(cikti, 'w', encoding='utf-8'), ensure_ascii=False)
print(len(notlar), 'not yazıldı ->', cikti)
for k, v in sorted(say.items()):
    print(' ', k if not k.startswith('klasör: ') else 'klasör (%d harf)' % len(k[8:]), v)
