# Installazione autonoma per agenti

Obiettivo: installare questo pacchetto locale Windows-MCP in ChatGPT/Codex senza usare Computer Use o automazione grafica.

1. Verifica che il sistema sia Windows x64 e che la cartella estratta contenga `payload/uv.exe`, il wheel `windows_mcp-0.8.5-py3-none-any.whl`, `plugin/` e `Install-WindowsMCP.ps1`.
2. Da PowerShell esegui una sola volta:
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-WindowsMCP.ps1 -NonInteractive`
3. Leggi `INSTALL_RESULT.json`. Considera l'installazione riuscita solo se `ok`, `mcp_configured` e `plugin_installed` sono tutti `true`.
4. Verifica anche con `codex mcp get windows-mcp` e `codex plugin list`. Non avviare manualmente il server in background: Codex lo avvia via stdio quando serve.
5. Comunica all'utente che deve chiudere completamente ChatGPT/Codex, riaprirlo e creare una nuova task affinché MCP e skill vengano caricati.
6. Nella nuova task, prova prima `Screenshot`; poi completa un piccolo click e acquisisci un nuovo `Screenshot` per verificare visivamente il cambiamento.

Non dichiarare successo se il server appare solo nelle impostazioni ma i tool non sono presenti nella nuova task.
