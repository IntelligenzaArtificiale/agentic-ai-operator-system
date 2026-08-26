# Piano di esecuzione compilato

`execution-plan.json` separa il ragionamento dall'esecuzione meccanica. Non contiene
codice arbitrario: descrive blocchi dichiarativi eseguiti dal runner locale.

## Stati

- `exploratory`: l'IA osserva e scopre il percorso corretto;
- `stabilizing`: il percorso viene ripetuto e misurato;
- `compiled_candidate`: esiste un candidato deterministico ancora da confermare;
- `compiled`: i blocchi deterministici possono usare il runner locale;
- `degraded`: una guardia non coincide più e serve rimappatura.

La promozione a `compiled` richiede almeno tre run pulite, stesso stato iniziale,
risultato verificato, nessun recupero e variabilità entro la soglia indicata.

## Blocchi

Ogni blocco ha `id`, `executor` (`deterministic` o `ai`), `side_effect` (`none`,
`reversible`, `external` o `destructive`), `preconditions`, `actions`,
`postconditions` e `on_failure: return_to_ai`. Un blocco `ai` non contiene azioni.

Operazioni consentite: `app`, `click`, `type`, `multi_edit`, `shortcut`, `wait`,
`wait_for`. Le coordinate assolute sono ammesse solo con fingerprint ambientale e
guardie sufficienti; preferire scorciatoie, controlli semantici e ancore relative.
I valori dinamici usano slot `{{nome_variabile}}` dichiarati in `variables`.

Il runner esegue solo piani `compiled`. Un blocco cognitivo, un effetto esterno non
autorizzato o una guardia fallita interrompono il blocco e restituiscono controllo
all'IA senza proseguire alla cieca.
