---
name: modifica-procedura
description: Aggiorna una procedura aziendale e il relativo SKILL.md, schema, riferimenti e catalogo. Usala quando l'utente indica una procedura esistente e le modifiche desiderate.
---

# Modifica procedura

Risolvi la procedura sotto `%USERPROFILE%\Documents\Agentic AI Operator System\procedure` e leggi `procedure.json`, `SKILL.md`, `experience\lessons.json` e soltanto i riferimenti coinvolti. Conserva run e incidenti storici; se cambi step o selettori, aggiorna esplicitamente l'ambito delle lezioni interessate senza cancellare l'evidenza originale.

1. Applica la richiesta coerentemente a istruzioni, flow, input, condizioni, test e screenshot di riferimento.
2. Non alterare `recording\`, che conserva la fonte originale. Aggiungi nuove registrazioni come sottocartelle datate.
3. Incrementa la versione: patch per correzioni, minor per nuovi passaggi/bivi/input, major per cambiamenti incompatibili.
4. Imposta `status` a `draft` quando la modifica cambia comportamento o criteri di successo; conserva `validated` solo per correzioni editoriali prive di effetti operativi.
5. Mantieni il protocollo di efficienza adattiva: contesto destinatario certo prima dell'azione, interazione diretta con l'applicazione, batch solo nello stesso stato stabile, checkpoint significativi, `Screenshot` leggero e `Snapshot` selettivo. Non introdurre workaround da terminale per un risparmio marginale.
6. Aggiorna `updated_at`, aggiungi una nota in `CHANGELOG.md`, valida struttura e JSON e rigenera il dashboard.

Comunica cosa è cambiato e se è necessario un nuovo collaudo. Non eseguire automaticamente la procedura salvo richiesta esplicita separata.
