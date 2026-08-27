(() => {
  const data = window.ATPA_DATA || {system:{},counts:{},procedures:[]};
  const byId = id => document.getElementById(id);
  const escapeHtml = value => String(value || '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const duration = milliseconds => milliseconds == null ? '—' : milliseconds < 1000 ? `${milliseconds} ms` : `${(milliseconds / 1000).toFixed(1)} s`;

  function renderCompany() {
    const company = data.company || {status:'not_configured'};
    if (company.status !== 'configured') {
      byId('company').innerHTML = '<div class="brand">Profilo azienda</div><h2>Configura il DNA aziendale</h2><p>Avvia <b>$profilo-azienda</b> per contestualizzare procedure, reparti e strumenti.</p>';
      return;
    }
    const identity = company.identity || {};
    const business = company.business || {};
    const operations = company.operations || {};
    const tags = [...(business.sectors||[]), ...(operations.departments||[])].slice(0, 8);
    byId('company').innerHTML = `<div class="brand">Profilo azienda</div><h2>${escapeHtml(identity.display_name||identity.legal_name||'Azienda')}</h2><p>${escapeHtml(business.summary||'DNA aziendale configurato.')}</p><div class="company-data">${tags.map(tag=>`<span>${escapeHtml(tag)}</span>`).join('')}<span>${(company.sources||[]).length} fonti</span></div>`;
  }

  function renderSystem() {
    const labels = {chatgpt:'ChatGPT',codex:'Codex',mcp:'MCP Windows',plugin:'Sistema',recorder:'OpenSteps'};
    byId('system').innerHTML = Object.entries(labels).map(([key,label]) => `<div class="pill ${data.system[key]?'ok':''}"><i class="dot"></i><b>${label}</b><br><span>${data.system[key]?'Operativo':'Non rilevato'}</span></div>`).join('');
    const items = [['Procedure',data.counts.total],['Piani compilati',data.counts.compiled],['Esecuzioni',data.counts.runs],['Interventi IA',data.counts.ai_interventions],['Errori',data.counts.incidents],['Tempo medio verificato',duration(data.counts.average_duration_ms)]];
    byId('stats').innerHTML = items.map(([label,value]) => `<div class="stat"><strong>${value ?? 0}</strong><span>${label}</span></div>`).join('');
  }

  function renderCards() {
    const query = byId('q').value.toLowerCase();
    const department = byId('department').value;
    const status = byId('status').value;
    const procedures = data.procedures.filter(item => {
      const meta = item.meta;
      const haystack = [meta.name,meta.description,meta.department,meta.category,...(meta.roles||[])].join(' ').toLowerCase();
      return (!query || haystack.includes(query)) && (!department || meta.department === department) && (!status || meta.status === status);
    });
    byId('grid').innerHTML = procedures.length ? procedures.map(item => `<article class="card" data-slug="${escapeHtml(item.meta.slug)}"><span class="badge">${escapeHtml(item.meta.status)} · ${escapeHtml(item.plan?.status||'missing')}</span><h3>${escapeHtml(item.meta.name)}</h3><p>${escapeHtml(item.meta.description)}</p><div class="meta"><span>${escapeHtml(item.meta.department||'Senza reparto')}</span><span>v${escapeHtml(item.meta.version)}</span></div><div class="performance"><span>${item.metrics.run_count||0} esecuzioni</span><span>${item.metrics.deterministic_blocks||0} blocchi locali</span><span>${item.metrics.ai_interventions||0} interventi IA</span></div></article>`).join('') : '<div class="empty">Nessuna procedura corrispondente.</div>';
    document.querySelectorAll('.card').forEach(card => card.addEventListener('click', () => showDetail(card.dataset.slug)));
  }

  function showDetail(slug) {
    const item = data.procedures.find(candidate => candidate.meta.slug === slug);
    const meta = item.meta;
    const nodes = meta.flow?.nodes || [];
    const slow = item.metrics.slowest_steps || [];
    byId('detailBody').innerHTML = `<div class="brand">${escapeHtml(meta.category||'Procedura')}</div><h2>${escapeHtml(meta.name)}</h2><p>${escapeHtml(meta.description)}</p><p><b>Reparto:</b> ${escapeHtml(meta.department||'—')} · <b>Versione:</b> ${escapeHtml(meta.version)} · <b>Piano:</b> ${escapeHtml(item.plan?.status||'missing')} (${item.plan?.blocks||0} blocchi)</p><h3>Prestazioni verificate</h3><table class="metric-table"><tr><th>Esecuzioni</th><td>${item.metrics.run_count||0}</td><th>Successi verificati</th><td>${item.metrics.successful_runs||0}</td></tr><tr><th>Interventi IA</th><td>${item.metrics.ai_interventions||0}</td><th>Blocchi locali</th><td>${item.metrics.deterministic_blocks||0}</td></tr><tr><th>Migliore</th><td>${duration(item.metrics.best_duration_ms)}</td><th>Ultima verificata</th><td>${duration(item.metrics.last_duration_ms)}</td></tr><tr><th>Errori</th><td>${item.metrics.incident_count||0}</td><th>Media</th><td>${duration(item.metrics.average_duration_ms)}</td></tr></table><h3>Step più lenti</h3><table class="metric-table">${slow.length?slow.map(step=>`<tr><td>${escapeHtml(step.label)}</td><td>${duration(step.average_duration_ms)}</td><td>${step.samples} campioni</td></tr>`).join(''):'<tr><td>Nessun campione verificato disponibile.</td></tr>'}</table><h3>Flusso operativo</h3><div class="flow">${nodes.length?nodes.map(node=>`<div class="node ${node.type==='condition'?'condition':''}"><b>${escapeHtml(node.label)}</b><br><small>${escapeHtml(node.description||'')}</small></div>`).join(''):'<span class="empty">Diagramma non ancora definito.</span>'}</div><p><a href="${item.folder_uri}">Apri cartella procedura</a></p>`;
    byId('detail').showModal();
  }

  const departments = [...new Set(data.procedures.map(item => item.meta.department).filter(Boolean))].sort();
  byId('department').innerHTML += departments.map(value => `<option>${escapeHtml(value)}</option>`).join('');
  ['q','department','status'].forEach(id => byId(id).addEventListener(id === 'q' ? 'input' : 'change', renderCards));
  byId('close-detail').addEventListener('click', () => byId('detail').close());
  renderCompany();
  renderSystem();
  renderCards();
})();
