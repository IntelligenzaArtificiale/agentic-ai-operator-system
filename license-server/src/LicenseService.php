<?php
declare(strict_types=1);

namespace AIOS\Licensing;

final class LicenseService
{
    private const KEY_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    private $config;
    private $store;

    public function __construct(Config $config, LicenseStore $store)
    {
        $this->config = $config;
        $this->store = $store;
    }

    public function createLicense(array $input, string $actor): array
    {
        $name = $this->requiredText($input, 'name', 120);
        $email = filter_var(trim((string) ($input['email'] ?? '')), FILTER_VALIDATE_EMAIL);
        if ($email === false) {
            throw new \InvalidArgumentException('Email non valida.');
        }
        $phone = $this->requiredText($input, 'phone', 40);
        $deviceLimit = $this->boundedInt($input['device_limit'] ?? 1, 1, 20, 'Limite dispositivi');
        $expiresAt = $this->adminDateToUtc((string) ($input['expires_at'] ?? ''));
        if ($expiresAt <= Security::now()) {
            throw new \InvalidArgumentException('La scadenza deve essere futura.');
        }

        $key = $this->generateLicenseKey();
        $licenseId = bin2hex(random_bytes(16));
        $now = Security::iso(Security::now());
        $license = [
            'license_id' => $licenseId,
            'key_prefix' => substr($key, 0, 10),
            'key_hash' => Security::secretHash(Security::normalizeLicenseKey($key), $this->config->licensePepper()),
            'customer' => ['name' => $name, 'email' => $email, 'phone' => $phone],
            'status' => 'active',
            'expires_at' => Security::iso($expiresAt),
            'device_limit' => $deviceLimit,
            'devices' => [],
            'created_at' => $now,
            'updated_at' => $now,
        ];
        $this->store->transact(function (array &$state) use ($licenseId, $license, $actor): void {
            $state['licenses'][$licenseId] = $license;
            $this->audit($state, 'license_created', $actor, $licenseId);
        });
        return ['license' => $license, 'license_key' => $key];
    }

    public function updateLicense(string $licenseId, array $input, string $actor): void
    {
        $status = (string) ($input['status'] ?? '');
        if (!in_array($status, ['active', 'suspended', 'revoked'], true)) {
            throw new \InvalidArgumentException('Stato licenza non valido.');
        }
        $expiresAt = $this->adminDateToUtc((string) ($input['expires_at'] ?? ''));
        $deviceLimit = $this->boundedInt($input['device_limit'] ?? 1, 1, 20, 'Limite dispositivi');
        $this->store->transact(function (array &$state) use ($licenseId, $status, $expiresAt, $deviceLimit, $actor): void {
            $license = &$this->requireLicense($state, $licenseId);
            $license['status'] = $status;
            $license['expires_at'] = Security::iso($expiresAt);
            $license['device_limit'] = $deviceLimit;
            $license['updated_at'] = Security::iso(Security::now());
            $this->audit($state, 'license_updated', $actor, $licenseId, ['status' => $status]);
        });
    }

    public function revokeDevice(string $licenseId, string $activationId, string $actor): void
    {
        $this->store->transact(function (array &$state) use ($licenseId, $activationId, $actor): void {
            $license = &$this->requireLicense($state, $licenseId);
            if (!isset($license['devices'][$activationId])) {
                throw new \InvalidArgumentException('Dispositivo non trovato.');
            }
            $license['devices'][$activationId]['revoked_at'] = Security::iso(Security::now());
            $license['devices'][$activationId]['token_hash'] = null;
            $license['updated_at'] = Security::iso(Security::now());
            $this->audit($state, 'device_revoked', $actor, $licenseId, ['activation_id' => $activationId]);
        });
    }

