<?php
declare(strict_types=1);

namespace AIOS\Licensing;

final class DeliveryMessage
{
    public static function forCustomer(string $name, string $key): string
    {
        return "Ciao " . $name . ",\n\n"
            . "La tua chiave personale (NON incollarla in chat):\n" . $key . "\n\n"
            . "Conserva la chiave: la inserirai tu nella finestra di attivazione sul Desktop.\n\n"
            . "COPIA IN CHAT SOLO IL PROMPT QUI SOTTO, SENZA LA CHIAVE:\n\n"
            . "Installa Agentic AI Operator System per Windows dalla release ufficiale "
            . "https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system/releases/latest . "
            . "Scarica lo ZIP Windows, estrailo e leggi AGENTS.md e GUIDA-UTENTE.md. "
            . "Esegui Install-System.ps1 -NonInteractive e verifica INSTALL_RESULT.json e le registrazioni MCP/plugin. "
            . "Non usare Computer Use per installare, non chiedere la chiave in chat e non aprire finestre di attivazione. "
            . "Quando l'installazione e verificata, indicami l'icona sul Desktop Attiva Agentic AI Operator System. "
            . "Chiedimi di aprirla, inserire la chiave, attendere Licenza attiva, chiudere la finestra e confermartelo. "
            . "Attendi la mia risposta. Poi verifica LicenseStatus e, solo se attivo, invitami a riavviare ChatGPT/Codex. "
            . "Distingui installazione riuscita da attivazione verificata.";
    }
}
