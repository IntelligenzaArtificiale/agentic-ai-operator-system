# Installazione autonoma di Agentic AI Operator System da parte di ChatGPT/Codex

Questo pacchetto contiene tutto il necessario e non richiede Python, pip o privilegi
di amministratore. Deve essere installato solo dopo una richiesta esplicita
dell'utente.

## Procedura obbligatoria per l'agente

1. Estrarre tutto lo ZIP in una directory temporanea locale.
2. Verificare che esistano `app\winbridge.exe` e `Install-WinBridge.ps1`.
3. Eseguire da PowerShell, senza usare automazione grafica:

   ```powershell
   & '.\Install-WinBridge.ps1' -NonInteractive
   ```

4. Leggere il file `INSTALL_RESULT.json` indicato dall'installer.
5. Verificare che `ok`, `plugin_installed` e `mcp_configured` siano `true`.
6. Chiedere all'utente di chiudere completamente e riaprire ChatGPT/Codex. Il
   riavvio dell'app non deve essere automatizzato.
7. Dopo il riavvio, aprire una **nuova task**: una task gia aperta conserva il
   precedente elenco degli strumenti e non acquisisce Agentic AI Operator System a posteriori.
8. Nella nuova task verificare la presenza del server globale `winbridge` con `/mcp` e
   della skill `$windows-desktop-control`. Per ogni azione sul desktop Windows
   usare sempre prima Agentic AI Operator System.

## Cosa fa l'installer

- Installa il plugin personale in `%USERPROFILE%\plugins\winbridge`.
- Aggiorna il marketplace personale preservando gli altri plugin e creando un backup.
- Registra `winbridge@personal`, il server MCP globale `winbridge` e la skill
  `$windows-desktop-control`.
- Rende il server obbligatorio all'avvio e pre-approva i suoi strumenti per
  ridurre attese e richieste ripetute di conferma.
- Esegue una diagnostica e produce `INSTALL_RESULT.json`.
- Non installa servizi, driver, attività pianificate o avvii automatici Windows.

## Aggiornamenti

`Check-WinBridgeUpdate.ps1` controlla un manifest HTTPS configurabile. Il controllo
non installa nulla senza `-Install`; prima dell'installazione verifica sempre SHA-256.
Il file `UPDATE_MANIFEST.example.json` mostra il formato da pubblicare.

Il server viene avviato su richiesta dall'host ChatGPT/Codex e quindi non occupa RAM
quando ChatGPT/Codex non lo sta usando.
