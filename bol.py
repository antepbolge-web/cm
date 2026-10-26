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

def mektubat_arama(v):
    """Mektubat gelişmiş arama (26.10.2026 kullanıcı: 'gelişmiş arama olsun'; 24.10'da 'numara/kelime/konu/muhatap süzme çok önemli').
    Kelimeler sırasız aranır, "tırnak" tam ifade; süzgeç: cilt, nerede, durum, numara aralığı; konu çipleri;
    sonuçta ve açılan mektupta eşleşme işaretlenir, ilk eşleşmeye kaydırılır."""
    css = (b'<style id="gelismis-arama">.suz{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;margin-bottom:12px}.suz[hidden]{display:none}'
           b'.suz label{display:flex;align-items:center;gap:6px;font-weight:600;font-size:17px}'
           b'.suz select,.suz input{min-height:44px;border-radius:12px;border:2px solid var(--line);background:var(--card);color:var(--tx);padding:0 8px;font-size:17px}'
           b'.suz input{width:80px}#sKonu:empty{display:none}#sBilgi{flex-basis:100%}'
           b'#suzD{flex-basis:100%}#suzD summary{min-height:44px;display:flex;align-items:center;gap:6px;font-weight:700;font-size:17px;cursor:pointer;color:var(--acc)}'
           b'.suzIc{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;padding:6px 0 4px}.lk span.parca{-webkit-line-clamp:3}'
           b'mark.bul{background:#fde68a;color:#111;border-radius:3px;padding:0 1px}</style>')
    html = ('<div class="suz" id="suz" hidden><details id="suzD"><summary id="suzOzet">Süzgeç</summary><div class="suzIc">'
            '<label>Cilt <select id="sCilt"><option value="0">Hepsi</option><option value="1">1. Cilt</option><option value="2">2. Cilt</option><option value="3">3. Cilt</option></select></label>'
            '<label>Nerede <select id="sYer"><option value="hepsi">Her yerde</option><option value="metin">Mektup metni</option><option value="muhatap">Muhatap</option><option value="konu">Konularım</option><option value="not">Notlarım</option></select></label>'
            '<label>Durum <select id="sDurum"><option value="hepsi">Hepsi</option><option value="okunmamis">Okunmamış</option><option value="okunmus">Okunmuş</option><option value="fav">Favori</option><option value="notlu">Notlu</option></select></label>'
            '<label>No <input id="sBas" type="number" min="1" inputmode="numeric" placeholder="ilk" aria-label="İlk numara"> – <input id="sSon" type="number" min="1" inputmode="numeric" placeholder="son" aria-label="Son numara"></label>'
            '<button class="btn sm" id="sSifirla" type="button">Süzgeci sıfırla</button></div></details>'
            '<div class="chips" id="sKonu"></div><div class="durum" id="sBilgi"></div></div>').encode()
    js = r"""/* ---- Gelişmiş arama (bolme/bol.py mektubat_arama) ---- */
var SZ=LSget('cafer_mektubat_suz',{c:'0',yer:'hepsi',d:'hepsi'}),VURGU=null,GOSTER=100,araTmr=0;
var ES=[['namaz','nemaz'],['zikir','zikr'],['fikir','fikr'],['sabir','sabr'],['sukur','sukr'],['kabir','kabr'],['nefis','nefs']];   // baskının yazımı: nemâz, zikr…
function cesit(t){var r=[t];ES.forEach(function(e){[0,1].forEach(function(i){if(t.indexOf(e[i])>=0){var y=t.split(e[i]).join(e[1-i]);if(r.indexOf(y)<0)r.push(y)}})});return r}
function terimler(ham){var q=norm(ham).trim(),m=q.match(/^["“”](.+)["“”]$/);return (m?[m[1].trim()]:q.split(/\s+/).filter(Boolean)).map(cesit)}
function duz(ts){return [].concat.apply([],ts)}
function alanMetni(k,yer){var e=S.m[k]||{};
  if(yer==='metin')return tnorm(k);
  if(yer==='muhatap')return norm(e.muhatap||'')+' '+tnorm(k).slice(0,700);
  if(yer==='not')return norm(e.not||'');
  if(yer==='konu')return norm((e.konu||[]).join(' '));
  return tnorm(k)+' '+norm([e.not,e.muhatap,kaynakAl(k),(e.konu||[]).join(' ')].join(' '))}
function haritali(s){var n='',m=[];for(var i=0;i<s.length;i++){var c=norm(s.charAt(i));for(var j=0;j<c.length;j++){n+=c.charAt(j);m.push(i)}}m.push(s.length);return {n:n,m:m}}
function isaretle(kutu,metin,ts){
  var h=haritali(metin),ar=[];
  ts.forEach(function(t){if(!t)return;var i=h.n.indexOf(t);while(i>=0){ar.push([h.m[i],h.m[i+t.length]]);i=h.n.indexOf(t,i+t.length)}});
  ar.sort(function(a,b){return a[0]-b[0]});var p=0,say=0;
  ar.forEach(function(r){if(r[0]<p)return;if(r[0]>p)kutu.appendChild(document.createTextNode(metin.slice(p,r[0])));var mk=el('mark','bul',metin.slice(r[0],r[1]));kutu.appendChild(mk);p=r[1];say++});
  if(p<metin.length)kutu.appendChild(document.createTextNode(metin.slice(p)));return say}
function parca(k,ts){var e=S.m[k]||{},m=metinAl(k);
  if(SZ.yer==='not'&&e.not)m=e.not;else if(SZ.yer==='konu')return 'Konular: '+(e.konu||[]).join(', ');
  m=m.replace(/\s+/g,' ');var n=norm(m),i=-1;
  duz(ts).forEach(function(t){var j=n.indexOf(t);if(j>=0&&(i<0||j<i))i=j});
  if(i<0)return m.slice(0,160);var a=Math.max(0,i-25);a=Math.max(0,m.lastIndexOf(' ',a)+1);return (a?'… ':'')+m.slice(a,a+220)+' …'}
function suzgecDurum(){$('sCilt').value=SZ.c;$('sYer').value=SZ.yer;$('sDurum').value=SZ.d;$('sBas').value=SZ.bas||'';$('sSon').value=SZ.son||'';
  var on=[];if(SZ.c!=='0')on.push(SZ.c+'. Cilt');if(SZ.yer!=='hepsi')on.push($('sYer').selectedOptions[0].textContent);if(SZ.d!=='hepsi')on.push($('sDurum').selectedOptions[0].textContent);if(SZ.bas||SZ.son)on.push('No '+(SZ.bas||'1')+'–'+(SZ.son||'son'));
  $('suzOzet').textContent='⚙ Süzgeç'+(on.length?': '+on.join(' · '):' (hepsi)');
  var tum={};Object.keys(S.m).forEach(function(k){(S.m[k].konu||[]).forEach(function(t){tum[t]=(tum[t]||0)+1})});
  var b=$('sKonu');b.textContent='';var ks=Object.keys(tum).sort();if(ks.length)b.appendChild(el('span','mut','Konularım:'));
  ks.forEach(function(t){var c=el('button','tag',t+' ('+tum[t]+')');c.type='button';c.onclick=function(){SZ.yer='konu';LSset('cafer_mektubat_suz',SZ);$('ara').value=t;GOSTER=100;notListe()};b.appendChild(c)})}
function notListe(){
  var ham=$('ara').value,q=norm(ham).trim(),box=$('nList'),bas=$('p-notlar').querySelector('h2');
  $('suz').hidden=!q;
  if(q){
    var m=q.match(/^(\d)\s*[:.\/]\s*(\d{1,3})$/);
    if(m&&+m[1]>=1&&+m[1]<=3&&+m[2]>=1&&+m[2]<=VOL[+m[1]-1]){var kk=key(+m[1],+m[2]);sekme('mektup');ac(kk);return}
    bas.textContent='Arama sonuçları';suzgecDurum();
    var ts=terimler(ham),nb=+SZ.bas||0,ns=+SZ.son||0;
    var tum={};Object.keys(S.m).forEach(function(k){tum[k]=1});Object.keys(TOHUM).forEach(function(k){tum[k]=1});
    var ks=Object.keys(tum).filter(function(k){
      var p=k.split(':'),c=+p[0],n=+p[1],e=S.m[k]||{};
      if(SZ.c!=='0'&&String(c)!==SZ.c)return false;if(nb&&n<nb)return false;if(ns&&n>ns)return false;
      if(SZ.d==='okunmamis'&&e.okundu)return false;if(SZ.d==='okunmus'&&!e.okundu)return false;if(SZ.d==='fav'&&!e.fav)return false;if(SZ.d==='notlu'&&!e.not)return false;
      var a=alanMetni(k,SZ.yer);return ts.every(function(c){return c.some(function(t){return a.indexOf(t)>=0})})}).sort(sirala);
    box.textContent='';
    var ust=ks.length+' mektup bulundu'+(ts.length>1&&!/^["“”]/.test(ham.trim())?' · kelimelerin hepsi geçenler (tam ifade: "tırnak")':'');
    $('sBilgi').textContent=ust;
    if(!ks.length){box.appendChild(el('p','mut','Sonuç bulunamadı. Süzgeci sıfırlamayı ya da daha az kelime yazmayı deneyin.'));return}
    ks.slice(0,GOSTER).forEach(function(k){var e=S.m[k]||{},b=el('button','lk');b.type='button';
      b.appendChild(el('b','',(e.fav?'★ ':'')+(e.okundu?'✓ ':'')+ad(k)+(e.muhatap?' · '+e.muhatap:'')));
      var s=el('span','parca');isaretle(s,parca(k,ts),duz(ts));b.appendChild(s);
      b.onclick=function(){VURGU={k:k,ts:duz(ts)};sekme('mektup');ac(k)};box.appendChild(b)});
    if(ks.length>GOSTER){var d=el('button','btn sm',(ks.length-GOSTER)+' sonuç daha · göster');d.type='button';d.onclick=function(){GOSTER+=100;notListe()};box.appendChild(d)}
    return;
  }
  bas.textContent='Notlarım';
  var ks2=Object.keys(S.m).filter(function(k){return S.m[k].not}).sort(sirala);
  liste(box,ks2,'Henüz not yok. Bir mektubu açıp "Notlarım" kutusuna yazın.');
}
[['sCilt','c'],['sYer','yer'],['sDurum','d'],['sBas','bas'],['sSon','son']].forEach(function(x){var g=$(x[0]);g.addEventListener(g.tagName==='SELECT'?'change':'input',function(){SZ[x[1]]=this.value;LSset('cafer_mektubat_suz',SZ);GOSTER=100;notListe()})});
$('sSifirla').onclick=function(){SZ={c:'0',yer:'hepsi',d:'hepsi'};LSset('cafer_mektubat_suz',SZ);GOSTER=100;notListe()};
function vurguUygula(box){
  if(!VURGU||VURGU.k!==cur)return;var ilk=null;
  box.querySelectorAll('p').forEach(function(p){var t=p.textContent,n=norm(t);if(!VURGU.ts.some(function(x){return n.indexOf(x)>=0}))return;p.textContent='';isaretle(p,t,VURGU.ts);if(!ilk)ilk=p.querySelector('mark.bul')});
  if(ilk)setTimeout(function(){ilk.scrollIntoView({block:'center'})},260)}
"""
    yama = [
        (b'<div class="liste" id="nList">', html + b'<div class="liste" id="nList">'),
        ('placeholder="Metin, not, muhatap, 1:45…"'.encode(), 'placeholder="Ara: kelime, &quot;tam ifade&quot;, 1:45…"'.encode()),
        (b"    box.appendChild(p);\n  });\n}\nfunction mod(", b"    box.appendChild(p);\n  });\n  vurguUygula(box);\n}\nfunction mod("),
        (b"$('ara').addEventListener('input',function(){if(this.value.trim()){",
         b"$('ara').addEventListener('input',function(){GOSTER=100;var me=this;clearTimeout(araTmr);araTmr=setTimeout(function(){araCalis.call(me)},180)});\nfunction araCalis(){if(this.value.trim()){"),
    ]
    for eski, yeni in yama:
        assert v.count(eski) == 1, ('arama yaması tutmadı', eski[:50])
        v = v.replace(eski, yeni)
    # eski notListe'nin yerine yenisi; arama satırının sonu: 'else sekme(A.tab)});' → işlev kapanışı
    a = v.index(b'function notListe(){')
    e = v.index(b"$('ara').addEventListener('input'", a)
    v = v[:a] + js.encode() + v[e:]
    eski = b"notListe()}else sekme(A.tab)});"
    assert v.count(eski) == 1, 'arama satırı sonu bulunamadı'
    v = v.replace(eski, b"notListe()}else sekme(A.tab)}")
    i = v.index(b'</head>')
    return v[:i] + css + v[i:]

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
            veri = mektubat_arama(mektubat2(veri))
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

