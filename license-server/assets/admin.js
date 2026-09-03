// Handles the few progressive interactions; all forms remain server-rendered.
document.addEventListener('click', async (event) => {
  const open = event.target.closest('[data-dialog]');
  if (open) {
    const dialog = document.getElementById(open.dataset.dialog);
    dialog?.showModal();
    dialog?.querySelector('input:not([type="hidden"])')?.focus();
  }
  const close = event.target.closest('[data-close]');
  if (close) close.closest('dialog')?.close();
  const copy = event.target.closest('[data-copy]');
  if (copy) {
    try {
      await navigator.clipboard.writeText(document.getElementById(copy.dataset.copy)?.textContent || '');
      copy.textContent = 'Copiata';
      copy.dataset.state = 'success';
    } catch (_error) {
      copy.textContent = 'Copia non riuscita';
      copy.dataset.state = 'error';
    }
  }
});

document.querySelectorAll('dialog').forEach((dialog) => {
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
});
