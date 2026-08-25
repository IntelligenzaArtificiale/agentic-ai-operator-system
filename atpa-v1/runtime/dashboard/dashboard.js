(() => {
  const data = window.ATPA_DATA || {system:{},counts:{},procedures:[]};
  const byId = id => document.getElementById(id);
  const escapeHtml = value => String(value || '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const duration = milliseconds => milliseconds == null ? '—' : milliseconds < 1000 ? `${milliseconds} ms` : `${(milliseconds / 1000).toFixed(1)} s`;

  function renderSystem() {
    const labels = {chatgpt:'ChatGPT',codex:'Codex',mcp:'MCP Windows',plugin:'Sistema',recorder:'OpenSteps'};
    byId('system').innerHTML = Object.entries(labels).map(([key,label]) => `<div class="pill ${data.system[key]?'ok':''}"><i class="dot"></i><b>${label}</b><br><span>${data.system[key]?'Operativo':'Non rilevato'}</span></div>`).join('');
    const items = [['Procedure',data.counts.total],['Esecuzioni',data.counts.runs],['Successi verificati',data.counts.successful_runs],['Non verificati',data.counts.unverified_runs],['Errori',data.counts.incidents],['Tempo medio verificato',duration(data.counts.average_duration_ms)]];
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
    byId('grid').innerHTML = procedures.length ? procedures.map(item => `<article class="card" data-slug="${escapeHtml(item.meta.slug)}"><span class="badge">${escapeHtml(item.meta.status)}</span><h3>${escapeHtml(item.meta.name)}</h3><p>${escapeHtml(item.meta.description)}</p><div class="meta"><span>${escapeHtml(item.meta.department||'Senza reparto')}</span><span>v${escapeHtml(item.meta.version)}</span></div><div class="performance"><span>${item.metrics.run_count||0} esecuzioni</span><span>media ${duration(item.metrics.average_duration_ms)}</span><span>${item.metrics.incident_count||0} errori</span></div></article>`).join('') : '<div class="empty">Nessuna procedura corrispondente.</div>';
    document.querySelectorAll('.card').forEach(card => card.addEventListener('click', () => showDetail(card.dataset.slug)));
  }

  function showDetail(slug) {
    const item = data.procedures.find(candidate => candidate.meta.slug === slug);
    const meta = item.meta;
    const nodes = meta.flow?.nodes || [];
    const slow = item.metrics.slowest_steps || [];
    byId('detailBody').innerHTML = `<div class="brand">${escapeHtml(meta.category||'Procedura')}</div><h2>${escapeHtml(meta.name)}</h2><p>${escapeHtml(meta.description)}</p><p><b>Reparto:</b> ${escapeHtml(meta.department||'—')} · <b>Versione:</b> ${escapeHtml(meta.version)}</p><h3>Prestazioni verificate</h3><table class="metric-table"><tr><th>Esecuzioni</th><td>${item.metrics.run_count||0}</td><th>Successi verificati</th><td>${item.metrics.successful_runs||0}</td></tr><tr><th>Non verificati</th><td>${item.metrics.unverified_runs||0}</td><th>Media</th><td>${duration(item.metrics.average_duration_ms)}</td></tr><tr><th>Migliore</th><td>${duration(item.metrics.best_duration_ms)}</td><th>Ultima verificata</th><td>${duration(item.metrics.last_duration_ms)}</td></tr><tr><th>Errori</th><td>${item.metrics.incident_count||0}</td><th></th><td></td></tr></table><h3>Step più lenti</h3><table class="metric-table">${slow.length?slow.map(step=>`<tr><td>${escapeHtml(step.label)}</td><td>${duration(step.average_duration_ms)}</td><td>${step.samples} campioni</td></tr>`).join(''):'<tr><td>Nessun campione verificato disponibile.</td></tr>'}</table><h3>Flusso operativo</h3><div class="flow">${nodes.length?nodes.map(node=>`<div class="node ${node.type==='condition'?'condition':''}"><b>${escapeHtml(node.label)}</b><br><small>${escapeHtml(node.description||'')}</small></div>`).join(''):'<span class="empty">Diagramma non ancora definito.</span>'}</div><p><a href="${item.folder_uri}">Apri cartella procedura</a></p>`;
    byId('detail').showModal();
  }

  const departments = [...new Set(data.procedures.map(item => item.meta.department).filter(Boolean))].sort();
  byId('department').innerHTML += departments.map(value => `<option>${escapeHtml(value)}</option>`).join('');
  ['q','department','status'].forEach(id => byId(id).addEventListener(id === 'q' ? 'input' : 'change', renderCards));
  byId('close-detail').addEventListener('click', () => byId('detail').close());
  renderSystem();
  renderCards();
})();
