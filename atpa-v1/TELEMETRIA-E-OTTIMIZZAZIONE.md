# Telemetria, esperienza e ottimizzazione

Il sistema conserva tre livelli separati:

1. `runs/*.json`: fatti immutabili di ogni esecuzione, con tempi per step.
2. `experience/errors.jsonl`: incidenti osservati, recupero e causa probabile.
3. `experience/lessons.json`: regole preventive consolidate e contestuali.

Questa separazione evita che un errore transitorio riscriva subito una procedura.
La skill `$ottimizza-procedura` usa le run come baseline, prova soltanto passaggi
senza effetti produttivi e modifica il flusso quando il vantaggio è verificato.

## Esperimento Gmail del 25 agosto 2026

Il collaudo reale ha evidenziato tre incidenti: digitazione senza target esplicito,
inserimento del corpo dentro una firma HTML e timeout del toast di invio. Il
recupero ha usato target espliciti, sostituzione completa del corpo e verifica
nella cartella Inviati.

- prima esecuzione esplorativa: circa 86 secondi;
- esecuzione ottimizzata: circa 21,6 secondi;
- riduzione misurata: circa 75%;
- checkpoint critici conservati: verifica bozza e verifica in Inviati.
