# Struttura delle procedure

Ogni procedura è autonoma ma viene caricata dinamicamente dalle skill centrali; non richiede reinstallazione o riavvio.

```text
procedure/<slug>/
├── procedure.json              metadati, input, stato e diagramma
├── SKILL.md                    istruzioni eseguibili per l'agente
├── CHANGELOG.md                versioni e modifiche
├── recording/                  esportazioni originali immutabili
├── references/
│   ├── procedure.md            guida umana completa
│   ├── test-cases.md           casi normali, errori e ambiguità
│   └── screenshots/            sole immagini utili all'esecuzione
├── tests/                      report di collaudo
└── runs/                       report compatti di esecuzione
```

La radice di sistema contiene inoltre `experience/software`,
`experience/business` ed `experience/patterns`: memoria condivisa selezionata in
base a `procedure.json > experience_context`, non caricata indiscriminatamente.

## Stati

- `draft`: nuova o modificata, richiede collaudo.
- `validated`: collaudo riuscito e criteri verificati.
- `active`: approvata per l'uso operativo ordinario.

## Regole di efficienza

Le registrazioni originali non vengono caricate durante l'esecuzione normale. La skill usa istruzioni compatte e apre riferimenti soltanto nei bivi pertinenti. Azioni deterministiche vengono aggregate; `Screenshot` è il checkpoint leggero; `Snapshot` è riservato alla scoperta o rimappatura della UI. Ogni procedura definisce checkpoint significativi invece di verificare indiscriminatamente ogni singola azione.

## Metadati catalogo

`company-profile.json` contiene il DNA aziendale globale, le fonti e le priorità di automazione. `procedure.json` contiene nome, slug, descrizione, reparto, categoria, ruoli, stato, versione, date, input, risultato atteso, contesto esperienza e grafo del flusso con identificativi stabili. `execution-plan.json` conserva la versione eseguibile: blocchi deterministici locali, blocchi cognitivi, effetti, guardie, fingerprint e stato di apprendimento. Il dashboard legge file e telemetria, senza avviare procedure in background.

Firma editoriale: **Agentic AI Operator System · Alessandro Ciciarelli · Intelligenza Artificiale Italia**.
