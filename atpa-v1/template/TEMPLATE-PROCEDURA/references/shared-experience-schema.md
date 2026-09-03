# Esperienza condivisa

La memoria trasversale vive nella radice di sistema `experience/`, separata in
`software/`, `business/` e `patterns/`. Ogni file JSON contiene `schema_version`,
`id`, `scope`, `title`, `match` e `lessons`.

`match` può dichiarare `applications`, `departments`, `categories` e `patterns`.
Una procedura dichiara gli stessi campi in `procedure.json > experience_context`;
`refs` forza inoltre riferimenti espliciti nel formato `scope/nome`.

Ogni lezione condivisa contiene almeno `lesson_id`, `status` (`candidate` o
`validated`), `trigger`, `avoid`, `preferred_action`, `verification`,
`observations`, `distinct_procedures` ed `evidence`.

- Una lezione locale include sempre `step_ids` e resta nella procedura.
- Promuovi nella memoria condivisa solo conoscenza indipendente da dati, destinatari
  o obiettivi della singola procedura.
- Una nuova deduzione nasce `candidate`: può aggiungere un controllo o una cautela,
  ma non riscrive automaticamente un percorso compilato.
- Passa a `validated` dopo almeno tre riscontri verificati oppure due procedure
  distinte coerenti. Evidenze incerte non incrementano i conteggi.
- Non salvare credenziali, dati personali, contenuti aziendali sensibili o
  coordinate prive di fingerprint.
