---
name: start-agentic-ai-operator-system
description: Presenta in modo molto breve Agentic AI Operator System, l'ordine consigliato dei comandi e il collegamento alla dashboard. Usala quando l'utente scrive start, onboarding o /start-agentic-ai-operator-system.
---

# Start Agentic AI Operator System

Spiega il sistema senza dettagli tecnici, in italiano semplice e in non più di
otto punti brevi. Presenta questo ordine:

1. `$profilo-azienda`: crea il DNA dell'azienda con poche domande e informazioni pubbliche verificate;
2. `$crea-procedura`: trasforma una registrazione OpenSteps in una procedura;
3. `$crea-procedura-guidata`: crea una procedura descrivendola in chat;
4. `$collauda-procedura`: prova il flusso, impara dagli errori e ne verifica il risultato;
5. `$ottimizza-procedura`: riduce tempi e interventi dell'IA dopo dati sufficienti;
6. `$avvia-procedura`: esegue una procedura pronta;
7. `$visualizza-procedure`: aggiorna e apre il catalogo locale.

Indica come primo passo `$profilo-azienda` se `company-profile.json` è assente o ha
`status: not_configured`; altrimenti mostra il nome dell'azienda e suggerisci la
creazione della prima procedura. Non avviare interviste o procedure da questa skill.

Assicurati che il dashboard esista eseguendo `Update-Dashboard.ps1` se disponibile,
poi restituisci sempre un link Markdown cliccabile al file locale
`%USERPROFILE%\Documents\Agentic AI Operator System\catalogo\index.html`.
