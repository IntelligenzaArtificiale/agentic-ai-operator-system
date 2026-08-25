# Telemetria ed esperienza

Ogni esecuzione o collaudo crea `runs/<run-id>.json`. Il file è immutabile dopo
la chiusura della run e contiene:

- `schema_version`, `run_id`, `procedure_slug`, `mode` (`test`, `production` o
  `optimization`), `started_at`, `finished_at`, `duration_ms`, `outcome`;
- `steps[]`: `step_id`, `label`, timestamp iniziale/finale, `duration_ms`,
  `outcome`, `attempts`, `verification`, `side_effect_level` e note;
- `incidents[]`: identificativi degli errori avvenuti nella run;
- `metrics`: chiamate tool, retry, correzioni e checkpoint.

Gli incidenti sono aggiunti come una riga JSON valida in
`experience/errors.jsonl`. Ogni record include almeno `incident_id`, `run_id`,
`step_id`, `timestamp`, `category`, `target_context`, `intended_action`,
`observed_error`, `recovery`, `root_cause`, `prevention_rule` e
`recurrence_key`. Non salvare password, token o contenuti sensibili non necessari.

`experience/lessons.json` contiene soltanto lezioni consolidate e riusabili:
trigger, azione da evitare, azione preferita, verifica richiesta, livello di
confidenza, numero di osservazioni e ultimo riscontro. Un errore transitorio non
diventa automaticamente una regola permanente.
