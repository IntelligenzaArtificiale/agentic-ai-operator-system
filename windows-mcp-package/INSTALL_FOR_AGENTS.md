# Windows-MCP 0.8.5 per ChatGPT/Codex

Il pacchetto include il wheel ufficiale CursorTouch 0.8.5, una copia di `uv.exe`, il plugin Codex e l'installer automatico. Internet è consigliato per scaricare le dipendenze; il wheel principale è già incluso.

## Prompt per la prima installazione

> Installa autonomamente Windows-MCP dallo ZIP che trovi in `<PERCORSO_ZIP>`. Estrai lo ZIP in una cartella locale, leggi integralmente `AGENTS.md`, esegui `Install-WindowsMCP.ps1 -NonInteractive`, verifica `INSTALL_RESULT.json`, `codex mcp get windows-mcp` e `codex plugin list`. Non usare Computer Use per installarlo e non dichiarare successo finché tutte le verifiche non risultano positive. Alla fine dimmi se devo riavviare ChatGPT/Codex.

## Prompt di collaudo dopo il riavvio

> Usa esclusivamente Windows-MCP. Acquisisci uno Screenshot, apri Blocco note, scrivi una breve riga, acquisisci un nuovo Screenshot e verifica visivamente che la riga sia presente. Chiudi Blocco note senza salvare e conferma il risultato soltanto dopo l'ultima verifica visiva.

## Aggiornamenti

Esegui `Check-WindowsMCPUpdate.ps1` per vedere l'ultima versione pubblicata su PyPI; aggiungi `-Install` per installarla. Dopo un aggiornamento riavvia completamente ChatGPT/Codex.

Progetto originale e documentazione: https://github.com/CursorTouch/Windows-MCP (licenza MIT).
