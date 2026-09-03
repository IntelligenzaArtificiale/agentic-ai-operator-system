<?php
declare(strict_types=1);

return [
    'product' => 'Agentic AI Operator System',
    'admin_password_hash' => 'REPLACE_WITH_PASSWORD_HASH',
    'license_pepper' => 'REPLACE_WITH_BASE64_RANDOM_BYTES',
    'signing_secret_key' => 'REPLACE_WITH_BASE64_ED25519_SECRET_KEY',
    'data_file' => __DIR__ . '/license.json',
    'lease_seconds' => 86400,
    'refresh_after_seconds' => 300,
    'admin_timezone' => 'Europe/Rome',
    'allow_insecure_local' => false,
    'trusted_proxy' => false,
];
