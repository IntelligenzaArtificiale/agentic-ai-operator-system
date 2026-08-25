---
name: collauda-procedura
description: Collauda una procedura aziendale esistente con Windows-MCP, raccoglie prove visive e aggiorna lo stato. Usala quando l'utente chiede di testare o validare una procedura.
---

# Collauda procedura

Risolvi il nome nella directory `%USERPROFILE%\Documents\Agentic AI Operator System\procedure`; se più nomi corrispondono, chiedi quale. Leggi `procedure.json`, `SKILL.md`, `experience\lessons.json` e solo i riferimenti necessari al caso.

Prima del primo collaudo avvisa che può durare più di un'esecuzione normale:
include osservazioni aggiuntive, analisi degli errori e misurazione di ogni step.
Apri una run con modalità `test` e usa lo schema in
`references\telemetry-schema.md`.

- Richiedi gli input mancanti prima dell'esecuzione.
- Usa esclusivamente `windows-mcp` per l'interfaccia Windows.
- Verifica che ogni azione sia indirizzata ad applicazione, finestra, vista e controllo corretti; testa in particolare i cambi di contesto e che l'input sostituisca, anziché concatenare, contenuti preesistenti.
- Considera difetto della procedura l'apertura non necessaria di terminali, shell o script per pilotare applicazioni che possono essere usate direttamente.
- Esegui prima il caso normale, quindi le sole eccezioni che possono essere provate senza conseguenze indesiderate.
- Minimizza token e round trip senza ridurre l'affidabilità: preferisci azioni deterministiche e batch soltanto in un contesto stabile; `Screenshot` ai checkpoint; `Snapshot` solo per rimappare elementi o leggere struttura; riusa lo stato stabile; evita di rileggere registrazioni e immagini storiche.
- Dopo un'azione senza cambiamento visibile, acquisisci stato fresco e correggi al massimo due volte. Non dichiarare successo dal solo esito del tool.
- Misura inizio, fine e durata di ogni step logico, con tentativi e verifica.
- Per ogni errore, ferma la sequenza, osserva stato fresco, recupera in sicurezza,
  aggiungi l'incidente a `experience\errors.jsonl` e alla run. Registra bersaglio o
  coordinate, azione prevista, risultato errato, causa, recupero e prevenzione.
- Aggiorna `experience\lessons.json` soltanto con lezioni contestuali e dimostrate;
  applicale nei passaggi successivi e nei collaudi futuri.
- Salva in `tests\<timestamp>-report.md` esito, durata, input mascherati quando opportuno, checkpoint verificati, errori e screenshot finali utili; salva sempre anche `runs\<run-id>.json`.
- Se tutti i criteri risultano verificati, imposta `status` a `validated` e aggiorna `last_tested_at`; altrimenti lascia `draft` e registra il motivo.
- Aggiorna le statistiche `telemetry` in `procedure.json` e rigenera il dashboard.
  Non rendere attiva una procedura non validata.
