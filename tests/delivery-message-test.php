<?php
declare(strict_types=1);
require __DIR__ . '/../license-server/src/DeliveryMessage.php';
$text = \AIOS\Licensing\DeliveryMessage::forCustomer('Cliente test', 'AIOS-TEST-SECRET');
$parts = explode('COPIA IN CHAT SOLO IL PROMPT QUI SOTTO, SENZA LA CHIAVE:', $text);
if (count($parts) !== 2 || strpos($parts[1], 'AIOS-TEST-SECRET') !== false
    || strpos($parts[1], 'GUIDA-UTENTE.md') === false
    || strpos($parts[1], 'INSTALL_FOR_CHATGPT.md') !== false
    || strpos($parts[1], 'Attendi la mia risposta') === false) {
    throw new RuntimeException('Delivery message does not separate private key and prompt.');
}
echo "Delivery message test passed\n";
