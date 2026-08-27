---
name: crea-procedura
description: Trasforma una o più esportazioni del registratore in una procedura aziendale dinamica e riutilizzabile. Usala quando l'utente indica i path Markdown o delle cartelle registrate e vuole creare la procedura.
---

# Crea procedura

Ricevi dall'utente uno o più path esportati dal registratore e il nome della procedura. La radice predefinita è `%USERPROFILE%\Documents\Agentic AI Operator System`. Se `company-profile.json` è configurato, usalo soltanto per contestualizzare reparto, ruoli e strumenti senza dedurre azioni non richieste.

1. Leggi integralmente Markdown, trascrizioni audio, immagini e metadati UI disponibili. Se sono presenti più registrazioni, confrontale e separa invarianti da dati variabili.
2. Prima di creare file, individua le ambiguità che possono cambiare comportamento, input, bivi, criteri di successo o gestione degli errori. Se ne esistono, poni in chat una sola domanda concreta, attendi la risposta, incorporala e ripeti finché le ambiguità sostanziali sono risolte. Non fare questionari multipli, non inventare risposte e non chiedere dettagli puramente editoriali deducibili dagli asset. Quando utile, proponi nella domanda l'interpretazione più probabile.
3. Crea uno slug breve e una directory sotto `procedure\<slug>`, copiando gli originali in `recording\` senza modificarli.
4. Genera `procedure.json`, `execution-plan.json`, `SKILL.md`, `references\procedure.md`, `references\test-cases.md`, `references\screenshots\`, `tests\`, `runs\`, `experience\errors.jsonl` e `experience\lessons.json`. Parti dagli schemi in `TEMPLATE-PROCEDURA`.
5. Il `SKILL.md` della procedura deve descrivere input, prerequisiti, risultato osservabile, percorso normale, bivi, errori e condizioni di arresto. Deve richiedere gli strumenti `windows-mcp`.
6. Classifica il flusso in blocchi deterministici, cognitivi ed effetti esterni. Inizializza `execution-plan.json` come `exploratory`: non dichiarare compilati passaggi mai ripetuti. Converti click e coordinate in intenzioni e target semantici; conserva coordinate solo come candidato contestuale associato a fingerprint e guardie ambientali.
7. Applica il protocollo adattivo: osservazione completa in esplorazione, poi raggruppa azioni deterministiche nello stesso contesto stabile; usa osservazione IA solo per decisioni, deviazioni e prove significative. Non imporre uno screenshot dopo ogni click.
8. Per l'interazione ordinaria usa l'interfaccia dell'applicazione. Non introdurre terminali, shell o script come scorciatoia per avviare o pilotare programmi, salvo che la procedura li richieda oppure l'interfaccia non sia utilizzabile e il fallback sia esplicitamente appropriato.
9. Compila in `procedure.json` reparto, categoria, ruoli, versione `1.0.0`, stato `draft`, input e un flow con nodi/archi. Se un metadato editoriale non è deducibile, usa una stringa vuota; non usare questo espediente per ambiguità operative.
10. Esegui lo script runtime `Update-Dashboard.ps1` se disponibile e comunica path creato, input individuati e punti ancora da collaudare. Non eseguire la procedura in questa fase.

Firma editoriale dei file generati: “Agentic AI Operator System · Alessandro Ciciarelli · Intelligenza Artificiale Italia”.
