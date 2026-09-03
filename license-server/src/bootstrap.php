<?php
declare(strict_types=1);

use AIOS\Licensing\Config;
use AIOS\Licensing\LicenseService;
use AIOS\Licensing\LicenseStore;

spl_autoload_register(static function (string $class): void {
    $prefix = 'AIOS\\Licensing\\';
    if (strpos($class, $prefix) === 0) {
        require_once __DIR__ . '/' . substr($class, strlen($prefix)) . '.php';
    }
});

function licenseService(): LicenseService
{
    static $service;
    if (!$service instanceof LicenseService) {
        $config = Config::load(dirname(__DIR__) . '/private/config.php');
        $service = new LicenseService($config, new LicenseStore((string) $config->get('data_file')));
    }
    return $service;
}

function licenseConfig(): Config
{
    static $config;
    return $config ??= Config::load(dirname(__DIR__) . '/private/config.php');
}
