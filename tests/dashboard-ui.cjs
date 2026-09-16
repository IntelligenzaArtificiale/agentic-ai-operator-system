// Isolated browser QA: synthetic fixtures only, no account or production services.
const {chromium} = require('playwright');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root=path.resolve(__dirname,'../atpa-v1/runtime/dashboard');
const out=path.resolve(__dirname,'../build/dashboard-qa');
fs.mkdirSync(out,{recursive:true});
const procedures=Array.from({length:14},(_,i)=>({
  meta:{slug:'test-'+i,name:i===0?'Processo da verificare':i===1?'Processo con nome molto lungo per verificare il comportamento della scheda e la leggibilità':'Processo di prova '+i,
    description:'Dati sintetici per la verifica della dashboard, non procedure aziendali reali.',department:i%2?'Amministrazione':'Operazioni',status:i%3?'validated':'draft',version:'1.0.0',roles:['Responsabile'],
    flow:{nodes:[{id:'read',label:'Leggi i dati',description:'Acquisizione delle informazioni.'},{id:'check',label:'Valuta il risultato',type:'condition'}],edges:[{from:'read',to:'check',label:'Completato'}]}},
  plan:{status:'compiled',blocks:4},path:'C:\\Test\\procedure\\test-'+i,
  metrics:{run_count:12,successful_runs:11,failed_runs:1,unverified_runs:0,average_duration_ms:12345,best_duration_ms:9876,incident_count:2,ai_interventions:4,deterministic_blocks:33,
    last_run:{outcome:i===0?'failed':'succeeded',at:'2026-09-16T08:00:00Z'},recent_runs:[{run_id:'qa-run',outcome:'succeeded',at:'2026-09-16T08:00:00Z',duration_ms:12345}],slowest_steps:[{label:'Verifica delle informazioni',samples:11,average_duration_ms:5000}]}
}));
let status=200;
let payload={version:'2.6.0',generated_at:'2026-09-16T10:00:00Z',company:{status:'configured',identity:{display_name:'Ambiente di verifica'},business:{summary:'Dati sintetici per il controllo visivo e funzionale.',sectors:['Servizi']},operations:{departments:['Operazioni']}},system:{codex:true,mcp:true,runner:true,plugin:true,recorder:true,checked_at:'2026-09-16T09:00:00Z'},counts:{runs:168,successful_runs:154,average_duration_ms:12345},procedures,warnings:[]};
const server=http.createServer((req,res)=>{
  if(req.url==='/api/data'){res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(payload));return;}
  const name=req.url==='/'?'index.html':path.basename(req.url.split('?')[0]);
  if(!['index.html','tokens.css','workspace.css','view.js','detail.js','dashboard.js'].includes(name)){res.writeHead(404);res.end();return;}
  res.writeHead(200,{'Content-Type':name.endsWith('.css')?'text/css':name.endsWith('.js')?'text/javascript':'text/html'});
  res.end(fs.readFileSync(path.join(root,name)));
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({executablePath:process.env.AIOS_QA_BROWSER || 'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  try {
    const page=await browser.newPage();
    const errors=[];page.on('pageerror',error=>errors.push(error.message));
    const url='http://127.0.0.1:'+server.address().port;
    await page.goto(url);await page.locator('.process-row').first().waitFor();
    const contrast=await page.evaluate(()=>{
      const css=getComputedStyle(document.documentElement), canvas=document.createElement('canvas');
      canvas.width=canvas.height=1; const ctx=canvas.getContext('2d');
      function luminance(token){ctx.fillStyle=css.getPropertyValue('--color-'+token).trim();ctx.fillRect(0,0,1,1);const rgb=[...ctx.getImageData(0,0,1,1).data].slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];}
      return [['ink','paper'],['muted','paper'],['muted','soft'],['surface','ink'],['success','success-bg'],['warning','warning-bg'],['error','error-bg'],['accent','surface']].map(([a,b])=>{const x=luminance(a),y=luminance(b);return {pair:a+'/'+b,ratio:(Math.max(x,y)+.05)/(Math.min(x,y)+.05)};});
    });
    assert(contrast.every(pair=>pair.ratio>=4.5),JSON.stringify(contrast));
    console.log('Contrast WCAG minimum:',Math.min(...contrast.map(pair=>pair.ratio)).toFixed(2));
    assert.equal(await page.locator('.process-row').count(),10);
    await page.getByRole('button',{name:'Successiva',exact:true}).click();
    assert.equal(await page.locator('.process-row').count(),4);
    await page.locator('#q').fill('inesistente');
    await page.getByRole('button',{name:'Azzera filtri'}).click();
    await page.locator('#status').selectOption('attention');
    assert.equal(await page.locator('.process-row').count(),1);
    await page.locator('#status').selectOption('');
    await page.locator('#department').selectOption('Amministrazione');
    assert.equal(await page.locator('.process-row').count(),7);
    await page.locator('#department').selectOption('');
    for(const width of [320,375,414,768,1440]) {
      await page.setViewportSize({width,height:1000});
      await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});
      await page.screenshot({path:path.join(out,'catalog-'+width+'.png'),fullPage:true});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth), 'catalog overflows '+width);
      await page.locator('[data-detail]').first().click();
      assert(await page.locator('#detail').evaluate(el=>el.scrollWidth<=el.clientWidth+1),'detail overflows '+width);
      await page.screenshot({path:path.join(out,'detail-'+width+'.png')});
      await page.keyboard.press('Escape');
    }
    await page.locator('[data-detail]').first().focus();await page.keyboard.press('Enter');
    await page.getByRole('button',{name:'Comando di avvio'}).click();
    assert.match(await page.locator('#command-text').inputValue(),/^\$avvia-procedura /);
    await page.locator('#copy-command').click();
    assert.match(await page.locator('#copy-status').textContent(),/Incollalo|Ctrl\+C/);
    await page.keyboard.press('Escape');await page.keyboard.press('Escape');
    payload={...payload,procedures:[],company:{status:'not_configured'},counts:{}};
    await page.locator('#refresh').click();await page.getByRole('button',{name:'Crea un processo',exact:true}).waitFor();
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:path.join(out,'empty.png'),fullPage:true});
    // Hostile text must stay inert, not create elements or handlers.
    payload={...payload,procedures:[{...procedures[0],meta:{...procedures[0].meta,name:'<img src=x onerror=alert(1)>'}}]};
    await page.locator('#refresh').click();await page.locator('.process-row').waitFor();
    assert.equal(await page.locator('.process-row img').count(),0);
    status=403;await page.locator('#refresh').click();await page.locator('.notice.error').waitFor();
    assert.equal(await page.locator('.process-row').count(),0);
    assert.match(await page.locator('#notice').textContent(),/Licenza non attiva/);
    await page.screenshot({path:path.join(out,'denied.png'),fullPage:true});
    assert.deepEqual(errors,[]);
    console.log('PASS: filters, pagination, keyboard, detail, copy fallback, 5 widths, empty, XSS, license denial.');
  } finally {await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
