// Cafer Ailesi ortak "Yeni sürüm var" şeridi (03.11.2026, Cafer Bey seçti: yüzen turkuaz şerit, her uygulamada aynı).
// Her uygulamada aynı dosya. Kabuk kendi sürümünü bilir ve bir kez çağırır:
//   CaferSurum.denetle({ anahtar: 'depo', kod: 5, surum: '2.1.2', ac: function (link) { ... } });
// anahtar = cm/surum.json'daki kayıt (bilgisayar programlarında 'pc_…'). ac yoksa İndir yerine
// "Drive → apk-indir" yazar. ✕ o sürümü bir daha göstermez; daha yeni sürüm gelince şerit yine çıkar.
// Kotlin uygulamalarındaki eşi CaferSurum.kt; renkler ve yazılar ikisinde aynı tutulur.
(function () {
  var ADRES = 'https://raw.githubusercontent.com/antepbolge-web/cm/main/surum.json';
  var ZEMIN = '#0f766e', ALTIN = '#e8b630';

  function gizliOku(a) {
    try { return Number(localStorage.getItem('cafer_surum_gizli_' + a)) || 0; } catch (e) { return 0; }
  }
  function gizle(a, kod) {
    try { localStorage.setItem('cafer_surum_gizli_' + a, String(kod)); } catch (e) {}
  }

  function dugme(yazi, css) {
    var b = document.createElement('button');
    b.type = 'button'; b.textContent = yazi;
    b.style.cssText = 'flex:none;min-height:44px;border:0;border-radius:10px;cursor:pointer;font:700 16px/1 system-ui,Roboto,"Segoe UI",Arial,sans-serif;' + css;
    return b;
  }

  // s = surum.json kaydı {code, surum, link}; o = denetle() seçenekleri
  function ciz(s, o) {
    var eski = document.getElementById('yeniSurum');
    if (eski) eski.remove();
    var d = document.createElement('div');
    d.id = 'yeniSurum'; d.setAttribute('role', 'status');
    d.style.cssText = 'position:fixed;left:8px;right:8px;top:calc(env(safe-area-inset-top,0px) + 8px);z-index:99999;' +
      'max-width:560px;margin:0 auto;box-sizing:border-box;display:flex;align-items:center;gap:8px;padding:8px 8px 8px 14px;' +
      'border-radius:14px;background:' + ZEMIN + ';color:#fff;box-shadow:0 4px 16px rgba(0,0,0,.3);' +
      'font:600 16px/1.3 system-ui,Roboto,"Segoe UI",Arial,sans-serif;text-align:left';
    var y = document.createElement('div');
    y.style.cssText = 'flex:1;min-width:0';
    var b1 = document.createElement('div');
    b1.textContent = 'Yeni sürüm var: ' + s.surum;
    var b2 = document.createElement('div');
    b2.style.cssText = 'font-weight:400;font-size:14px;opacity:.9';
    b2.textContent = o.ac ? (o.surum ? 'Sizdeki: ' + o.surum : '') : 'Drive → apk-indir klasöründen indirin';
    y.appendChild(b1);
    if (b2.textContent) y.appendChild(b2);
    d.appendChild(y);
    if (o.ac) {
      var a = dugme('İndir', 'padding:0 16px;background:' + ALTIN + ';color:#111');
      a.onclick = function () { o.ac(s.link); };
      d.appendChild(a);
    }
    var k = dugme('✕', 'min-width:44px;padding:0;background:rgba(255,255,255,.18);color:#fff;font-size:18px');
    k.setAttribute('aria-label', 'Bu sürümü gösterme');
    k.title = 'Bu sürümü gösterme';
    k.onclick = function () { gizle(o.anahtar, s.code); d.remove(); };
    d.appendChild(k);
    (document.body || document.documentElement).appendChild(d);
    return d;
  }

  function denetle(o) {
    if (!o || !o.anahtar || !(o.kod > 0) || typeof fetch !== 'function') return Promise.resolve(null);
    return fetch(ADRES + '?t=' + Date.now(), { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        var s = j && j[o.anahtar];
        if (!s || !(s.code > o.kod) || s.code === gizliOku(o.anahtar)) return null;
        if (!/^https:\/\//.test(String(s.link || ''))) return null;
        var git = function () { ciz(s, o); };
        if (document.body) git(); else document.addEventListener('DOMContentLoaded', git);
        return s;
      })['catch'](function () { return null; }); // internet yoksa sessizce geç
  }

  window.CaferSurum = { denetle: denetle, ciz: ciz };
})();
