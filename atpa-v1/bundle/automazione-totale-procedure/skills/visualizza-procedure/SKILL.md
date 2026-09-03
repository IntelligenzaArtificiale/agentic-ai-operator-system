---
name: visualizza-procedure
description: Aggiorna e apre il dashboard locale delle procedure aziendali, con stato sistema, filtri, dettagli e diagrammi. Usala quando l'utente vuole vedere o consultare il catalogo procedure.
---

# Visualizza procedure

Prima di leggere file o generare la dashboard, chiama `windows-mcp.LicenseStatus`. Se la licenza non è attiva, non accedere al catalogo e usa soltanto `windows-mcp.OpenLicenseActivation`; non chiedere mai la chiave in chat.

Il dashboard predefinito è `http://127.0.0.1:8765/`: il server locale verifica la licenza a ogni richiesta. Viene aggiornato automaticamente dopo creazione, modifica, collaudo, esecuzione e ottimizzazione.

Esegui una sola volta lo script runtime `Update-Dashboard.ps1 -Open`, quindi
restituisci il link locale cliccabile. Non aprire direttamente vecchi file del
catalogo: dalla versione 2.5.0 contengono soltanto un avviso di attivazione.

Il dashboard mostra profilo aziendale, stato sistema, numero di esecuzioni, successi, errori, durata
media e migliore, ultima durata e step più lenti per ogni procedura.

Se lo script non esiste, segnala che l'installazione deve essere riparata. Non ricostruire manualmente il dashboard e non usare Windows-MCP per navigare nella pagina salvo richiesta dell'utente.
