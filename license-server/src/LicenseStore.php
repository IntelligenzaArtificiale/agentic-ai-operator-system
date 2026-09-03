<?php
declare(strict_types=1);

namespace AIOS\Licensing;

final class LicenseStore
{
    private $dataFile;

    public function __construct(string $dataFile)
    {
        $this->dataFile = $dataFile;
        $directory = dirname($dataFile);
        if (!is_dir($directory) && !mkdir($directory, 0700, true) && !is_dir($directory)) {
            throw new \RuntimeException('Cannot create license data directory.');
        }
    }

    public function read(): array
    {
        return $this->withLock(LOCK_SH, fn (): array => $this->readUnlocked());
    }

    public function transact(callable $callback)
    {
        return $this->withLock(LOCK_EX, function () use ($callback) {
            $state = $this->readUnlocked();
            $result = $callback($state);
            $state['revision'] = ((int) ($state['revision'] ?? 0)) + 1;
            $this->writeUnlocked($state);
            return $result;
        });
    }

    private function withLock(int $mode, callable $callback)
    {
        $lock = fopen($this->dataFile . '.lock', 'c+');
        if ($lock === false || !flock($lock, $mode)) {
            throw new \RuntimeException('Cannot lock license data.');
        }
        try {
            return $callback();
        } finally {
            flock($lock, LOCK_UN);
            fclose($lock);
        }
    }

    private function readUnlocked(): array
    {
        if (!is_file($this->dataFile)) {
            return $this->emptyState();
        }
        $raw = file_get_contents($this->dataFile);
        $value = $raw === false ? null : json_decode($raw, true);
        if (!is_array($value) || ($value['schema_version'] ?? null) !== 1) {
            throw new \RuntimeException('Invalid license data file.');
        }
        $value['licenses'] = is_array($value['licenses'] ?? null) ? $value['licenses'] : [];
        $value['rate_limits'] = is_array($value['rate_limits'] ?? null) ? $value['rate_limits'] : [];
        $value['audit'] = is_array($value['audit'] ?? null) ? $value['audit'] : [];
        return $value;
    }

    private function writeUnlocked(array $state): void
    {
        $encoded = json_encode($state, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
        $temporary = $this->dataFile . '.' . bin2hex(random_bytes(6)) . '.tmp';
        if (file_put_contents($temporary, $encoded . PHP_EOL, LOCK_EX) === false) {
            throw new \RuntimeException('Cannot write license data.');
        }
        chmod($temporary, 0600);
        if (!rename($temporary, $this->dataFile)) {
            @unlink($temporary);
            throw new \RuntimeException('Cannot commit license data.');
        }
    }

    private function emptyState(): array
    {
        return [
            'schema_version' => 1,
            'revision' => 0,
            'licenses' => [],
            'rate_limits' => [],
            'audit' => [],
        ];
    }
}
