# Telemetria, esperienza e ottimizzazione

La telemetria 3 separa tempo di azione locale, attesa, osservazione IA, verifica e
recupero. Le procedure attraversano `exploratory`, `stabilizing`,
`compiled_candidate`, `compiled` e `degraded`. Solo run pulite e confrontabili
promuovono un piano; una guardia fallita riattiva l'IA sulla sola porzione instabile.

Il sistema conserva tre livelli separati:

1. `runs/*.json`: fatti immutabili di ogni esecuzione, con tempi per step.
2. `experience/errors.jsonl`: incidenti osservati, recupero e causa probabile.
3. `experience/lessons.json`: regole preventive consolidate e contestuali.

Questa separazione evita che un errore transitorio riscriva subito una procedura.
La skill `$ottimizza-procedura` usa le run come baseline, prova soltanto passaggi
senza effetti produttivi e modifica il flusso quando il vantaggio è verificato.

## Criterio di validità

Una run è utilizzabile come baseline soltanto quando il risultato è verificato con
una prova persistente e specifica nel sistema di destinazione. Feedback transitori,
chiusura di una vista, navigazione o successo tecnico del tool non sono sufficienti.
Le durate di run prive di questa prova non sono benchmark e l'ottimizzatore deve
escluderle dai confronti.
