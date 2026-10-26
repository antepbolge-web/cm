"""bolme/mektubat2/*.md -> tek dosya (Drive'daki Mektubat_2Cilt_Ceviri.md). Kullanım: python -I mektubat2_birlestir.py <çıktı.md>"""
import sys,re,glob,os
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'mektubat2'); out=sys.argv[1]
bol={};arap=''
for y in sorted(glob.glob(os.path.join(B,'*.md'))):
    t=open(y,encoding='utf-8').read()
    if '## Arapça metin' in t: t,a=t.split('## Arapça metin',1); arap='## Arapça metin'+a
    for b in re.split(r'\n(?=## \d+\. Mektup)','\n'+t)[1:]:
        n=int(re.match(r'## (\d+)\.',b).group(1)); bol[n]=b.split('\n---')[0].strip()
bas="""# Mektûbât 2. Cild — Türkçe deneme çevirisi (1–%d. mektuplar)

Kaynak: el-Menzilevî, Muhammed Murâd, *ed-Dürerü'l-meknûnât en-nefîse* (Mektûbât'ın Arapça tercümesi), 2. cüz, Hakîkat Kitâbevi, İstanbul 2002 (Vakfü'l-İhlâs). Drive: `PDF\Imam-i Rabbani Mektubati\mektubat rabbani ve masumi.pdf`; her mektubun PDF sayfası başlığının altında yazılıdır.
Yayınevinin notu (PDF s. 675): tercüme etmek ve basmak isteyen her Müslümana izin verilmiştir.
Asıl metin Farsçadır; bu çeviri Arapça tercümeden yapılmıştır (çevirinin çevirisi).
Çeviri: yapay zekâ (Claude), 26.10.2026. **Bir hocaya kontrol ettirilmeden kullanılmamalıdır.**
Bu dosya tek güncel sürümdür; yeni mektuplar buraya eklenir. Aynı metinler "Vakit ve Mektup" uygulamasında 2. Cilt olarak durur.
""" % max(bol)
open(out,'w',encoding='utf-8').write(bas+'\n---\n\n'+'\n\n---\n\n'.join(bol[k] for k in sorted(bol))+'\n\n---\n\n'+arap.replace('## Arapça metin (kontrol için','## Arapça metin (2. ve 5. mektup, kontrol için'))
print(sorted(bol), os.path.getsize(out))
