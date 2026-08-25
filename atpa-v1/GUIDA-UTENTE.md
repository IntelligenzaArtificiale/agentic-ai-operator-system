# Agentic AI Operator System

Sistema ideato da **Alessandro Ciciarelli**, fondatore di **Intelligenza Artificiale Italia** — [IntelligenzaArtificialeItalia.net](https://intelligenzaartificialeitalia.net).

## Dopo l'installazione

Chiudi completamente ChatGPT/Codex, riaprilo e crea una nuova task. Le funzioni centrali disponibili sono:

- `$crea-procedura`: riceve uno o più path esportati dal registratore e genera una procedura dinamica.
- `$crea-procedura-guidata`: crea una procedura senza registrazione tramite domande adattive, una per volta.
- `$collauda-procedura`: esegue il test reale e salva prove e report.
- `$avvia-procedura`: esegue una procedura per nome.
- `$modifica-procedura`: modifica procedura, skill, flow e versione.
- `$ottimizza-procedura`: analizza tempi ed errori, prova step sicuri e riduce i tempi misurati.
- `$visualizza-procedure`: apre il catalogo locale già pronto con esecuzioni, tempi ed errori.

## Prima procedura

1. Apri dal Desktop **Agentic AI Operator System - OpenSteps**.
2. Registra il processo, correggi i passaggi e aggiungi nelle descrizioni bivi ed eccezioni.
3. Esporta in Markdown in una nuova cartella sotto `Documenti\Agentic AI Operator System\registrazioni`.
4. In una nuova task scrivi: `$crea-procedura`, indicando il nome e i path restituiti dal registratore.

In alternativa, senza usare il registratore, avvia `$crea-procedura-guidata` e descrivi in poche parole il processo. La skill raccoglie soltanto le informazioni mancanti, una domanda per volta, quindi crea la stessa struttura standard pronta per il collaudo.
5. Esegui `$collauda-procedura <nome>`.
6. Quando il collaudo è positivo, usa `$avvia-procedura <nome>`.

Le procedure sono conservate in `Documenti\Agentic AI Operator System\procedure`; il template non è una procedura attiva e si trova in `TEMPLATE-PROCEDURA`.

## Aggiornamenti

Esegui `Check-AgenticUpdate.ps1` senza parametri per controllare una nuova versione.
Il controllo non installa nulla. Dopo una conferma esplicita, usa
`Check-AgenticUpdate.ps1 -Install`: il pacchetto viene scaricato da GitHub,
verificato tramite SHA-256 e installato conservando procedure e registrazioni.

## Prestazioni

Ogni collaudo ed esecuzione salva una run JSON con tempi per step. Gli errori diventano incidenti documentati e lezioni contestuali per evitare recidive. Il sistema raggruppa le azioni deterministiche, usa schermate leggere ai checkpoint e richiede analisi strutturali complete soltanto quando la schermata cambia o presenta un bivio. La verifica finale resta obbligatoria.
