---
name: visualizza-procedure
description: Aggiorna e apre il dashboard locale delle procedure aziendali, con stato sistema, filtri, dettagli e diagrammi. Usala quando l'utente vuole vedere o consultare il catalogo procedure.
---

# Visualizza procedure

Il dashboard predefinito è `%USERPROFILE%\Documents\Agentic AI Operator System\catalogo\index.html` e viene creato dall'installer, poi aggiornato automaticamente dopo creazione, modifica, collaudo, esecuzione e ottimizzazione.

Se `index.html` e `data.js` esistono, non rigenerarli: restituisci subito il link
locale cliccabile e aprilo tramite `windows-mcp`, senza terminale o PowerShell. Se
mancano o `data.js` è più vecchio dell'ultima run, esegui una sola volta lo script
runtime `Update-Dashboard.ps1`, quindi apri il file.

Il dashboard mostra profilo aziendale, stato sistema, numero di esecuzioni, successi, errori, durata
media e migliore, ultima durata e step più lenti per ogni procedura.

Se lo script non esiste, segnala che l'installazione deve essere riparata. Non ricostruire manualmente il dashboard e non usare Windows-MCP per navigare nella pagina salvo richiesta dell'utente.
