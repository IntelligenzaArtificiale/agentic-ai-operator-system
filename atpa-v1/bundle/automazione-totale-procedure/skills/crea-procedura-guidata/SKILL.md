---
name: crea-procedura-guidata
description: Progetta e crea una procedura aziendale completa tramite intervista, senza richiedere registrazioni OpenSteps. Usala quando l'utente vuole descrivere a voce o in chat un nuovo processo da automatizzare.
---

# Crea procedura guidata

Costruisci una procedura sotto `%USERPROFILE%\Documents\Agentic AI Operator System\procedure` partendo dalle informazioni dell'utente, senza richiedere né avviare OpenSteps. Se `company-profile.json` è configurato, riusa nomi, reparti e strumenti pertinenti senza trasformarli in passaggi impliciti.

## Intervista adattiva

1. Ricava prima tutto ciò che è già presente nel messaggio e negli eventuali documenti forniti; non richiedere nuovamente informazioni note.
2. Mantieni internamente una bozza con scopo, evento di avvio, input, prerequisiti, applicazioni coinvolte, percorso normale, dati variabili, decisioni, eccezioni, risultato osservabile e criteri di successo.
3. Individua la lacuna più importante che impedisce di rendere la procedura eseguibile e poni una sola domanda concreta. Attendi la risposta prima di formularne un'altra.
4. Adatta la domanda successiva alle risposte già ricevute. Quando aiuta, proponi l'interpretazione più probabile da confermare o correggere. Non mostrare questionari, non interrogare su dettagli deducibili e non inventare passaggi mancanti.
5. Continua finché restano soltanto dettagli editoriali o varianti non necessarie al primo collaudo. Presenta quindi una sintesi compatta del flusso e chiedi, con una singola domanda, conferma alla creazione.

Non creare la directory definitiva prima della conferma. Se l'utente chiede esplicitamente di saltare le domande, crea comunque solo quando le informazioni consentono un flusso non ambiguo; altrimenti spiega la lacuna con una domanda sola.

## Creazione

1. Copia la struttura di `%USERPROFILE%\Documents\Agentic AI Operator System\TEMPLATE-PROCEDURA` in `procedure\<slug>` senza modificare il template originale; inizializza telemetria, `runs` ed `experience`.
2. Genera e completa `procedure.json`, `execution-plan.json`, `SKILL.md`, `references\procedure.md`, `references\test-cases.md`, `references\screenshots\`, `tests\`, `runs\`, `experience\errors.jsonl`, `experience\lessons.json` e `CHANGELOG.md`. La cartella `recording\` può essere assente o vuota: la procedura non deve dipendere da una registrazione.
3. Trasforma la descrizione umana in intenzioni e target semantici, non in coordinate inventate. Prima di ogni gruppo operativo stabilisci applicazione, finestra, vista e controllo destinatari; usa l'interazione diretta dell'applicazione e non workaround da terminale.
4. Classifica i passaggi come deterministici, cognitivi o effetti esterni e inizializza il piano come `exploratory`. Inserisci checkpoint significativi, bivi, condizioni di arresto, massimo due tentativi correttivi e una prova osservabile del risultato finale. L'esplorazione scopre le azioni; solo il collaudo può promuoverle a blocchi compilati.
5. Se un dettaglio dell'interfaccia potrà essere conosciuto solo durante il collaudo, descrivi un passo di individuazione semantica e segnalo tra i punti da verificare; non fabbricare label o coordinate.
6. Imposta versione `1.0.0` e stato `draft`, compila flow, reparto, categoria e ruoli, quindi valida JSON e struttura. Esegui `Update-Dashboard.ps1` se disponibile.
7. Comunica path creato, input richiesti, assunzioni confermate e aspetti da collaudare. Non eseguire automaticamente la procedura.

Firma editoriale: “Agentic AI Operator System · Alessandro Ciciarelli · Intelligenza Artificiale Italia”.
