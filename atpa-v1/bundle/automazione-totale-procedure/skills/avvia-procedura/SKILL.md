---
name: avvia-procedura
description: Esegue per nome una procedura aziendale già creata usando Windows-MCP. Usala quando l'utente chiede di avviare, eseguire o completare una procedura catalogata.
---

# Avvia procedura

Trova la procedura per nome o slug sotto `%USERPROFILE%\Documents\Agentic AI Operator System\procedure`. Leggi prima `procedure.json`, il suo `SKILL.md` e `experience\lessons.json`; carica riferimenti, incidenti storici ed eccezioni solo quando diventano rilevanti. Avvisa se lo stato non è `validated` o `active` e chiedi conferma prima di eseguire una bozza.

## Run e memoria operativa

Apri una run prima della prima azione e misura con timestamp UTC ogni step logico,
non ogni singola chiamata interna. Registra in `runs\<run-id>.json` modalità
`production`, inizio/fine, durata, esito, tentativi, checkpoint e metriche secondo
`references\telemetry-schema.md`. Aggiorna il file alla fine anche in caso di
fallimento o interruzione.

Applica preventivamente le lezioni il cui trigger coincide con applicazione,
schermata e step correnti. Non applicare una lezione fuori contesto.

Quando un'azione produce uno stato errato o inatteso:

1. ferma la sequenza e osserva stato fresco;
2. metti il sistema in uno stato sicuro, correggendo al massimo due volte;
3. registra in `experience\errors.jsonl` cosa era previsto, bersaglio o coordinate,
   cosa è accaduto, causa probabile, recupero verificato e regola preventiva;
4. consolida o aggiorna una lezione in `experience\lessons.json` solo se è
   specifica, riproducibile e supportata dall'evidenza;
5. collega l'incidente alla run e prosegui soltanto se il risultato resta sicuro.

Non memorizzare segreti. Non considerare errore un'attesa normale o un cambiamento
UI già gestito; non trasformare un singolo evento transitorio in una regola rigida.

Usa esclusivamente `windows-mcp` per il desktop. Ottimizza l'esecuzione:

- prima di digitare o cliccare, assicurati che applicazione, finestra, vista e controllo di destinazione siano quelli previsti; quando cambi contesto, usa un'azione esplicita che sostituisca eventuale contenuto precedente;
- pilota normalmente l'interfaccia dell'applicazione e non aprire terminali o shell come scorciatoia, salvo che siano parte della procedura o un fallback necessario e appropriato dopo verifica;
- azioni meccaniche, scorciatoie, input completi e batch prima del ragionamento visuale;
- un singolo checkpoint per una sequenza deterministica senza bivi;
- `Screenshot` per osservazione veloce e verifica; `Snapshot` solo quando serve identificare controlli, testo, DOM o rimappare una schermata cambiata;
- riusa label, finestra e mappatura finché lo stato resta coerente;
- checkpoint immediati per condizioni, errori, conferme, invii e risultati finali;
- non caricare screenshot storici durante il percorso normale se le istruzioni testuali sono sufficienti;
- massimo due tentativi correttivi basati su stato fresco;
- il risparmio di token non giustifica mai un'azione ambigua, un contesto non verificato o un workaround più fragile dell'interazione diretta.

Raccogli gli input necessari, esegui, verifica il risultato finale, aggiorna le
statistiche `telemetry` in `procedure.json` e rigenera il dashboard. Non affermare
mai un risultato non osservato.
