<?php
declare(strict_types=1);

$configPath = __DIR__ . '/private/config.php';
$dataPath = __DIR__ . '/private/license.json';
$tokenPath = __DIR__ . '/private/setup-token.txt';
$provisioningPath = __DIR__ . '/private/provisioning.php';
$error = null;
$completed = false;

if (is_file($configPath)) {
    http_response_code(404);
    exit('Setup already completed. Delete setup.php from the server.');
}
if (!is_file($tokenPath) || !is_file($provisioningPath)) {
    http_response_code(404);
    exit('Setup token missing.');
}
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    try {
        if (($_SERVER['HTTPS'] ?? '') !== 'on' && ($_SERVER['SERVER_PORT'] ?? '') !== '443') {
            throw new RuntimeException('HTTPS è obbligatorio.');
        }
        if (!extension_loaded('sodium')) {
            throw new RuntimeException('L’estensione PHP sodium non è disponibile.');
        }
        $expectedToken = trim((string) file_get_contents($tokenPath));
        $providedToken = trim((string) ($_POST['setup_token'] ?? ''));
        if (strlen($expectedToken) < 32 || !hash_equals($expectedToken, $providedToken)) {
            throw new RuntimeException('Token di setup non valido.');
        }
        $password = (string) ($_POST['password'] ?? '');
        if (strlen($password) < 14) {
            throw new RuntimeException('Usa una password di almeno 14 caratteri.');
        }
        $provisioning = require $provisioningPath;
        if (!is_array($provisioning) || !isset($provisioning['license_pepper'], $provisioning['signing_secret_key'])) {
            throw new RuntimeException('Provisioning non valido.');
        }
        $values = [
            'product' => 'Agentic AI Operator System',
            'admin_password_hash' => password_hash($password, PASSWORD_DEFAULT),
            'license_pepper' => $provisioning['license_pepper'],
            'signing_secret_key' => $provisioning['signing_secret_key'],
            'data_file' => $dataPath,
            'lease_seconds' => 86400,
            'refresh_after_seconds' => 300,
            'admin_timezone' => 'Europe/Rome',
            'allow_insecure_local' => false,
            'trusted_proxy' => false,
        ];
        $php = "<?php\ndeclare(strict_types=1);\n\nreturn " . var_export($values, true) . ";\n";
        if (!is_file($dataPath)) {
            if (file_put_contents($dataPath, json_encode(['schema_version' => 1, 'revision' => 0, 'licenses' => new stdClass(), 'rate_limits' => new stdClass(), 'audit' => []], JSON_PRETTY_PRINT) . PHP_EOL, LOCK_EX) === false) {
                throw new RuntimeException('Impossibile inizializzare private/license.json.');
            }
            chmod($dataPath, 0600);
        }
        if (file_put_contents($configPath, $php, LOCK_EX) === false) {
            throw new RuntimeException('Impossibile scrivere private/config.php.');
        }
        chmod($configPath, 0600);
        unlink($tokenPath);
        unlink($provisioningPath);
        $completed = true;
    } catch (Throwable $exception) {
        $error = $exception->getMessage();
    }
}
?>
<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Setup licenze · AIOS</title><link rel="stylesheet" href="assets/admin.css"></head><body><main class="shell auth-shell"><section class="auth-card" aria-labelledby="setup-title"><div class="brand"><span class="brand-mark">AI</span><span>Agentic AI Operator System</span></div><h1 id="setup-title">Configura le licenze</h1><p>Proteggi l’area amministrativa e completa la prima configurazione.</p><?php if ($error): ?><p class="notice error" role="alert"><?= htmlspecialchars($error) ?></p><?php endif; ?><?php if ($completed): ?><p class="notice" role="status">Configurazione completata. Elimina setup.php dal server e apri index.php.</p><a class="button" href="index.php">Apri area amministrativa</a><?php else: ?><form method="post" class="stack"><label class="field">Token monouso<input class="input" type="password" name="setup_token" minlength="32" autocomplete="off" required autofocus></label><label class="field">Nuova password amministratore<input class="input" type="password" name="password" minlength="14" autocomplete="new-password" required></label><button class="button">Completa configurazione</button></form><?php endif; ?></section></main></body></html>
