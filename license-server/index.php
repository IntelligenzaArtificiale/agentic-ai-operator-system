<?php
declare(strict_types=1);

use AIOS\Licensing\Security;

require __DIR__ . '/src/bootstrap.php';

$config = licenseConfig();
Security::requireHttps($config);
Security::startAdminSession($config);
$message = null;
$error = null;

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    try {
        Security::requireCsrf();
        $action = (string) ($_POST['action'] ?? '');
        if ($action === 'login') {
            licenseService()->enforceRateLimit('admin-login:' . Security::clientIp($config), 10, 900);
            if (!password_verify((string) ($_POST['password'] ?? ''), (string) $config->get('admin_password_hash'))) {
                throw new RuntimeException('Password non valida.');
            }
            session_regenerate_id(true);
            $_SESSION['authenticated'] = true;
        } elseif ($action === 'logout') {
            $_SESSION = [];
            session_destroy();
            header('Location: index.php');
            exit;
        } elseif (!($_SESSION['authenticated'] ?? false)) {
            throw new RuntimeException('Autenticazione richiesta.');
        } elseif ($action === 'create') {
            $created = licenseService()->createLicense($_POST, 'admin');
            $_SESSION['license_key_context'] = ['license_id' => $created['license']['license_id'], 'license_key' => $created['license_key'], 'customer_name' => $created['license']['customer']['name']];
            $message = 'Licenza creata.';
        } elseif ($action === 'update') {
            licenseService()->updateLicense((string) $_POST['license_id'], $_POST, 'admin');
            $message = 'Licenza aggiornata.';
        } elseif ($action === 'revoke_device') {
            licenseService()->revokeDevice((string) $_POST['license_id'], (string) $_POST['activation_id'], 'admin');
            $message = 'Dispositivo revocato.';
        } elseif ($action === 'reveal_key') {
            $_SESSION['license_key_context'] = licenseService()->revealLicenseKey((string) $_POST['license_id']);
            $message = 'Chiave decifrata in sicurezza.';
        } elseif ($action === 'regenerate_key') {
            $_SESSION['license_key_context'] = licenseService()->regenerateLicenseKey((string) $_POST['license_id'], 'admin');
            $message = 'Nuova chiave generata. La precedente e tutti i dispositivi associati sono stati invalidati.';
        } elseif ($action === 'delete_license') {
            licenseService()->deleteLicense((string) $_POST['license_id'], (string) ($_POST['confirmation'] ?? ''), 'admin');
            unset($_SESSION['license_key_context']);
            $message = 'Licenza, dispositivi e storico associato eliminati definitivamente.';
        }
    } catch (Throwable $exception) {
        $error = $exception->getMessage();
    }
}

$authenticated = (bool) ($_SESSION['authenticated'] ?? false);
$search = trim((string) ($_GET['q'] ?? ''));
$page = max(1, (int) ($_GET['page'] ?? 1));
$licenses = $authenticated ? licenseService()->listLicenses($search, $page) : null;
$keyContext = $_SESSION['license_key_context'] ?? null;
unset($_SESSION['license_key_context']);
require __DIR__ . '/templates/admin.php';
