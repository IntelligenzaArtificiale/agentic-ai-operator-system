/* Safe presentation helpers. Procedure content is text, never executable HTML. */
window.AiosView = (() => {
  const el = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const arr = value => Array.isArray(value) ? value : [];
  const num = value => typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : 0;
  const count = value => new Intl.NumberFormat('it-IT').format(num(value));
  const duration = value => {
    if (value == null || !Number.isFinite(value) || value < 0) return '—';
    if (value < 1000) return `${Math.round(value)} ms`;
    if (value < 60000) return `${(value / 1000).toLocaleString('it-IT', {maximumFractionDigits:1})} s`;
    if (value < 3600000) return `${Math.floor(value / 60000)} min ${Math.round(value % 60000 / 1000)} s`;
    return `${Math.floor(value / 3600000)} h ${Math.floor(value % 3600000 / 60000)} min`;
  };
  const date = value => value && Number.isFinite(Date.parse(value)) ? new Date(value).toLocaleString('it-IT', {dateStyle:'short',timeStyle:'short'}) : 'Data non disponibile';
  const state = value => ({draft:'Bozza',validated:'Collaudato',active:'Attivo',paused:'In pausa',archived:'Archiviato'}[value] || 'Stato da verificare');
  const outcome = value => ({succeeded:'Verificata',failed:'Non riuscita',unverified:'Da verificare',cancelled:'Annullata'}[value] || 'Nessun esito');
  const attention = item => ['failed','unverified'].includes(item.metrics?.last_run?.outcome);
  const badge = (label, tone='') => `<span class="badge ${tone}">${esc(label)}</span>`;
  function company(data) {
    const c = data.company || {};
    const name = c.identity?.display_name || c.identity?.legal_name || 'La tua azienda';
    el('company-name').textContent = c.status === 'configured' ? name : 'Spazio aziendale';
    el('create').textContent = c.status === 'configured' ? 'Nuovo processo' : 'Configura DNA';
    el('create').dataset.command = c.status === 'configured' ? '$crea-procedura-guidata' : '$profilo-azienda';
    el('company').innerHTML = c.status === 'configured'
      ? `<h2>DNA aziendale · ${esc(name)}</h2><p>${esc(c.business?.summary || 'Profilo configurato.')}</p><div class="company-tags">${[...arr(c.business?.sectors),...arr(c.operations?.departments)].slice(0,10).map(tag=>`<span>${esc(tag)}</span>`).join('')}</div><button data-command="$profilo-azienda">Aggiorna DNA</button>`
      : '<h2>Prima il contesto, poi i processi.</h2><p>Configura il DNA aziendale: attività, reparti e strumenti che l’agente userà per comprendere il tuo lavoro.</p><button data-command="$profilo-azienda">Configura DNA</button>';
  }
  function system(data) {
    const labels = {codex:'Codex',mcp:'Controllo Windows',runner:'Esecutore locale',plugin:'Skill AIOS',recorder:'OpenSteps'};
    el('system-body').innerHTML = `<div class="system-grid">${Object.entries(labels).map(([key,label])=>`<div><strong>${label}</strong><span>${data.system?.[key] ? (['codex','recorder'].includes(key)?'Installato':'Configurato') : 'Non rilevato'}</span></div>`).join('')}</div><p class="footnote">Configurazione rilevata: ${esc(date(data.system?.checked_at))}. Non è un controllo di esecuzione continua. Per aggiornare questi controlli usa “Visualizza procedure” nella chat.</p>`;
  }
  function stats(data) {
    const p = arr(data.procedures), c = data.counts || {};
    const values = [['Processi',count(p.length)],['Da verificare',count(p.filter(attention).length)],['Esecuzioni verificate',`${count(c.successful_runs)} / ${count(c.runs)}`],['Tempo medio verificato',duration(c.average_duration_ms)]];
    el('stats').innerHTML = values.map(([label,value])=>`<div><strong>${esc(value)}</strong><span>${label}</span></div>`).join('');
  }
  function row(item, index) {
    const m = item.meta || {}, t = item.metrics || {}, last = t.last_run;
    const tone = attention(item) ? (last.outcome==='failed'?'bad':'warn') : last?.outcome==='succeeded' ? 'good' : '';
    return `<article class="process-row"><div class="process-title"><h3>${esc(m.name || m.slug)}</h3>${badge(state(m.status))}<p>${esc(m.department || 'Reparto non definito')} · v${esc(m.version || '—')}</p><p class="description">${esc(m.description || 'Descrizione non disponibile.')}</p></div><div class="process-data"><div><span>Ultimo esito</span>${badge(last?outcome(last.outcome):'Non disponibile',tone)}<span>${last?esc(date(last.at)):'Nessuna run datata'}</span></div><div><span>Esecuzioni</span><strong>${count(t.run_count)}</strong><span>Media verificata</span><strong>${duration(t.average_duration_ms)}</strong></div></div><button data-detail="${index}" aria-label="Apri scheda ${esc(m.name || m.slug)}">Scheda →</button></article>`;
  }
  return {el,esc,arr,num,count,duration,date,state,outcome,attention,badge,company,system,stats,row};
})();
