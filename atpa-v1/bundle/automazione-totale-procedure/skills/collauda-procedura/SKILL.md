---
name: collauda-procedura
description: Collauda una procedura aziendale esistente con Windows-MCP, raccoglie prove visive e aggiorna lo stato. Usala quando l'utente chiede di testare o validare una procedura.
---

# Collauda procedura

Risolvi il nome nella directory `%USERPROFILE%\Documents\Agentic AI Operator System\procedure`; se più nomi corrispondono, chiedi quale. Leggi `procedure.json`, `SKILL.md` e solo i riferimenti necessari al caso.

- Richiedi gli input mancanti prima dell'esecuzione.
- Usa esclusivamente `windows-mcp` per l'interfaccia Windows.
- Verifica che ogni azione sia indirizzata ad applicazione, finestra, vista e controllo corretti; testa in particolare i cambi di contesto e che l'input sostituisca, anziché concatenare, contenuti preesistenti.
- Considera difetto della procedura l'apertura non necessaria di terminali, shell o script per pilotare applicazioni che possono essere usate direttamente.
- Esegui prima il caso normale, quindi le sole eccezioni che possono essere provate senza conseguenze indesiderate.
- Minimizza token e round trip senza ridurre l'affidabilità: preferisci azioni deterministiche e batch soltanto in un contesto stabile; `Screenshot` ai checkpoint; `Snapshot` solo per rimappare elementi o leggere struttura; riusa lo stato stabile; evita di rileggere registrazioni e immagini storiche.
- Dopo un'azione senza cambiamento visibile, acquisisci stato fresco e correggi al massimo due volte. Non dichiarare successo dal solo esito del tool.
- Salva in `tests\<timestamp>-report.md` esito, durata, input mascherati quando opportuno, checkpoint verificati, errori e screenshot finali utili.
- Se tutti i criteri risultano verificati, imposta `status` a `validated` e aggiorna `last_tested_at`; altrimenti lascia `draft` e registra il motivo.
- Rigenera il dashboard. Non rendere attiva una procedura non validata.
