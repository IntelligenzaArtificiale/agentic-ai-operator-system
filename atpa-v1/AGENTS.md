# Installazione autonoma

Installa **Agentic AI Operator System 2.5.2** su Windows 10/11 x64.

1. Leggi integralmente questo file e `GUIDA-UTENTE.md`.
2. Verifica che lo ZIP sia stato estratto localmente e contenga `payload`, `bundle`, `runtime`, `template` e `Install-System.ps1`.
3. Esegui senza automazione grafica:
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-System.ps1 -NonInteractive`
4. Leggi `INSTALL_RESULT.json`. Non dichiarare successo se `ok`, `mcp_configured`, `runner_configured`, `plugin_installed`, `opensteps_installed`, `licensing_installed`, `activation_shortcut`, `updater_installed`, `dashboard_ready` e `company_profile_ready` non sono tutti `true`.
5. Verifica inoltre `codex mcp get windows-mcp`, `codex mcp get procedure-runner` e la presenza di `automazione-totale-procedure@personal` in `codex plugin list`.
6. Distingui installazione riuscita da licenza attiva. Non aprire finestre di attivazione e non rilanciare l'installer per un problema di licenza. Comunica: “Sul Desktop trovi **Attiva Agentic AI Operator System**. Aprila, inserisci la chiave, attendi **Licenza attiva**, chiudi la finestra e dimmi quando hai finito.” Non chiedere né leggere mai la chiave in chat o da terminale. Attendi la risposta dell'utente.
7. Dopo la sua conferma verifica lo stato con `LicenseStatus` (oppure `licensing/check.py` installato). Solo se `active=true`, invita a chiudere completamente ChatGPT/Codex, riaprirlo e creare una nuova task. Poi: “Inizia con `$start-agentic-ai-operator-system`, quindi configura il DNA con `$profilo-azienda`.” Se la verifica fallisce, riporta il messaggio senza chiedere la chiave e senza aprire automaticamente altre finestre.

Non avviare manualmente server MCP persistenti e non usare Computer Use durante l'installazione.
