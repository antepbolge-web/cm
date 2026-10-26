"""Notlar sayfasını (nc.html içindeki P_notlar parçası) tek başına açıp içe aktarmayı dener; yalnız SAYILARI yazar.
İkinci kez de içe aktarır: tekrar yüklemenin çift not üretmediğini görmek için."""
import base64, sys
kabuk = open(sys.argv[1], 'rb').read()
a = kabuk.index(b'id="P_notlar">') + len(b'id="P_notlar">'); e = kabuk.index(b'</script>', a)
t = base64.b64decode(kabuk[a:e].strip()).decode('utf-8')
j = base64.b64encode(open(sys.argv[2], 'rb').read()).decode()
js = r"""
<script type="text/plain" id="TESTJSON">%s</script><pre id="sonuc">BEKLIYOR</pre><script>
function yaz(s){document.getElementById('sonuc').textContent='SONUC '+s}
window.onerror=function(m){yaz('HATA '+m)};
function yukle(){var b=atob(document.getElementById('TESTJSON').textContent.trim()),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);
  var dt=new DataTransfer();dt.items.add(new File([u],'a.json',{type:'application/json'}));var inp=document.getElementById('yedekDosya');inp.files=dt.files;inp.dispatchEvent(new Event('change'))}
var n=0,t=setInterval(function(){if(!window.__hazir){if(++n>60){clearInterval(t);yaz('HATA hazir degil')}return}clearInterval(t);try{
  window.confirm=function(){return true};var S=__nt.S,once=S.notes.length,g=getComputedStyle(document.getElementById('yedekYukle')).display;
  yukle();setTimeout(function(){var bir=S.notes.length;yukle();setTimeout(function(){
    yaz('dugme='+g+' once='+once+' sonra='+bir+' ikinci='+S.notes.length+' cop='+S.notes.filter(function(n){return n.cop}).length+' klasor='+S.folders.length+' resimli='+S.notes.filter(function(n){return n.html.indexOf('data:image')>=0}).length+' pdf='+S.notes.filter(function(n){return n.html.indexOf('data:application/pdf')>=0}).length+' sabit='+S.notes.filter(function(n){return n.sabit}).length)},1500)},1500);
}catch(e){yaz('HATA '+e.message)}},200);
</script></body></html>""" % j
i = t.rindex('</body>')
open(sys.argv[3], 'wb').write((t[:i] + js).encode('utf-8'))
