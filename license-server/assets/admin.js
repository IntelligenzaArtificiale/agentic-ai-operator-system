document.addEventListener('click', async (event) => {
  const open = event.target.closest('[data-dialog]');
  if (open) document.getElementById(open.dataset.dialog)?.showModal();
  if (event.target.closest('[data-close]')) event.target.closest('dialog')?.close();
  const copy = event.target.closest('[data-copy]');
  if (copy) {
    await navigator.clipboard.writeText(document.getElementById(copy.dataset.copy)?.textContent || '');
    copy.textContent = 'Copiata';
  }
});
