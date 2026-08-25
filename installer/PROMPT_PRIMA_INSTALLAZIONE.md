# Prompt per ChatGPT/Codex

## Prima installazione

```text
Installa autonomamente Agentic AI Operator System da questo ZIP seguendo integralmente AGENTS.md e INSTALL_FOR_CHATGPT.md. Estrai lo ZIP in una cartella temporanea, esegui Install-WinBridge.ps1 -NonInteractive, leggi INSTALL_RESULT.json e considera riuscita l'installazione solo se ok, plugin_installed e mcp_configured sono true. Non usare Computer Use per installarlo. Alla fine indicami esattamente se devo riavviare l'app.
```

## Prima verifica dopo il riavvio

```text
Verifica con /mcp che il server globale winbridge sia disponibile, quindi chiama health_check. Verifica anche il plugin Agentic AI Operator System e la skill $windows-desktop-control. Usa esclusivamente il tool MCP create_desktop_note per creare sul Desktop "Test-Agentic AI Operator System.txt" con il testo "Test Agentic AI Operator System riuscito" e aprirlo in Blocco note. Se i tool MCP Agentic AI Operator System non sono presenti fermati subito: non avviare winbridge.exe tramite PowerShell, shell o exec e non usare Chrome, Browser o Computer Use.
```

## Controllo aggiornamenti

```text
Controlla se esistono aggiornamenti di Agentic AI Operator System eseguendo Check-WinBridgeUpdate.ps1 senza -Install. Leggi il JSON restituito e non installare nulla senza una mia conferma esplicita.
```

## Installazione aggiornamento autorizzato

```text
Ho autorizzato l'aggiornamento di Agentic AI Operator System. Esegui Check-WinBridgeUpdate.ps1 -Install, verifica SHA-256 e INSTALL_RESULT.json, quindi dimmi se serve riavviare ChatGPT/Codex.
```
