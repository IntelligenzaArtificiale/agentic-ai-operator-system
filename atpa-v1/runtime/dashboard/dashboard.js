/* Catalog controller: preserves filters during refresh; never executes a procedure. */
(() => {
  const V=window.AiosView, {el,arr,esc}=V;
  let data=null, page=1, visible=[], pending=false;
  const pageSize=10;
  function render() {
    if(!data) return;
    const all=arr(data.procedures), q=el('q').value.trim().toLocaleLowerCase('it');
    let filtered=all.filter(item=>{
      const m=item.meta || {};
      return (!q || [m.name,m.description,m.department,...arr(m.roles)].join(' ').toLocaleLowerCase('it').includes(q))
        && (!el('department').value || m.department===el('department').value)
        && (!el('status').value || (el('status').value==='attention'?V.attention(item):m.status===el('status').value));
    });
    const name=(a,b)=>String(a.meta?.name||'').localeCompare(String(b.meta?.name||''),'it');
    const time=item=>Date.parse(item.metrics?.last_run?.at)||0;
    filtered.sort((a,b)=>{
      if(el('sort').value==='recent') return time(b)-time(a)||name(a,b);
      if(el('sort').value==='duration') return V.num(b.metrics?.average_duration_ms)-V.num(a.metrics?.average_duration_ms)||name(a,b);
      if(el('sort').value==='name') return name(a,b);
      return Number(V.attention(b))-Number(V.attention(a))||time(b)-time(a)||name(a,b);
    });
    const pages=Math.max(1,Math.ceil(filtered.length/pageSize)); page=Math.min(page,pages);
    visible=filtered.slice((page-1)*pageSize,page*pageSize);
    el('result-count').textContent=`${filtered.length} di ${all.length} processi`;
    el('grid').innerHTML=visible.length?visible.map(V.row).join(''):all.length
      ? '<div class="empty"><h2>Nessun processo con questi filtri.</h2><p>Prova un altro nome o visualizza tutti i reparti.</p><button id="clear-filters">Azzera filtri</button></div>'
      : '<div class="empty"><h2>Il primo processo parte da qui.</h2><p>Descrivi il lavoro da affidare all’agente. Poi collaudalo, verifica il risultato e ottimizzalo con dati reali.</p><button data-command="$crea-procedura-guidata" class="primary">Crea un processo</button></div>';
    el('pagination').innerHTML=filtered.length>pageSize?`<button id="prev" ${page===1?'disabled':''}>Precedente</button><span>Pagina ${page} di ${pages}</span><button id="next" ${page===pages?'disabled':''}>Successiva</button>`:'';
    el('prev')?.addEventListener('click',()=>{page--;render();});
    el('next')?.addEventListener('click',()=>{page++;render();});
    el('clear-filters')?.addEventListener('click',()=>{for(const id of ['q','department','status'])el(id).value='';page=1;render();});
  }
  async function refresh(manual=false) {
    if(pending || el('detail').open || el('command-dialog').open)return;
    if(!manual && el('grid').contains(document.activeElement))return;
    pending=true; el('refresh').disabled=true; el('refresh').setAttribute('aria-busy','true');
    const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),10000);
    try {
      const response=await fetch('/api/data',{cache:'no-store',signal:controller.signal});
      if(!response.ok) {
        if(response.status===403) {data=null;for(const id of ['grid','stats','company','system-body','pagination'])el(id).replaceChildren();el('company-name').textContent='Spazio aziendale';}
        throw new Error(response.status===403?'Licenza non attiva. Apri “Attiva Agentic AI Operator System” dal Desktop, verifica lo stato e riprova.':'Catalogo non disponibile. Usa “Visualizza procedure” nella chat e riprova.');
      }
      const next=await response.json();
      if(!next || !Array.isArray(next.procedures))throw new Error('Formato del catalogo non valido. Rigenera la dashboard dalla chat.');
      data=next;
      const selection=el('department').value;
      el('department').innerHTML='<option value="">Tutti i reparti</option>'+[...new Set(data.procedures.map(p=>p.meta?.department).filter(x=>typeof x==='string'&&x))].sort().map(x=>`<option value="${esc(x)}">${esc(x)}</option>`).join('');
      el('department').value=selection;
      V.company(data); V.system(data); V.stats(data); render();
      el('version').textContent='Versione '+data.version;
      el('updated').textContent='Aggiornato '+V.date(data.generated_at);
      el('notice').hidden=!arr(data.warnings).length; el('notice').className='notice';
      el('notice').textContent=arr(data.warnings).length?`${data.warnings.length} segnalazioni nella lettura dei dati. ${data.warnings.slice(0,3).join(' · ')}`:'';
    } catch(error) {
      el('notice').hidden=false; el('notice').className='notice error';
      el('notice').textContent=(error.name==='AbortError'?'Aggiornamento troppo lento. Premi Aggiorna per riprovare.':error.message)+(data?' I dati visibili sono quelli dell’ultimo aggiornamento riuscito.':'');
      if(!data)el('result-count').textContent='Catalogo non disponibile';
    } finally {
      clearTimeout(timeout);pending=false;el('refresh').disabled=false;el('refresh').removeAttribute('aria-busy');el('grid').setAttribute('aria-busy','false');
    }
  }
  for(const id of ['q','department','status','sort'])el(id).addEventListener(id==='q'?'input':'change',()=>{page=1;render();});
  el('grid').addEventListener('click',event=>{const button=event.target.closest('[data-detail]'); if(button && visible[Number(button.dataset.detail)])window.AiosDetail.show(visible[Number(button.dataset.detail)]);});
  el('refresh').addEventListener('click',()=>refresh(true));
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
  setInterval(()=>{if(!document.hidden)refresh();},30000);
  refresh();
})();