    public function listLicenses(string $search, int $page, int $pageSize = 12): array
    {
        $state = $this->store->read();
        $needle = $this->lower(trim($search));
        $items = array_values($state['licenses']);
        if ($needle !== '') {
            $items = array_values(array_filter($items, function (array $license) use ($needle): bool {
                $customer = $license['customer'] ?? [];
                $haystack = implode(' ', [
                    $license['license_id'] ?? '', $license['key_prefix'] ?? '',
                    $customer['name'] ?? '', $customer['email'] ?? '', $customer['phone'] ?? '',
                ]);
                return strpos($this->lower($haystack), $needle) !== false;
            }));
        }
        usort($items, static fn (array $a, array $b): int => strcmp((string) ($b['created_at'] ?? ''), (string) ($a['created_at'] ?? '')));
        $total = count($items);
        $pages = max(1, (int) ceil($total / $pageSize));
        $page = max(1, min($page, $pages));
        return [
            'items' => array_slice($items, ($page - 1) * $pageSize, $pageSize),
            'total' => $total,
            'page' => $page,
            'pages' => $pages,
            'page_size' => $pageSize,
        ];
    }

    public function activate(array $input, string $ip): array
    {
        $normalizedKey = Security::normalizeLicenseKey((string) ($input['license_key'] ?? ''));
        $deviceHash = $this->deviceHash($input['device_id'] ?? '');
        $deviceName = $this->cleanText((string) ($input['device_name'] ?? 'Windows device'), 120);
        $clientVersion = $this->cleanText((string) ($input['client_version'] ?? ''), 32);
        if (strlen($normalizedKey) < 24) {
            throw new LicenseDenied('Licenza non valida.', 401);
        }
        $keyHash = Security::secretHash($normalizedKey, $this->config->licensePepper());

        return $this->store->transact(function (array &$state) use ($keyHash, $deviceHash, $deviceName, $clientVersion, $ip): array {
            $licenseId = $this->findLicenseByKeyHash($state, $keyHash);
            if ($licenseId === null) {
                $this->audit($state, 'activation_denied', $ip, null);
                throw new LicenseDenied('Licenza non valida.', 401);
            }
            $license = &$state['licenses'][$licenseId];
            $this->assertLicenseActive($license);
            $activationId = $this->findDeviceByHash($license, $deviceHash);
            if ($activationId === null) {
                if ($this->activeDeviceCount($license) >= (int) $license['device_limit']) {
                    throw new LicenseDenied('Limite dispositivi raggiunto.', 409);
                }
                $activationId = bin2hex(random_bytes(16));
            }
            $token = Security::base64UrlEncode(random_bytes(32));
            $now = Security::iso(Security::now());
            $license['devices'][$activationId] = [
                'activation_id' => $activationId,
                'device_hash' => $deviceHash,
                'device_name' => $deviceName,
                'token_hash' => Security::secretHash($token, $this->config->licensePepper()),
                'client_version' => $clientVersion,
                'activated_at' => $license['devices'][$activationId]['activated_at'] ?? $now,
                'last_seen_at' => $now,
                'last_ip_hash' => hash('sha256', $ip),
                'revoked_at' => null,
            ];
            $license['updated_at'] = $now;
            $this->audit($state, 'device_activated', $ip, $licenseId, ['activation_id' => $activationId]);
            return ['activation_token' => $token] + $this->signedLease($license, $license['devices'][$activationId]);
        });
    }

    public function validate(array $input, string $ip): array
    {
        $token = (string) ($input['activation_token'] ?? '');
        $deviceHash = $this->deviceHash($input['device_id'] ?? '');
        if (strlen($token) < 32) {
            throw new LicenseDenied('Attivazione richiesta.', 401);
        }
        $tokenHash = Security::secretHash($token, $this->config->licensePepper());
        return $this->store->transact(function (array &$state) use ($tokenHash, $deviceHash, $ip): array {
            [$licenseId, $activationId] = $this->findActivation($state, $tokenHash, $deviceHash);
            if ($licenseId === null || $activationId === null) {
                throw new LicenseDenied('Attivazione richiesta.', 401);
            }
            $license = &$state['licenses'][$licenseId];
            $this->assertLicenseActive($license);
            $device = &$license['devices'][$activationId];
            if (!empty($device['revoked_at'])) {
                throw new LicenseDenied('Dispositivo revocato.', 403);
            }
            $device['last_seen_at'] = Security::iso(Security::now());
            $device['last_ip_hash'] = hash('sha256', $ip);
            return $this->signedLease($license, $device);
        });
    }

