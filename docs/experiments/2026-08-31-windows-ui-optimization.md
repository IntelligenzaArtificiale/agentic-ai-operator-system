# Esperimento Windows UI: transizioni e contenuto preesistente

Scenario di laboratorio autorizzato: invio a sé stessi tramite Gmail in Chrome.
Il caso applicativo serve solo come sonda; le decisioni sotto sono indipendenti
dall'applicazione.

## Esito osservato

- Baseline: il destinatario ha ridisposto il form; coordinate raccolte prima della
  transizione hanno indirizzato i campi successivi in modo errato. Il checkpoint
  pre-invio ha bloccato l'effetto, la bozza errata è stata eliminata e la run è
  stata recuperata da stato fresco.
- Candidato: deep-link allo stato iniziale, attesa condizionale, nuova fase dopo la
  selezione dinamica, inserimento del corpo ancorato all'inizio e una verifica
  pre-effetto. Invio riuscito al primo tentativo e prova persistente tramite ricerca
  del marker nel sistema di destinazione.
- Baseline verificata: circa 68,4 s di tempo tool fino alla prova persistente.
- Candidato verificato: circa 42,0 s, miglioramento osservato del 38,6%.
- Le osservazioni DOM complete hanno richiesto 5–9 s; le singole azioni 0,6–2 s.

## Decisioni generalizzate

1. Ogni azione che può ridisporre una UI crea un confine di fase.
2. Le coordinate non sopravvivono a un confine di fase senza nuova mappatura.
3. Ogni campo dichiara un contratto di contenuto: sostituzione, append o inserimento
   ancorato. Template e contenuto preesistente sono preservati per default.
4. L'osservazione IA resta nei bivi, nelle deviazioni e nei checkpoint di rischio;
   il percorso stabile usa azioni locali e attese condizionali.
5. Toast ed esito del tool non provano un effetto esterno: serve un artefatto
   persistente nel sistema di destinazione.

Il candidato resta `compiled_candidate`: una singola run pulita non basta per la
promozione automatica, che richiede almeno tre esecuzioni comparabili e verificate.
