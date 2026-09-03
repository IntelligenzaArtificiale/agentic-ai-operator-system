---
name: nome-procedura
description: Esegue la procedura aziendale descritta in questa directory quando richiesta per nome.
---

# Nome procedura

Definire scopo, input, prerequisiti, percorso normale, condizioni, errori e criteri di successo. Prima di agire chiamare `procedure-runner.PrepareRun` e seguire tutti gli step obbligatori con la memoria collegata. Leggere `execution-plan.json`: usare `procedure-runner` per blocchi deterministici compilati e Windows-MCP solo per esplorazione, ragionamento, deviazioni e verifiche proporzionate al rischio. Prima dell'esito chiamare `procedure-runner.ValidateRunCoverage`; salvare tempi distinti, incidenti e run secondo `references/telemetry-schema.md`.
