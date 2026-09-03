<?php
declare(strict_types=1);

namespace AIOS\Licensing;

final class Config
{
    private $values;

    public function __construct(array $values)
    {
        $this->values = $values;
        foreach (['product', 'admin_password_hash', 'license_pepper', 'signing_secret_key', 'data_file'] as $key) {
            if (!isset($values[$key]) || !is_string($values[$key]) || trim($values[$key]) === '') {
                throw new \RuntimeException("Missing server configuration: {$key}");
            }
        }
        if (!extension_loaded('sodium')) {
            throw new \RuntimeException('The PHP sodium extension is required.');
        }
        if (strlen($this->signingSecretKey()) !== SODIUM_CRYPTO_SIGN_SECRETKEYBYTES) {
            throw new \RuntimeException('Invalid Ed25519 signing key.');
        }
    }

    public static function load(string $path): self
    {
        if (!is_file($path)) {
            throw new \RuntimeException('License server is not configured.');
        }
        $values = require $path;
        if (!is_array($values)) {
            throw new \RuntimeException('Invalid license server configuration.');
        }
        return new self($values);
    }

    public function get(string $key, $default = null)
    {
        return $this->values[$key] ?? $default;
    }

    public function signingSecretKey(): string
    {
        $decoded = base64_decode((string) $this->values['signing_secret_key'], true);
        return $decoded === false ? '' : $decoded;
    }

    public function signingPublicKey(): string
    {
        return Security::base64UrlEncode(sodium_crypto_sign_publickey_from_secretkey($this->signingSecretKey()));
    }

    public function licensePepper(): string
    {
        $decoded = base64_decode((string) $this->values['license_pepper'], true);
        if ($decoded === false || strlen($decoded) < 32) {
            throw new \RuntimeException('Invalid license pepper.');
        }
        return $decoded;
    }
}
