---
name: collauda-procedura
description: Collauda una procedura aziendale esistente con Windows-MCP, raccoglie prove visive e aggiorna lo stato. Usala quando l'utente chiede di testare o validare una procedura.
---

# Collauda procedura

Risolvi il nome nella directory `%USERPROFILE%\Documents\Agentic AI Operator System\procedure`; se più nomi corrispondono, chiedi quale. Leggi `procedure.json`, `execution-plan.json`, `SKILL.md`, `experience\lessons.json` e solo i riferimenti necessari al caso.

Prima di agire chiama `procedure-runner.PrepareRun` e usa il risultato come
checklist obbligatoria: step concreti, errori locali collegati agli step, lezioni
locali ed esperienze condivise pertinenti. Inizializza `planned_steps`; nessuno step
obbligatorio può sparire perché ricordato in modo diverso dalla chat.

Prima del primo collaudo avvisa che può durare più di un'esecuzione normale:
include osservazioni aggiuntive, analisi degli errori e misurazione di ogni step.
Apri una run con modalità `test` e usa lo schema in
`references\telemetry-schema.md`.

- Richiedi gli input mancanti prima dell'esecuzione.
- Durante `exploratory` usa `windows-mcp` per osservare e scoprire. Trasforma i tratti stabili in blocchi dichiarativi del piano; non usare script applicativi o codice arbitrario.
- Verifica che ogni azione sia indirizzata ad applicazione, finestra, vista e controllo corretti; testa in particolare i cambi di contesto e che l'input sostituisca, anziché concatenare, contenuti preesistenti.
- Considera difetto della procedura l'apertura non necessaria di terminali, shell o script per pilotare applicazioni che possono essere usate direttamente.
- Esegui prima il caso normale, quindi le sole eccezioni che possono essere provate senza conseguenze indesiderate.
- In esplorazione osserva ogni passaggio significativo. In stabilizzazione ripeti dallo stesso stato iniziale e misura. Un candidato diventa `compiled` solo dopo almeno tre run pulite, verificate, senza recuperi e con variabilità entro la soglia del piano.
- Nei collaudi compilati chiama `procedure-runner.ExecuteBlock` per i blocchi deterministici: nessuno screenshot intermedio. Usa l'IA solo per blocchi `ai`, guardie fallite, rimappatura e checkpoint richiesti dal rischio.
- Dopo un'azione senza cambiamento visibile, acquisisci stato fresco e correggi al massimo due volte. Non dichiarare successo dal solo esito del tool.
- Per ogni effetto esterno osserva prima dell'azione i campi critici e salva una
  prova strutturata. Dopo l'azione verifica un artefatto persistente nel sistema di
  destinazione: feedback transitorio, chiusura di una vista o navigazione non
  bastano. Se manca la prova usa `unverified`, non ritentare automaticamente.
- Misura inizio, fine e durata di ogni step logico, con tentativi e verifica.
- Per ogni errore, ferma la sequenza, osserva stato fresco, recupera in sicurezza,
  aggiungi l'incidente a `experience\errors.jsonl` e alla run. Registra bersaglio o
  coordinate, azione prevista, risultato errato, causa, recupero e prevenzione.
- Collega sempre incidente e lezione locale a `step_id` e, se disponibile, a
  `block_id`. Se la conoscenza è indipendente dalla singola procedura, salvala anche
  sotto la memoria condivisa `software`, `business` o `patterns` come `candidate`.
- Aggiorna `experience\lessons.json` soltanto con lezioni contestuali e dimostrate;
  applicale nei passaggi successivi e nei collaudi futuri.
- Salva in `tests\<timestamp>-report.md` esito, durata, input mascherati quando opportuno, checkpoint verificati, errori e screenshot finali utili; salva sempre anche `runs\<run-id>.json`.
- Se tutti i criteri risultano verificati, imposta `status` a `validated` e aggiorna `last_tested_at`; altrimenti lascia `draft` e registra il motivo.
- Prima dell'esito finale chiama `procedure-runner.ValidateRunCoverage`. Uno step
  obbligatorio è coperto solo se eseguito oppure saltato con motivazione esplicita.
- Aggiorna le statistiche `telemetry` in `procedure.json` e rigenera il dashboard.
  Non rendere attiva una procedura non validata.
- Se una guardia compilata fallisce, imposta il piano `degraded`, registra la causa
  e rimappa con l'IA; non continuare usando coordinate non più garantite.
