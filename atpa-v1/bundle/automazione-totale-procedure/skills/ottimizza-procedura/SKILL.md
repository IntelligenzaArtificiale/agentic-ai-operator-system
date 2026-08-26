---
name: ottimizza-procedura
description: Analizza telemetria, errori e lezioni di una procedura aziendale, prova in sicurezza i soli step isolabili e aggiorna la procedura per ridurne i tempi senza effetti produttivi. Usala quando l'utente chiede di velocizzare o ottimizzare una procedura esistente.
---

# Ottimizza procedura

Risolvi la procedura sotto `%USERPROFILE%\Documents\Agentic AI Operator System\procedure` e leggi `procedure.json`, `execution-plan.json`, `SKILL.md`, gli schemi, tutte le run valide e `experience\lessons.json`. Usa gli incidenti grezzi soltanto per approfondire anomalie già individuate. Una run è valida per una baseline soltanto se ha `outcome: succeeded`, `verification_status: verified` e prove coerenti con i criteri di successo.

## Analisi

Calcola per procedura e step almeno numero di campioni, tasso di successo, mediana,
minimo e massimo. Segnala come candidati gli step che hanno durata molto superiore
alla propria mediana, retry frequenti, osservazioni complete ripetute o attese
fisse sostituibili con condizioni. Con meno di tre campioni formula ipotesi, non
conclusioni statistiche.

Ottimizza la topologia completa, incluso stato iniziale e strategia di apertura,
non soltanto la velocità dei click. Separa tempo di azione, attesa, osservazione IA,
verifica e recupero. Priorità:

1. eliminare errori ricorrenti applicando lezioni contestuali;
2. sostituire attese fisse con `WaitFor` mirati;
3. eliminare osservazioni IA da passaggi meccanici stabili;
4. riusare mappature protette da fingerprint e guardie;
5. aggregare input nello stesso contesto stabile;
6. ridurre checkpoint ridondanti, mai quelli richiesti dal rischio o finali.

## Prove isolate

Classifica ogni step per executor (`deterministic` o `ai`) e side effect (`none`,
`reversible`, `external` o `destructive`). Puoi provare autonomamente solo effetti
`none`; prova i `reversible` con rollback certo. Per effetti reali usa ambiente test
o simulazione e fermati prima dell'azione finale. Non inventare dati di produzione.

Ogni prova crea una run `optimization` con tempi per step e indica chiaramente se
è simulata. Una simulazione non è confrontabile numericamente con una run reale e
non può produrre percentuali di miglioramento. Confronta il candidato con la
baseline usando lo stesso criterio di successo e lo stesso livello di effetto.
Confronta strategie partendo dallo stesso stato controllato. Accetta una modifica solo se il risultato è verificato con prova persistente, non
aumenta i retry e produce un miglioramento significativo o una semplificazione
dimostrabile. Se la verifica è dubbia, marca `unverified` e scarta il campione.

## Aggiornamento

Aggiorna istruzioni, flow, lezioni ed `execution-plan.json`; incrementa la versione della
procedura, aggiungi una nota in `CHANGELOG.md` con baseline, nuovo tempo e rischio,
e imposta `status: draft` se cambia il comportamento. Conserva run e incidenti
precedenti. Rigenera il dashboard e comunica cosa è stato provato, cosa è cambiato,
risparmio misurato e quali step non sono stati eseguiti per sicurezza.

Promuovi il piano a `compiled` solo dopo almeno tre esecuzioni pulite, verificate,
senza recuperi, stesso fingerprint iniziale e variabilità entro soglia. Le
coordinate prive di guardie non sono compilabili. Una deviazione successiva porta
il piano a `degraded` e riattiva l'IA soltanto per la porzione da riapprendere.