# 5. Güncelleme uyarısı (26.10.2026 kullanıcı: 'açılışta yeni sürüm var'): 6. bağımsız değişken "paket:versionCode:versionName".
# Yalnız APK'da (Capacitor; kabuğun yerli() işlevi kapalı kapsamda, buradan görünmez) GitHub'daki surum.json okunur; orada daha büyük code varsa üstte şerit çıkar, "İndir" bağlantıyı tarayıcıda açar.
if len(sys.argv) > 6:
    pk, kod, sr = sys.argv[6].split(':')
    js = ("<script id=\"guncelle\">(function(){var P='%s',K=%d,S='%s';window.UYG_SURUM=S;"
          "try{if(!(window.Capacitor&&Capacitor.isNativePlatform&&Capacitor.isNativePlatform()))return}catch(e){return}"
          "fetch('https://raw.githubusercontent.com/antepbolge-web/cm/main/surum.json?t='+Date.now(),{cache:'no-store'})"
          ".then(function(r){return r.ok?r.json():null}).then(function(j){var s=j&&j[P];if(!s||!(s.code>K)||!s.link)return;"
          "var d=document.createElement('div');d.id='yeniSurum';d.setAttribute('role','status');"
          "d.style.cssText='position:fixed;left:8px;right:8px;top:calc(env(safe-area-inset-top,0px) + 8px);z-index:99999;display:flex;align-items:center;gap:8px;padding:10px 12px;border-radius:14px;background:#0f766e;color:#fff;font:600 16px/1.3 system-ui,Roboto,Arial,sans-serif;box-shadow:0 4px 16px rgba(0,0,0,.3)';"
          "var y=document.createElement('span');y.style.flex='1';y.textContent='Yeni s\\u00fcr\\u00fcm var: '+s.surum+' (sizdeki '+S+')';d.appendChild(y);"
          "var a=document.createElement('button');a.type='button';a.textContent='\\u0130ndir';"
          "a.style.cssText='min-height:44px;padding:0 16px;border:0;border-radius:10px;background:#d4a017;color:#111;font:700 16px system-ui,Roboto,Arial,sans-serif';"
          "a.onclick=function(){location.href=s.link};d.appendChild(a);"
          "var k=document.createElement('button');k.type='button';k.textContent='\\u2715';k.setAttribute('aria-label','Kapat');"
          "k.style.cssText='min-width:44px;min-height:44px;border:0;border-radius:10px;background:transparent;color:#fff;font:700 18px system-ui';"
          "k.onclick=function(){d.remove()};d.appendChild(k);document.body.appendChild(d)})['catch'](function(){})"
          "})();</script>\n" % (pk, int(kod), sr))
    degistir('</body></html>', js + '</body></html>')

open(cikti, 'wb').write(t.encode('utf-8'))
print(cikti, len(t.encode('utf-8')), 'bayt;', [s['tel'] for s in yeni], '| arama:', [k[1] for k in kay])
