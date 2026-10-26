new Promise(function(ok){var n=0,t=setInterval(function(){var s=document.getElementById('sonuc').textContent;if(s.indexOf('SONUC')===0||++n>150){clearInterval(t);ok(s)}},200)})