    public function deactivate(array $input, string $ip): void
    {
        $tokenHash = Security::secretHash((string) ($input['activation_token'] ?? ''), $this->config->licensePepper());
        $deviceHash = $this->deviceHash($input['device_id'] ?? '');
        $this->store->transact(function (array &$state) use ($tokenHash, $deviceHash, $ip): void {
            [$licenseId, $activationId] = $this->findActivation($state, $tokenHash, $deviceHash);
            if ($licenseId === null || $activationId === null) {
                return;
            }
            $state['licenses'][$licenseId]['devices'][$activationId]['revoked_at'] = Security::iso(Security::now());
            $state['licenses'][$licenseId]['devices'][$activationId]['token_hash'] = null;
            $this->audit($state, 'device_deactivated', $ip, $licenseId, ['activation_id' => $activationId]);
        });
    }

    public function enforceRateLimit(string $bucket, int $limit, int $windowSeconds): void
    {
        $allowed = $this->store->transact(function (array &$state) use ($bucket, $limit, $windowSeconds): bool {
            $now = time();
            foreach ($state['rate_limits'] as $key => $entry) {
                if (($entry['window_started'] ?? 0) < $now - ($windowSeconds * 2)) {
                    unset($state['rate_limits'][$key]);
                }
            }
            $key = hash('sha256', $bucket);
            $entry = $state['rate_limits'][$key] ?? ['window_started' => $now, 'count' => 0];
            if ($entry['window_started'] <= $now - $windowSeconds) {
                $entry = ['window_started' => $now, 'count' => 0];
            }
            $entry['count']++;
            $state['rate_limits'][$key] = $entry;
            return $entry['count'] <= $limit;
        });
        if (!$allowed) {
            throw new LicenseDenied('Troppi tentativi. Riprova più tardi.', 429);
        }
    }

    private function signedLease(array $license, array $device): array
    {
        $now = Security::now();
        $licenseExpiry = Security::parseDate((string) $license['expires_at']);
        $validUntil = min($licenseExpiry->getTimestamp(), $now->getTimestamp() + (int) $this->config->get('lease_seconds', 86400));
        $refreshAfter = min($validUntil, $now->getTimestamp() + (int) $this->config->get('refresh_after_seconds', 300));
        $payload = [
            'schema_version' => 1,
            'product' => (string) $this->config->get('product'),
            'license_id' => $license['license_id'],
            'activation_id' => $device['activation_id'],
            'device_hash' => $device['device_hash'],
            'status' => 'active',
            'issued_at' => Security::iso($now),
            'refresh_after' => Security::iso((new \DateTimeImmutable('@' . $refreshAfter))->setTimezone(new \DateTimeZone('UTC'))),
            'valid_until' => Security::iso((new \DateTimeImmutable('@' . $validUntil))->setTimezone(new \DateTimeZone('UTC'))),
        ];
        $json = json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
        return [
            'lease' => Security::base64UrlEncode($json),
            'signature' => Security::base64UrlEncode(sodium_crypto_sign_detached($json, $this->config->signingSecretKey())),
        ];
    }

    private function assertLicenseActive(array $license): void
    {
        if (($license['status'] ?? '') !== 'active') {
            throw new LicenseDenied('Licenza sospesa o revocata.', 403);
        }
        if (Security::parseDate((string) $license['expires_at']) <= Security::now()) {
            throw new LicenseDenied('Licenza scaduta.', 403);
        }
    }

    private function findLicenseByKeyHash(array $state, string $keyHash): ?string
    {
        foreach ($state['licenses'] as $licenseId => $license) {
            if (hash_equals((string) ($license['key_hash'] ?? ''), $keyHash)) {
                return (string) $licenseId;
            }
        }
        return null;
    }

