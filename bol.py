"""Cafer Hepsi kabuğundan seçili sekmelerle tek uygulama sayfası üretir.
Kullanım: python -I bol.py <k_klasoru> <cikti.html> "<Uygulama adı>" <id,id,...> <ara_kaynaklari,...>
Örnek:    python -I bol.py k_exe vakit.html "Vakit ve Mektup" vakit,mektubat mektubat,kuran
Kaynak sayfalara dokunmaz; yalnız kabuktaki listeleri süzer. Yedek dosyası 'Cafer Hepsi' biçiminde kalır
ki Hepsi'den alınan yedek yeni uygulamada 'Geri yükle' ile açılabilsin."""
import sys, os, base64, json, re
kdir, cikti, ad, ids, ara = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(','), sys.argv[5].split(',')
t = open(os.path.join(kdir, 'kabuk.html'), 'rb').read().decode('utf-8').replace('\r\n', '\n')

def degistir(eski, yeni, say=1):
    global t
    n = t.count(eski)
    assert n == say, (eski[:60], n)
    t = t.replace(eski, yeni)

def fazilet(v):
    """Vakit sayfası yaması: Fazilet Takvimi yöntemi (26.10.2026 kullanıcı isteği).
    Kaynak: Fazilet Takvimi açıklaması (kunfeyekun.org 23572, zehirliok.aciz.net/web/fazilettakvimi):
    imsak 19°, yatsı 17°; imsak -10, güneş -5, öğle/ikindi/yatsı +10, akşam +7 dk; ikindi asr-ı evvel (sayfada zaten)."""
    yama = [
        (b"// Diyanet'e yakin ayarlar: imsak 18, yatsi 17; dakika duzeltmeleri",
         b"// Fazilet Takvimi: imsak 19, yatsi 17; temkinler: imsak -10, gunes -5, ogle/ikindi/yatsi +10, aksam +7"),
        (b"var AYAR={fajr:18,isha:17,imsak:10,dk:{imsak:0,fajr:0,sunrise:-7,dhuhr:5,asr:4,maghrib:7,isha:0}};",
         b"var AYAR={fajr:19,isha:17,imsak:10,dk:{imsak:0,fajr:-10,sunrise:-5,dhuhr:10,asr:10,maghrib:7,isha:10}};"),
        ("Hesap: İmsak 18°, Yatsı 17°, Diyanet düzeltmeleriyle. Türkiye saati (UTC+3). Resmî ezan saati için Diyanet takvimine bakın.".encode(),
         "Hesap: Fazilet Takvimi yöntemi (İmsak 19°, Yatsı 17°, ikindi asr-ı evvel, Fazilet temkinleriyle). Türkiye saati (UTC+3). Basılı Fazilet Takvimi ile 1-2 dk fark olabilir.".encode()),
    ]
    for eski, yeni in yama:
        assert v.count(eski) == 1, ('fazilet yaması tutmadı', eski[:50])
        v = v.replace(eski, yeni)
    return v

def notlar_telefon(v):
    """Notlar telefonda (<=760 px): liste tam boy; düzenleyici yalnız not açılınca tam ekran, '← Notlar' ve geri tuşuyla kapanır.
    (26.10.2026 kullanıcı: 'alttaki bölüm asıl alanı kapatıyor'). Bilgisayar düzeni değişmez."""
    css = (b'<style id="tel-duzen">@media (max-width:760px){'
           b'.nlist{max-height:none!important;overflow:visible!important}#edBos{display:none!important}'
           b'#ed:not([hidden]),#kilitP:not([hidden]){position:fixed;inset:0;z-index:30;overflow:auto;background:var(--bg);margin:0;border-radius:0;padding:8px 10px 28px}'
           b'.edKapat{display:flex!important}}'
           b'.edKapat{display:none;align-items:center;gap:6px;min-height:48px;margin:0 0 8px;padding:0 16px;border-radius:12px;border:2px solid var(--line);background:var(--card);color:var(--tx);font:700 18px/1 system-ui,Roboto,Arial,sans-serif;cursor:pointer}'
           b'</style>')
    # Kod sayfanın kapalı kapsamında, açılışın sonunda çalışır: cur, ac, listeCiz, degisti oradan erişilir
    js = (b"(function(){var tel=window.matchMedia('(max-width:760px)'),kayit=false;"
          b"function kapat(geri){if(cur){try{degisti()}catch(e){}}cur=null;$('ed').hidden=true;$('kilitP').hidden=true;$('edBos').hidden=false;try{resBarGizle()}catch(e){}listeCiz();"
          b"if(kayit){kayit=false;if(!geri)try{history.back()}catch(e){}}}"
          b"['ed','kilitP'].forEach(function(k){var b=document.createElement('button');b.type='button';b.className='edKapat';b.textContent='\xe2\x86\x90 Notlar';b.onclick=function(){kapat(false)};$(k).insertBefore(b,$(k).firstChild)});"
          b"var eskiAc=ac;ac=function(id){var r=eskiAc.apply(this,arguments);if(tel.matches&&cur&&!kayit){kayit=true;try{history.pushState({not:1},'')}catch(e){}}return r};"
          b"window.addEventListener('popstate',function(){if(kayit){kayit=false;kapat(true)}});"
          b"})();\n  window.__hazir=true;")
    eski = b'  window.__hazir=true;'
    assert v.count(eski) == 1, 'notlar telefon yaması tutmadı'
    v = v.replace(eski, js)
    i = v.index(b'</style></head><body>')   # ilk </head>; ikincisi Word dışa aktarma şablonunun içinde
    return v[:i + 8] + css + v[i + 8:]

