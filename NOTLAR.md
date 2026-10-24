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

## 1.6.2 (24.10.2026, telefon ekran görüntülerine göre)
7. Telefon koyu modda iken uygulamada "Açık" tema seçilince kartlar koyu kalıyordu (sayfa sonundaki `prefers-color-scheme:dark` + `html:not([data-theme])` kuralı). Çözüm: `temaEsle()` body'deki `light` sınıfını `html[data-theme]`'e yansıtır.
8. Kur'an-ı Kerim ve Mektubat menü girişleri gizli (CSS; sayfalar ve PDF APK'da duruyor, satırı silince geri gelir).
9. Sekme şeridi: Popüler | Yeni | Kategoriler | Favoriler.
10. Ayarlar'dan kaldırılanlar (CSS ile gizli): Yazı tipi, Açılış sayfası, Okuma kolaylığı, Hatırlatıcılar, Gizli klasörler, Menü düzenini sıfırla. Kalanlar: Dil, Tema, Yazı boyutu, Kart düzeni, Yedekle / Geri yükle, Hakkında.
- Menü sürüm yazısı `APK 1.6.2`, versionCode 3. Eski 1.6.1 APK'ları Drive `apk-indir\Eski`'de.

## 1.6.3 (24.10.2026)
11. Haberler: sayfanın üstünde "Türkçe | İngilizce" şeridi; tek dil görünür, seçim `cafer_haber_dil` ile hatırlanır. Menüdeki iki giriş (Yapay Zekâ / Teknoloji) aynı kaldı.
12. Şerit başlıkları (Popüler/Yeni/Kategoriler/Favoriler ve Türkçe/İngilizce) uzun basıp sürükleyince yer değiştirir; sıra `cafer_serit_sira` / `cafer_haber_sira` anahtarlarında. Sayfanın hazır `sortable()` işlevi kullanıldı (380 ms uzun basma). Menü zaten sürüklenebiliyordu (`cafer_menu_order`). Sürükleme bilgisayarda denenemedi, telefonda denenmeli.
13. Sade ve modern tema: düz kartlar (gölge/gradyan yok, 1 px çizgi, 16 px köşe), düz üst panel (kutusuz simgeler), tek vurgu rengi turkuaz (altın vurgular kalktı), sade menü, düz pencereler; Not Defteri iframe'inde gölgeler kapalı, zemin renkleri uyumlu. Renkler: açık zemin #f6f7f9 / kart #fff; koyu zemin #111317 / kart #1a1d23. Blok `ozel160.html` içinde "11)" başlığı; silince eski görünüm döner. 8 ekran iki temada Edge ile kontrol edildi.
- Kullanıcının 11:21'de gönderdiği "bulut simgesi duruyor" görüntüleri eski uygulamadan (menüde "APK 1.6" ve Kur'an girişi görünüyor). Yeni uygulama "Cafer AI Yeni" adıyla ayrı kurulu; iki uygulamanın simgesi aynı.
- Menü sürüm yazısı `APK 1.6.3`, versionCode 4. 1.6.2 APK'ları `apk-indir\Eski`'de.

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
