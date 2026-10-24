# Cafer AI Merkezi 1.6.x özelleştirme notları (24.10.2026)

Paket: `tr.cafer.aimerkezi` (Capacitor/WebView). Tüm arayüz `assets/public/index.html`.

## 1.6.1 değişiklikleri (`ozel160.html` bloğu + 2 küçük düzenleme)
1. Açılış her zaman Ana Sayfa: `let tab='best';`
2. Eşitle (bulut) simgesi gizli: CSS `#cafer-off-cloud, button[style*="99998"]{display:none}`
3. Üst panel her sayfada: geri, menü, başlık, ana sayfa, ara (Kur'an/Mektubat'a "Ara" eklendi)
4. Açık/koyu tema: Ana Sayfa, Yeni, Kategoriler, haberler, menü, Kur'an, Mektubat, Notlar, Yedek/Hakkında pencereleri bilgisayarda (Edge) iki temada denendi; ek kod gerekmedi
5. "Popüler | Yeni | Kategoriler" sekme şeridi (`#ozelSekme`)
6. Kur'an ve Mektubat üst paneli yüksek (min 96 px, simgeler 48 px)
- Menü sürüm yazısı: `APK 1.6.1`, versionCode 2.

## Dosyalar
- `cafer-ai-merkezi-1.6.0.apk`: özgün, Android Debug imzalı (telefondaki).
- `cafer-ai-merkezi-1.6.1.apk`: aynı paket adı; telefondaki üstüne kurulmaz (imza farklı), önce eskisi silinmeli.
- `cafer-ai-merkezi-1.6.1-yeni.apk`: paket `tr.cafer.aimerkezi.yeni`, ad "Cafer AI Yeni"; eskisiyle yan yana kurulur, notlar ayrı başlar.
- `ozel160.html`: eklenen CSS/JS bloğu. `index.1.6.1.html`: son index.html.
- İmza: `C:\Users\User\anahtarlar\cafer.jks` (alias cafer; parola dosyası git'e girmez). Yedek: Drive `apk-indir\anahtar-yedek`.

## Derleme
`apktool.jar d` → `assets/public/index.html` sonuna `ozel160.html` ekle (bayt düzeyinde; dosya karışık kodlamalı) → `apktool.jar b` → `zipalign -p 4` → `apksigner`. Ayrı sürüm için manifestte `package`, `authorities`, `DYNAMIC_RECEIVER...` izni ve `strings.xml` (`app_name`, `package_name`) değişir; `MainActivity` sınıf adı aynı kalır.

## Yedekleme (kullanıcı kararı 24.10.2026)
Google Drive (`apk-indir`) + GitHub. APK'lar `.gitignore` gereği git'e girmez; Drive'da durur. GitHub'da kaynak ve notlar tutulur.