def mektubat2_metinler():
    """bolme/mektubat2/*.md içindeki '## N. Mektup — Muhatap' bölümlerini {'2:N': metin} yapar.
    Çeviri: Menzilevî'nin Arapça tercümesinden (Hakîkat Kitâbevi 2002), yapay zekâ, hoca kontrolünden geçmedi."""
    import glob
    uyari = '⚠ Deneme çevirisi: yapay zekâ ile Arapça tercümeden (Menzilevî, ed-Dürerü\'l-meknûnât, Hakîkat Kitâbevi 2002) çevrildi. Hoca kontrolünden geçmedi; bir hocaya danışmadan esas almayın.'
    son = {}
    for yol in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mektubat2', '*.md'))):
        md = '\n' + open(yol, encoding='utf-8').read().split('\n## Arapça metin')[0]   # baştaki '\n': dosya '## ' ile başlarsa ilk mektup atlanmasın
        for b in re.split(r'\n(?=## \d+\. Mektup)', md)[1:]:
            m = re.match(r'## (\d+)\. Mektup — (.+)\n', b)
            govde = b[m.end():].split('\n---')[0].strip()
            ilk, _, kalan = govde.partition('\n\n')
            ilk = re.sub(r'\s*\(PDF s\.[^)]*\)\s*$', '', ilk).strip('* ')
            if 'yazılmıştır' not in ilk:
                ilk = 'Bu mektup, %s yazılmıştır. %s' % (m.group(2).strip(), ilk)
            metin = uyari + '\n\n' + ilk + '\n\n' + kalan.replace('*', '').strip()
            assert '2:' + m.group(1) not in son, ('iki kez', m.group(1))
            son['2:' + m.group(1)] = metin
    return son

