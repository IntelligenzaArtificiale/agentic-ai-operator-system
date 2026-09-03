<?php declare(strict_types=1); ?>
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Licenze · Agentic AI Operator System</title>
  <link rel="stylesheet" href="assets/admin.css">
</head>
<body>
<main class="shell">
  <header><div><p class="eyebrow">Intelligenza Artificiale Italia</p><h1>Licenze AI Operator</h1></div>
  <?php if ($authenticated): ?><form method="post"><input type="hidden" name="csrf" value="<?= htmlspecialchars($_SESSION['csrf']) ?>"><button class="quiet" name="action" value="logout">Esci</button></form><?php endif; ?></header>
  <?php if ($message): ?><p class="notice success"><?= htmlspecialchars($message) ?></p><?php endif; ?>
  <?php if ($error): ?><p class="notice error"><?= htmlspecialchars($error) ?></p><?php endif; ?>
  <?php if (!$authenticated): ?>
    <section class="login"><h2>Accesso amministratore</h2><form method="post"><input type="hidden" name="csrf" value="<?= htmlspecialchars($_SESSION['csrf']) ?>"><input type="hidden" name="action" value="login"><label>Password<input type="password" name="password" required autofocus></label><button>Accedi</button></form></section>
  <?php else: ?>
    <?php if ($newKey): ?><section class="key"><span>Nuova chiave</span><code id="new-key"><?= htmlspecialchars($newKey) ?></code><button type="button" data-copy="new-key">Copia</button></section><?php endif; ?>
    <section class="toolbar"><form method="get"><input name="q" value="<?= htmlspecialchars($search) ?>" placeholder="Cerca nome, email, telefono o prefisso"><button>Cerca</button></form><button type="button" data-dialog="create-license">+ Nuova licenza</button></section>
    <section class="grid">
    <?php foreach ($licenses['items'] as $license): $expired = strtotime($license['expires_at']) <= time(); ?>
      <article class="card"><div class="card-head"><div><span class="status <?= htmlspecialchars($expired ? 'expired' : $license['status']) ?>"><?= htmlspecialchars($expired ? 'scaduta' : $license['status']) ?></span><h2><?= htmlspecialchars($license['customer']['name']) ?></h2></div><strong><?= htmlspecialchars($license['key_prefix']) ?>…</strong></div>
        <dl><div><dt>Email</dt><dd><?= htmlspecialchars($license['customer']['email']) ?></dd></div><div><dt>Telefono</dt><dd><?= htmlspecialchars($license['customer']['phone']) ?></dd></div><div><dt>Scadenza</dt><dd><?= htmlspecialchars($license['expires_at']) ?></dd></div><div><dt>Dispositivi</dt><dd><?= count(array_filter($license['devices'], static fn($d) => empty($d['revoked_at']))) ?>/<?= (int) $license['device_limit'] ?></dd></div></dl>
        <details><summary>Gestisci</summary><form method="post" class="manage"><input type="hidden" name="csrf" value="<?= htmlspecialchars($_SESSION['csrf']) ?>"><input type="hidden" name="action" value="update"><input type="hidden" name="license_id" value="<?= htmlspecialchars($license['license_id']) ?>"><label>Stato<select name="status"><?php foreach (['active','suspended','revoked'] as $status): ?><option <?= $license['status'] === $status ? 'selected' : '' ?>><?= $status ?></option><?php endforeach; ?></select></label><label>Scadenza<input type="datetime-local" name="expires_at" value="<?= htmlspecialchars((new DateTimeImmutable($license['expires_at']))->setTimezone(new DateTimeZone((string) $config->get('admin_timezone')))->format('Y-m-d\TH:i')) ?>" required></label><label>Limite<input type="number" name="device_limit" min="1" max="20" value="<?= (int) $license['device_limit'] ?>"></label><button>Salva</button></form>
        <?php foreach ($license['devices'] as $device): ?><div class="device"><span><?= htmlspecialchars($device['device_name']) ?><small><?= htmlspecialchars($device['last_seen_at']) ?></small></span><?php if (empty($device['revoked_at'])): ?><form method="post"><input type="hidden" name="csrf" value="<?= htmlspecialchars($_SESSION['csrf']) ?>"><input type="hidden" name="action" value="revoke_device"><input type="hidden" name="license_id" value="<?= htmlspecialchars($license['license_id']) ?>"><input type="hidden" name="activation_id" value="<?= htmlspecialchars($device['activation_id']) ?>"><button class="danger">Revoca</button></form><?php else: ?><em>revocato</em><?php endif; ?></div><?php endforeach; ?></details>
      </article>
    <?php endforeach; ?>
    <?php if (!$licenses['items']): ?><p class="empty">Nessuna licenza trovata.</p><?php endif; ?>
    </section>
    <nav class="pages"><?php for ($i=1; $i <= $licenses['pages']; $i++): ?><a class="<?= $i === $licenses['page'] ? 'current' : '' ?>" href="?q=<?= urlencode($search) ?>&page=<?= $i ?>"><?= $i ?></a><?php endfor; ?></nav>
    <dialog id="create-license"><form method="post"><div class="dialog-head"><h2>Nuova licenza</h2><button type="button" data-close>×</button></div><input type="hidden" name="csrf" value="<?= htmlspecialchars($_SESSION['csrf']) ?>"><input type="hidden" name="action" value="create"><label>Nome<input name="name" maxlength="120" required></label><label>Email<input type="email" name="email" required></label><label>Telefono<input name="phone" maxlength="40" required></label><label>Scadenza<input type="datetime-local" name="expires_at" required></label><label>Dispositivi consentiti<input type="number" name="device_limit" min="1" max="20" value="1" required></label><button>Crea licenza</button></form></dialog>
  <?php endif; ?>
</main><script src="assets/admin.js" defer></script>
</body></html>
