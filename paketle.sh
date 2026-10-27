#!/bin/bash
# Cafer Hepsi APK'sından (apktool ile açılmış) ayrı paketli APK üretir.
# Kullanım: bash paketle.sh <çalışma> <dec_hepsi> <html> <paket_soneki> "<Uygulama adı>" <tema> <versionCode> <versionName> <çıktı_adı>
# Örnek:    bash paketle.sh "$W" dec_h vm.html vakitmektup "Vakit ve Mektup" vakit 2 1.0.1 vakit-ve-mektup-1.0.1
set -e
W="$1"; H="$2"; HTML="$3"; PK="tr.cafer.$4"; AD="$5"; TEMA="$6"; VC="$7"; VN="$8"; N="$9"
BURA="$(cd "$(dirname "$0")" && pwd)"
cd "$W"; D="dec_$4"; rm -rf "$D"; cp -r "$H" "$D"
# paket adı (MainActivity sınıf adı değişmez)
sed -i "s/package=\"tr\.cafer\.hepsi\"/package=\"$PK\"/; s/tr\.cafer\.hepsi\.DYNAMIC_RECEIVER/$PK.DYNAMIC_RECEIVER/g; s/\"tr\.cafer\.hepsi\.fileprovider\"/\"$PK.fileprovider\"/; s/\"tr\.cafer\.hepsi\.androidx-startup\"/\"$PK.androidx-startup\"/" "$D/AndroidManifest.xml"
sed -i "s|>Cafer Hepsi</string>|>$AD</string>|g; s|>tr.cafer.hepsi</string>|>$PK</string>|g" "$D/res/values/strings.xml"
sed -i "s/versionCode: [0-9]*/versionCode: $VC/; s/versionName: .*/versionName: $VN/" "$D/apktool.yml"
[ "$(grep -o 'tr\.cafer\.hepsi[A-Za-z.]*' "$D/AndroidManifest.xml" | sort -u)" = "tr.cafer.hepsi.MainActivity" ] || { echo "HATA: manifestte eski paket adı kaldı"; exit 1; }
grep -q "Cafer Hepsi\|>tr.cafer.hepsi<" "$D/res/values/strings.xml" && { echo "HATA: strings.xml"; exit 1; }
# Konum izni yalnız Vakit'te gerekir ("Konumumu bul"); öbür uygulamalarda konum çağrısı yok (27.10.2026)
if [ "$4" != "vakitmektup" ]; then
  sed -i '/android\.permission\.ACCESS_\(FINE\|COARSE\)_LOCATION/d' "$D/AndroidManifest.xml"
  grep -q "_LOCATION" "$D/AndroidManifest.xml" && { echo "HATA: konum izni kaldı"; exit 1; }
fi
# Capacitor ayarında Hepsi'nin adı kalmasın
sed -i "s/\"appId\": \"tr\.cafer\.hepsi\"/\"appId\": \"$PK\"/; s/\"appName\": \"Cafer Hepsi\"/\"appName\": \"$AD\"/" "$D/assets/capacitor.config.json"
grep -q "tr\.cafer\.hepsi\|Cafer Hepsi" "$D/assets/capacitor.config.json" && { echo "HATA: capacitor.config.json"; exit 1; }
cp "$HTML" "$D/assets/public/index.html"
python -I "$BURA/simge.py" "$H/res" "$D/res" "$TEMA"
bash /c/Users/User/.claude/skills/cafer-apk-ozellestirme/betikler/derle.sh "$W" "$D" "$N"
python -I -c "
import zipfile,sys
print('sayfa ayni:', zipfile.ZipFile(sys.argv[1]).read('assets/public/index.html')==open(sys.argv[2],'rb').read())" "$N.apk" "$HTML"