def mektubat2(v):
    """Mektubat sayfasına 2. cildin çevrilen mektuplarını ekler (26.10.2026 kullanıcı: '2. Cild olarak ekle')."""
    import gzip
    ek = mektubat2_metinler()
    a = v.index(b'<script type="text/plain" id="TOHUM">') + len(b'<script type="text/plain" id="TOHUM">')
    e = v.index(b'</script>', a)
    tohum = json.loads(gzip.decompress(base64.b64decode(v[a:e].strip())))
    assert not any(k.startswith('2:') for k in tohum), 'TOHUM zaten 2. cilt içeriyor'
    tohum.update(ek)
    yeni = base64.b64encode(gzip.compress(json.dumps(tohum, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9, mtime=0))
    v = v[:a] + yeni + v[e:]
    yama = [
        (b"function kaynakAl(k){var e=S.m[k];return (e&&e.kaynak)||(TOHUM[k]?KAYNAK:'')}",
         "var KAYNAK2='Mektûbât 2. Cild — Menzilevî, ed-Dürerü\\'l-meknûnât (Arapça tercüme), Hakîkat Kitâbevi 2002; Türkçesi yapay zekâ deneme çevirisi, hoca kontrolünden geçmedi';"
         "function kaynakAl(k){var e=S.m[k];return (e&&e.kaynak)||(TOHUM[k]?(k.charAt(0)==='2'?KAYNAK2:KAYNAK):'')}".encode()),
        ('2. ve 3. cild metinlerini kendiniz ekleyebilirsiniz.'.encode(),
         ('2. cildin %d mektubu (%s) Arapça tercümeden yapay zekâ ile çevrilmiş <b>deneme</b> metnidir, hoca kontrolünden geçmemiştir. '
          '3. cild metinlerini kendiniz ekleyebilirsiniz.' % (len(ek), ', '.join(k[2:] for k in sorted(ek, key=lambda k: int(k[2:]))))).encode()),
        ('Metinli (1. Cild)</title>'.encode(), 'Metinli (1. ve 2. Cild)</title>'.encode()),
    ]
    for eski, yeni in yama:
        assert v.count(eski) == 1, ('mektubat2 yaması tutmadı', eski[:50])
        v = v.replace(eski, yeni)
    return v

# 1. Sekme listesi: yalnız seçilenler (+ arama)
a = t.index('var SAYFA=') + len('var SAYFA=')
e = t.index(',AD=SAYFA', a)
SAYFA = json.loads(t[a:e])
yeni = [s for s in SAYFA if s['id'] in ids or s['id'] == 'ara']
assert len(yeni) == len(ids) + 1, 'eksik sekme'
t = t[:a] + json.dumps(yeni, ensure_ascii=False, separators=(',', ':')) + t[e:]

# 2. Gömülü parçalar: seçilmeyenlerin script satırı silinir
for s in SAYFA:
    if s['id'] == 'ara':
        continue
    satir = '<script type="text/plain" id="P_%s">@@%s@@</script>' % (s['id'], s['id'])
    if s['id'] in ids:
        veri = open(os.path.join(kdir, 'parca_' + s['id'] + '.html'), 'rb').read()
        if s['id'] == 'vakit':
            veri = fazilet(veri)
        if s['id'] == 'mektubat':
            veri = mektubat2(veri)
        if s['id'] == 'notlar':   # "Yedek yükle" görünsün: eski not yedekleri (Artline dönüşümü dahil) silmeden birleştirilir
            eski = b'#yedekAl,#yedekYukle,#yedekDurum{display:none!important}'
            assert veri.count(eski) == 1, 'notlar yaması tutmadı'
            veri = veri.replace(eski, b'#yedekAl,#yedekDurum{display:none!important}')
            veri = notlar_telefon(veri)
        degistir(satir, satir.replace('@@%s@@' % s['id'], base64.b64encode(veri).decode()))
    else:
        sonu = '\r\n' if satir + '\r\n' in t else '\n'
        degistir(satir + sonu, '')

# 3. Arama kaynakları: yalnız bu uygulamada bulunanlar
a = t.index('var ARA_KAYNAK = ') + len('var ARA_KAYNAK = ')
e = t.index(';\n', a)
kay = json.loads(t[a:e].replace("'", '"').replace('"Kur"an"', '"Kur\'an"'))
kay = [k for k in kay if k[0] in ara]
assert len(kay) == len(ara), 'eksik arama kaynağı'
t = t[:a] + json.dumps(kay, ensure_ascii=False) + t[e:]
a = t.index('kay: {', t.index('var ARA_AYAR')) + len('kay: {')
e = t.index('}', a)
t = t[:a] + ', '.join('%s: true' % k[0] for k in kay) + t[e:]

# 4. Ad ve yedek dosya adı
degistir('<title>Cafer Hepsi</title>', '<title>%s</title>' % ad)
degistir('<b id="baslik">Cafer Hepsi</b>', '<b id="baslik">%s</b>' % ad)
dosya = re.sub(r'[^a-z0-9]+', '-', ad.lower().translate(str.maketrans('çğıöşü', 'cgiosu'))).strip('-')
degistir("var ad='cafer-hepsi-yedek-'", "var ad='%s-yedek-'" % dosya)
degistir("// açılışta her zaman Cafer AI Merkezi", "// açılışta ilk sekme")
# Tek sekmeli uygulamada alt çubuğun işlevi yok: gizle, telefonun alt sistem çubuğu payı korunsun
if len(ids) == 1:
    degistir('</style></head><body>', 'nav{display:none!important}body{padding-bottom:var(--alt-bosluk)}\n</style></head><body>')
# Tek Kur'an yönlendirmesi yalnız Vakit sekmesi varken (yoksa Merkez kendi Kur'an'ını açar)
if 'vakit' not in ids:
    degistir("if(f===fr.merkez&&typeof w.openApp==='function'", "if(false&&f===fr.merkez&&typeof w.openApp==='function'")

open(cikti, 'wb').write(t.encode('utf-8'))
print(cikti, len(t.encode('utf-8')), 'bayt;', [s['tel'] for s in yeni], '| arama:', [k[1] for k in kay])
