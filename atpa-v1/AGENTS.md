# Installazione autonoma

Installa **Agentic AI Operator System 2.2.0** su Windows 10/11 x64.

1. Leggi integralmente questo file e `GUIDA-UTENTE.md`.
2. Verifica che lo ZIP sia stato estratto localmente e contenga `payload`, `bundle`, `runtime`, `template` e `Install-System.ps1`.
3. Esegui senza automazione grafica:
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-System.ps1 -NonInteractive`
4. Leggi `INSTALL_RESULT.json`. Non dichiarare successo se `ok`, `mcp_configured`, `runner_configured`, `plugin_installed`, `opensteps_installed`, `updater_installed` e `dashboard_ready` non sono tutti `true`.
5. Verifica inoltre `codex mcp get windows-mcp`, `codex mcp get procedure-runner` e la presenza di `automazione-totale-procedure@personal` in `codex plugin list`.
6. Comunica all'utente di chiudere completamente ChatGPT/Codex, riaprirlo e creare una nuova task.
7. Concludi: “Il sistema è pronto. Puoi creare la prima procedura da una registrazione con `$crea-procedura` oppure direttamente in chat con `$crea-procedura-guidata`.”

Non avviare manualmente server MCP persistenti e non usare Computer Use durante l'installazione.
