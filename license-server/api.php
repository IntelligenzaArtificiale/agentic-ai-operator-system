<?php
declare(strict_types=1);

use AIOS\Licensing\LicenseDenied;
use AIOS\Licensing\Security;

require __DIR__ . '/src/bootstrap.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function reply(int $status, array $body): void
{
    http_response_code($status);
    echo json_encode($body, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    exit;
}

try {
    $config = licenseConfig();
    Security::requireHttps($config);
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
        reply(405, ['ok' => false, 'error' => 'Metodo non consentito.']);
    }
    $raw = file_get_contents('php://input');
    if ($raw === false || strlen($raw) > 16384) {
        reply(413, ['ok' => false, 'error' => 'Richiesta troppo grande.']);
    }
    $input = json_decode($raw, true, 16, JSON_THROW_ON_ERROR);
    if (!is_array($input)) {
        reply(400, ['ok' => false, 'error' => 'JSON non valido.']);
    }
    $action = (string) ($input['action'] ?? '');
    $ip = Security::clientIp($config);
    $service = licenseService();
    $service->enforceRateLimit("api:{$action}:{$ip}", $action === 'activate' ? 12 : 120, 300);

    if ($action === 'activate') {
        reply(200, ['ok' => true, 'product' => $config->get('product'), 'signing_public_key' => $config->signingPublicKey()] + $service->activate($input, $ip));
    }
    if ($action === 'validate') {
        reply(200, ['ok' => true] + $service->validate($input, $ip));
    }
    if ($action === 'deactivate') {
        $service->deactivate($input, $ip);
        reply(200, ['ok' => true]);
    }
    reply(400, ['ok' => false, 'error' => 'Azione non valida.']);
} catch (LicenseDenied $error) {
    reply($error->statusCode, ['ok' => false, 'error' => $error->getMessage()]);
} catch (JsonException|InvalidArgumentException $error) {
    reply(400, ['ok' => false, 'error' => $error->getMessage()]);
} catch (Throwable $error) {
    error_log('AIOS licensing API: ' . $error->getMessage());
    reply(500, ['ok' => false, 'error' => 'Errore temporaneo del servizio licenze.']);
}
