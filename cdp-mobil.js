// node cdp-mobil.js <sayfa.html> <genislik> <yukseklik> <ifade.js> [zamanasimi_ms] [yazi_olcegi]
// Gerçek telefon taklidi: mobile:true, deviceScaleFactor 3, dokunmatik. (Chrome penceresi en az ~500 px olduğundan emülasyon şart.)
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const [, , dosya, gen = '390', yuk = '844', ifadeDosya, tmo = '240000', olcek = '1'] = process.argv;
const port = 9300 + Math.floor(Math.random() * 600);
const CH = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'].find(p => fs.existsSync(p));
const prof = path.join(process.env.TEMP, 'cdpm-' + port);
const ch = spawn(CH, ['--headless=new', '--disable-gpu', '--remote-debugging-port=' + port, '--user-data-dir=' + prof, '--window-size=800,900', '--enable-features=TranslationAPI,OptimizationGuideOnDeviceModel', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const bekle = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  let sekmeler;
  for (let i = 0; i < 40; i++) { try { sekmeler = await (await fetch('http://127.0.0.1:' + port + '/json')).json(); if (sekmeler.length) break; } catch (e) {} await bekle(250); }
  const ws = new WebSocket(sekmeler.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);
  let id = 0; const bekleyen = {}; const logs = [];
  ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && bekleyen[d.id]) { bekleyen[d.id](d); delete bekleyen[d.id]; } else if (d.method === 'Runtime.exceptionThrown') logs.push(JSON.stringify(d.params.exceptionDetails).slice(0, 160)); };
  const gonder = (method, params = {}) => new Promise(r => { const i = ++id; bekleyen[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  await gonder('Runtime.enable'); await gonder('Page.enable');
  await gonder('Emulation.setDeviceMetricsOverride', { width: +gen, height: +yuk, deviceScaleFactor: 3, mobile: true, screenWidth: +gen, screenHeight: +yuk });
  await gonder('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
  await gonder('Emulation.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (Linux; Android 14; Redmi Note 14 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Mobile Safari/537.36' });
  if (process.env.ONCE) await gonder('Page.addScriptToEvaluateOnNewDocument', { source: 'if(window===top){' + process.env.ONCE + '}' });   // sayfa açılmadan önce (ör. localStorage hazırlığı)
  await gonder('Page.navigate', { url: 'file:///' + dosya.replace(/\\/g, '/') });
  await bekle(3000);
  const kod = fs.readFileSync(ifadeDosya, 'utf8');
  const t = setTimeout(() => { console.log('ZAMAN ASIMI'); process.exit(2); }, +tmo);
  const r = await gonder('Runtime.evaluate', { expression: kod, awaitPromise: true, returnByValue: true, userGesture: true });
  clearTimeout(t);
  console.log(r.result.exceptionDetails ? 'HATA ' + JSON.stringify(r.result.exceptionDetails).slice(0, 500) : 'SONUC ' + JSON.stringify(r.result.result.value));
  console.log('logs', JSON.stringify(logs));
  if (process.env.EKRAN) { const s = await gonder('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(process.env.EKRAN, Buffer.from(s.data || s.result.data, 'base64')); console.log('ekran', process.env.EKRAN); }
  ws.close(); ch.kill(); setTimeout(() => process.exit(0), 400);
})();
