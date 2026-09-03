<?php
declare(strict_types=1);

namespace AIOS\Licensing;

final class Security
{
    public static function base64UrlEncode(string $value): string
    {
        return rtrim(strtr(base64_encode($value), '+/', '-_'), '=');
    }

    public static function normalizeLicenseKey(string $value): string
    {
        return strtoupper(preg_replace('/[^A-Z0-9]/i', '', trim($value)) ?? '');
    }

    public static function secretHash(string $value, string $pepper): string
    {
        return hash_hmac('sha256', $value, $pepper);
    }

    public static function now(): \DateTimeImmutable
    {
        return new \DateTimeImmutable('now', new \DateTimeZone('UTC'));
    }

    public static function iso(\DateTimeInterface $value): string
    {
        return $value->setTimezone(new \DateTimeZone('UTC'))->format('Y-m-d\TH:i:s\Z');
    }

    public static function parseDate(string $value): \DateTimeImmutable
    {
        try {
            return new \DateTimeImmutable($value, new \DateTimeZone('UTC'));
        } catch (\Exception) {
            throw new \InvalidArgumentException('Invalid date.');
        }
    }

    public static function clientIp(Config $config): string
    {
        if ($config->get('trusted_proxy', false) && isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            return trim(explode(',', (string) $_SERVER['HTTP_X_FORWARDED_FOR'])[0]);
        }
        return (string) ($_SERVER['REMOTE_ADDR'] ?? 'unknown');
    }

    public static function startAdminSession(Config $config): void
    {
        $secure = self::isHttps() || (bool) $config->get('allow_insecure_local', false);
        session_name('aios_license_admin');
        session_set_cookie_params([
            'lifetime' => 0,
            'path' => '/',
            'secure' => $secure && self::isHttps(),
            'httponly' => true,
            'samesite' => 'Strict',
        ]);
        session_start();
        if (!isset($_SESSION['csrf'])) {
            $_SESSION['csrf'] = self::base64UrlEncode(random_bytes(32));
        }
    }

    public static function requireCsrf(): void
    {
        $provided = (string) ($_POST['csrf'] ?? '');
        $expected = (string) ($_SESSION['csrf'] ?? '');
        if ($provided === '' || $expected === '' || !hash_equals($expected, $provided)) {
            throw new \RuntimeException('Sessione scaduta. Ricarica la pagina.');
        }
    }

    public static function requireHttps(Config $config): void
    {
        if (!self::isHttps() && !(bool) $config->get('allow_insecure_local', false)) {
            throw new \RuntimeException('HTTPS is required.');
        }
    }

    public static function isHttps(): bool
    {
        return ($_SERVER['HTTPS'] ?? '') === 'on' || ($_SERVER['SERVER_PORT'] ?? '') === '443';
    }
}
