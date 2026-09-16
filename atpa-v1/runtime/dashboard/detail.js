/* Read-only process drill-down; commands are copied, never automatically executed. */
window.AiosDetail = (() => {
  const {el,esc,arr,count,duration,date,state,outcome,badge} = window.AiosView;
  function show(item) {
    const m=item.meta || {}, t=item.metrics || {}, plan=item.plan || {};
    const nodes=arr(m.flow?.nodes), edges=arr(m.flow?.edges);
    const command = `$avvia-procedura ${JSON.stringify(String(m.name || m.slug || ''))}`;
    const metrics=[['Esecuzioni',count(t.run_count)],['Verificate',count(t.successful_runs)],['Non riuscite',count(t.failed_runs)],['Non verificate',count(t.unverified_runs)],['Tempo medio',duration(t.average_duration_ms)],['Miglior tempo',duration(t.best_duration_ms)],['Blocchi locali',count(t.deterministic_blocks)],['Interventi IA',count(t.ai_interventions)]];
    el('detailBody').innerHTML = `${badge(state(m.status))}<h2 id="detail-title" class="detail-title">${esc(m.name || m.slug)}</h2><p>${esc(m.description)}</p><p class="muted">${esc(m.department || 'Reparto non definito')} · versione ${esc(m.version || '—')}</p>
      <div class="detail-actions"><button class="primary" data-command="${esc(command)}">Comando di avvio</button><button data-command="${esc('$collauda-procedura '+JSON.stringify(String(m.name || m.slug || '')))}">Collauda</button><button data-command="${esc('$ottimizza-procedura '+JSON.stringify(String(m.name || m.slug || '')))}">Ottimizza</button></div>
      <p class="footnote">L’esecuzione avviene nella chat, con i controlli previsti dalla procedura. Aprire questa scheda non avvia alcuna azione.</p>
      <section class="detail-section"><h3>Risultati registrati</h3><dl class="metric-grid">${metrics.map(([key,value])=>`<div><dt>${key}</dt><dd>${esc(value)}</dd></div>`).join('')}</dl></section>
      <section class="detail-section"><h3>Ultime esecuzioni</h3><ol class="history">${arr(t.recent_runs).length?arr(t.recent_runs).map(run=>`<li>${badge(outcome(run.outcome),run.outcome==='failed'?'bad':run.outcome==='succeeded'?'good':'warn')} · ${duration(run.duration_ms)}<small>${esc(date(run.at))} · ${esc(run.run_id)}</small></li>`).join(''):'<li>Nessuna esecuzione registrata.</li>'}</ol><p class="footnote">Le run prive di data restano nello storico, ma non determinano l’ultimo esito.</p></section>
      <section class="detail-section"><h3>Dove si concentra il tempo</h3>${arr(t.slowest_steps).length?arr(t.slowest_steps).map(step=>`<div class="step-time"><span>${esc(step.label)}<br><small>${count(step.samples)} campioni verificati</small></span><strong>${duration(step.average_duration_ms)}</strong></div>`).join(''):'<p class="muted">I tempi per passaggio compariranno dopo un’esecuzione verificata.</p>'}</section>
      <section class="detail-section"><h3>Passaggi e collegamenti</h3><ol class="flow-list">${nodes.length?nodes.map(node=>`<li><strong>${esc(node.label || node.id)}</strong>${node.type==='condition'?' · Decisione':''}<p>${esc(node.description || '')}</p></li>`).join(''):'<li>Nessun flusso definito.</li>'}</ol>${edges.length?`<details><summary>Mostra collegamenti (${edges.length})</summary><ul>${edges.map(edge=>`<li>${esc(edge.from || edge.source)} → ${esc(edge.to || edge.target)} ${esc(edge.label || edge.condition || '')}</li>`).join('')}</ul></details>`:''}</section>
      <section class="detail-section"><h3>Esperienza e automazione</h3><p>${count(t.incident_count)} incidenti documentati. Piano: ${esc(({compiled:'compilato',exploratory:'in apprendimento',missing:'non disponibile'}[plan.status]) || 'da verificare')} · ${count(plan.blocks)} blocchi.</p><p class="footnote">Un piano compilato non dimostra da solo l’autonomia del processo. Gli esiti verificati e le guardie di esecuzione restano necessari.</p><p class="path">${esc(item.path)}</p></section>`;
    el('detail').showModal();
  }
  function command(value) {
    el('command-text').value = value;
    el('copy-status').textContent='';
    el('copy-command').textContent='Copia comando';
    el('copy-command').removeAttribute('data-state');
    el('command-dialog').showModal();
    el('command-text').focus();
  }
  el('copy-command').addEventListener('click', async () => {
    const button=el('copy-command'); button.disabled=true; button.setAttribute('aria-busy','true');
    try {
      await navigator.clipboard.writeText(el('command-text').value);
      button.textContent='Copiato'; button.dataset.state='success';
      el('copy-status').textContent='Incollalo nella chat per continuare.';
    } catch {
      button.dataset.state='error';
      el('copy-status').textContent='Copia automatica non disponibile. Seleziona il comando e premi Ctrl+C.';
      el('command-text').focus(); el('command-text').select();
    } finally { button.disabled=false; button.removeAttribute('aria-busy'); }
  });
  for (const [dialog,button] of [['detail','close-detail'],['command-dialog','close-command']]) {
    el(button).addEventListener('click',()=>el(dialog).close());
    el(dialog).addEventListener('click',event=>{if(event.target===el(dialog)){
      const box=el(dialog).getBoundingClientRect();
      if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom) el(dialog).close();
    }});
  }
  document.addEventListener('click',event=>{const button=event.target.closest('[data-command]'); if(button)command(button.dataset.command);});
  return {show,command};
})();
