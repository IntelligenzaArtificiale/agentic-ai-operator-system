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

## Stati

- `draft`: nuova o modificata, richiede collaudo.
- `validated`: collaudo riuscito e criteri verificati.
- `active`: approvata per l'uso operativo ordinario.

## Regole di efficienza

Le registrazioni originali non vengono caricate durante l'esecuzione normale. La skill usa istruzioni compatte e apre riferimenti soltanto nei bivi pertinenti. Azioni deterministiche vengono aggregate; `Screenshot` è il checkpoint leggero; `Snapshot` è riservato alla scoperta o rimappatura della UI. Ogni procedura definisce checkpoint significativi invece di verificare indiscriminatamente ogni singola azione.

## Metadati catalogo

`procedure.json` contiene nome, slug, descrizione, reparto, categoria, ruoli, stato, versione, date, input, risultato atteso e grafo del flusso. Il dashboard legge esclusivamente questi metadati e gli screenshot selezionati, quindi non avvia processi MCP in background.

Firma editoriale: **Agentic AI Operator System · Alessandro Ciciarelli · Intelligenza Artificiale Italia**.
