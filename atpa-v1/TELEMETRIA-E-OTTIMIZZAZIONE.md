# Telemetria, esperienza e ottimizzazione

Il sistema conserva tre livelli separati:

1. `runs/*.json`: fatti immutabili di ogni esecuzione, con tempi per step.
2. `experience/errors.jsonl`: incidenti osservati, recupero e causa probabile.
3. `experience/lessons.json`: regole preventive consolidate e contestuali.

Questa separazione evita che un errore transitorio riscriva subito una procedura.
La skill `$ottimizza-procedura` usa le run come baseline, prova soltanto passaggi
senza effetti produttivi e modifica il flusso quando il vantaggio è verificato.

## Criterio di validità

Una run è utilizzabile come baseline soltanto quando il risultato è verificato con
una prova persistente e specifica. Per un'email questo richiede di aprire il
messaggio da Inviati e controllare destinatario, oggetto e un marcatore del corpo.
Toast, chiusura del composer e presenza del solo oggetto non sono sufficienti.

Il test Gmail del 25 agosto 2026 è stato invalidato perché non ha dimostrato
destinatario e invio. Le durate precedentemente riportate non costituiscono un
benchmark e non devono essere usate dall'ottimizzatore.
