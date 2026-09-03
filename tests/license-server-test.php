<?php
declare(strict_types=1);

require __DIR__ . '/../license-server/src/Security.php';
require __DIR__ . '/../license-server/src/Config.php';
require __DIR__ . '/../license-server/src/LicenseStore.php';
require __DIR__ . '/../license-server/src/LicenseService.php';

use AIOS\Licensing\Config;
use AIOS\Licensing\LicenseDenied;
use AIOS\Licensing\LicenseService;
use AIOS\Licensing\LicenseStore;

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$temporary = sys_get_temp_dir() . '/aios-license-' . bin2hex(random_bytes(6));
mkdir($temporary, 0700, true);
$pair = sodium_crypto_sign_keypair();
$config = new Config([
    'product' => 'Agentic AI Operator System',
    'admin_password_hash' => password_hash('unused-password', PASSWORD_DEFAULT),
    'license_pepper' => base64_encode(random_bytes(32)),
    'signing_secret_key' => base64_encode(sodium_crypto_sign_secretkey($pair)),
    'data_file' => $temporary . '/license.json',
    'lease_seconds' => 3600,
    'refresh_after_seconds' => 60,
    'admin_timezone' => 'UTC',
]);
$store = new LicenseStore((string) $config->get('data_file'));
$service = new LicenseService($config, $store);
$future = (new DateTimeImmutable('+2 days', new DateTimeZone('UTC')))->format('Y-m-d\TH:i');
$created = $service->createLicense(['name' => 'Test', 'email' => 'test@example.com', 'phone' => '+39000', 'device_limit' => 1, 'expires_at' => $future], 'test');
check(!str_contains(file_get_contents($temporary . '/license.json'), $created['license_key']), 'Plaintext key persisted');

$deviceOne = str_repeat('a', 64);
$activation = $service->activate(['license_key' => $created['license_key'], 'device_id' => $deviceOne, 'device_name' => 'PC 1', 'client_version' => '2.5.0'], '127.0.0.1');
check(isset($activation['activation_token'], $activation['lease'], $activation['signature']), 'Activation response incomplete');
$validated = $service->validate(['activation_token' => $activation['activation_token'], 'device_id' => $deviceOne], '127.0.0.1');
check(isset($validated['lease']), 'Validation failed');

try {
    $service->activate(['license_key' => $created['license_key'], 'device_id' => str_repeat('b', 64)], '127.0.0.2');
    throw new RuntimeException('Device limit was not enforced');
} catch (LicenseDenied $error) {
    check($error->statusCode === 409, 'Wrong device-limit status');
}

$state = $store->read();
$licenseId = $created['license']['license_id'];
$activationId = array_key_first($state['licenses'][$licenseId]['devices']);
$service->revokeDevice($licenseId, $activationId, 'test');
try {
    $service->validate(['activation_token' => $activation['activation_token'], 'device_id' => $deviceOne], '127.0.0.1');
    throw new RuntimeException('Revoked activation was accepted');
} catch (LicenseDenied $error) {
    check($error->statusCode === 401, 'Wrong revoked-token status');
}

$service->updateLicense($licenseId, ['status' => 'revoked', 'device_limit' => 1, 'expires_at' => $future], 'test');
try {
    $service->activate(['license_key' => $created['license_key'], 'device_id' => $deviceOne], '127.0.0.1');
    throw new RuntimeException('Revoked license was accepted');
} catch (LicenseDenied $error) {
    check($error->statusCode === 403, 'Wrong revoked-license status');
}

$expired = $service->createLicense(['name' => 'Expired', 'email' => 'expired@example.com', 'phone' => '+39111', 'device_limit' => 1, 'expires_at' => $future], 'test');
$store->transact(function (array &$state) use ($expired): void {
    $state['licenses'][$expired['license']['license_id']]['expires_at'] = '2000-01-01T00:00:00Z';
});
try {
    $service->activate(['license_key' => $expired['license_key'], 'device_id' => $deviceOne], '127.0.0.1');
    throw new RuntimeException('Expired license was accepted');
} catch (LicenseDenied $error) {
    check($error->statusCode === 403, 'Wrong expired-license status');
}

for ($attempt = 0; $attempt < 3; $attempt++) {
    try {
        $service->enforceRateLimit('test-bucket', 2, 60);
        check($attempt < 2, 'Rate limit was not enforced');
    } catch (LicenseDenied $error) {
        check($attempt === 2 && $error->statusCode === 429, 'Rate limit failed');
    }
}

echo "license-server tests passed\n";