    private function findDeviceByHash(array $license, string $deviceHash): ?string
    {
        foreach ($license['devices'] ?? [] as $activationId => $device) {
            if (($device['device_hash'] ?? '') === $deviceHash && empty($device['revoked_at'])) {
                return (string) $activationId;
            }
        }
        return null;
    }

    private function findActivation(array $state, string $tokenHash, string $deviceHash): array
    {
        foreach ($state['licenses'] as $licenseId => $license) {
            foreach ($license['devices'] ?? [] as $activationId => $device) {
                if (($device['device_hash'] ?? '') === $deviceHash && is_string($device['token_hash'] ?? null)
                    && hash_equals($device['token_hash'], $tokenHash)) {
                    return [(string) $licenseId, (string) $activationId];
                }
            }
        }
        return [null, null];
    }

    private function activeDeviceCount(array $license): int
    {
        return count(array_filter($license['devices'] ?? [], static fn (array $device): bool => empty($device['revoked_at'])));
    }

    private function &requireLicense(array &$state, string $licenseId): array
    {
        if (!isset($state['licenses'][$licenseId])) {
            throw new \InvalidArgumentException('Licenza non trovata.');
        }
        return $state['licenses'][$licenseId];
    }

    private function generateLicenseKey(): string
    {
        $characters = '';
        for ($index = 0; $index < 25; $index++) {
            $characters .= self::KEY_ALPHABET[random_int(0, strlen(self::KEY_ALPHABET) - 1)];
        }
        return 'AIOS-' . implode('-', str_split($characters, 5));
    }

    private function deviceHash($value): string
    {
        $deviceHash = strtolower(trim((string) $value));
        if (!preg_match('/^[a-f0-9]{64}$/', $deviceHash)) {
            throw new LicenseDenied('Identificativo dispositivo non valido.', 400);
        }
        return $deviceHash;
    }

    private function adminDateToUtc(string $value): \DateTimeImmutable
    {
        $timezone = new \DateTimeZone((string) $this->config->get('admin_timezone', 'Europe/Rome'));
        $date = \DateTimeImmutable::createFromFormat('Y-m-d\TH:i', $value, $timezone);
        if (!$date) {
            throw new \InvalidArgumentException('Scadenza non valida.');
        }
        return $date->setTimezone(new \DateTimeZone('UTC'));
    }

    private function requiredText(array $input, string $key, int $maxLength): string
    {
        $value = $this->cleanText((string) ($input[$key] ?? ''), $maxLength);
        if ($value === '') {
            throw new \InvalidArgumentException('Compila tutti i campi obbligatori.');
        }
        return $value;
    }

    private function cleanText(string $value, int $maxLength): string
    {
        $clean = trim(preg_replace('/\s+/', ' ', $value) ?? '');
        return function_exists('mb_substr') ? mb_substr($clean, 0, $maxLength) : substr($clean, 0, $maxLength);
    }

    private function lower(string $value): string
    {
        return function_exists('mb_strtolower') ? mb_strtolower($value) : strtolower($value);
    }

    private function boundedInt($value, int $minimum, int $maximum, string $label): int
    {
        $integer = filter_var($value, FILTER_VALIDATE_INT);
        if ($integer === false || $integer < $minimum || $integer > $maximum) {
            throw new \InvalidArgumentException("{$label} non valido.");
        }
        return $integer;
    }

    private function audit(array &$state, string $event, string $actor, ?string $licenseId, array $details = []): void
    {
        $state['audit'][] = [
            'timestamp' => Security::iso(Security::now()),
            'event' => $event,
            'actor_hash' => hash('sha256', $actor),
            'license_id' => $licenseId,
            'details' => $details,
        ];
        $state['audit'] = array_slice($state['audit'], -1000);
    }
}

final class LicenseDenied extends \RuntimeException
{
    public $statusCode;

    public function __construct(string $message, int $statusCode)
    {
        $this->statusCode = $statusCode;
        parent::__construct($message);
    }
}
