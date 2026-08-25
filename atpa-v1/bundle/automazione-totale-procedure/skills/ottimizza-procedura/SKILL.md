---
name: ottimizza-procedura
description: Analizza telemetria, errori e lezioni di una procedura aziendale, prova in sicurezza i soli step isolabili e aggiorna la procedura per ridurne i tempi senza effetti produttivi. Usala quando l'utente chiede di velocizzare o ottimizzare una procedura esistente.
---

# Ottimizza procedura

Risolvi la procedura sotto `%USERPROFILE%\Documents\Agentic AI Operator System\procedure` e leggi `procedure.json`, `SKILL.md`, `references\telemetry-schema.md`, tutte le run valide e `experience\lessons.json`. Usa gli incidenti grezzi soltanto per approfondire anomalie già individuate.

## Analisi

Calcola per procedura e step almeno numero di campioni, tasso di successo, mediana,
minimo e massimo. Segnala come candidati gli step che hanno durata molto superiore
alla propria mediana, retry frequenti, osservazioni complete ripetute o attese
fisse sostituibili con condizioni. Con meno di tre campioni formula ipotesi, non
conclusioni statistiche.

Priorità:

1. eliminare errori ricorrenti applicando lezioni contestuali;
2. sostituire attese fisse con `WaitFor` mirati;
3. riusare mappature ancora valide;
4. aggregare input nello stesso contesto stabile;
5. ridurre checkpoint ridondanti, mai quello prima di un effetto esterno o finale.

## Prove isolate

Classifica ogni step come `read_only`, `reversible`, `external_side_effect` o
`destructive`. Puoi provare autonomamente soltanto step `read_only`; prova quelli
`reversible` solo con rollback certo. Per email, pagamenti, pubblicazioni,
aggiornamenti gestionali, cancellazioni e altri effetti reali usa una bozza, un
ambiente test o una simulazione e fermati prima dell'azione finale. Non inventare
destinatari o dati di produzione.

Ogni prova crea una run `optimization` con tempi per step e indica chiaramente se
è simulata. Confronta il candidato con la baseline usando lo stesso criterio di
successo. Accetta una modifica solo se il risultato è verificato, non aumenta i
retry e produce un miglioramento significativo o una semplificazione dimostrabile.

## Aggiornamento

Aggiorna istruzioni, flow e lezioni interessate; incrementa la versione della
procedura, aggiungi una nota in `CHANGELOG.md` con baseline, nuovo tempo e rischio,
e imposta `status: draft` se cambia il comportamento. Conserva run e incidenti
precedenti. Rigenera il dashboard e comunica cosa è stato provato, cosa è cambiato,
risparmio misurato e quali step non sono stati eseguiti per sicurezza.
