---
name: avvia-procedura
description: Esegue per nome una procedura aziendale già creata usando Windows-MCP. Usala quando l'utente chiede di avviare, eseguire o completare una procedura catalogata.
---

# Avvia procedura

Trova la procedura per nome o slug sotto `%USERPROFILE%\Documents\Agentic AI Operator System\procedure`. Leggi prima `procedure.json` e il suo `SKILL.md`; carica riferimenti ed eccezioni solo quando diventano rilevanti. Avvisa se lo stato non è `validated` o `active` e chiedi conferma prima di eseguire una bozza.

Usa esclusivamente `windows-mcp` per il desktop. Ottimizza l'esecuzione:

- prima di digitare o cliccare, assicurati che applicazione, finestra, vista e controllo di destinazione siano quelli previsti; quando cambi contesto, usa un'azione esplicita che sostituisca eventuale contenuto precedente;
- pilota normalmente l'interfaccia dell'applicazione e non aprire terminali o shell come scorciatoia, salvo che siano parte della procedura o un fallback necessario e appropriato dopo verifica;
- azioni meccaniche, scorciatoie, input completi e batch prima del ragionamento visuale;
- un singolo checkpoint per una sequenza deterministica senza bivi;
- `Screenshot` per osservazione veloce e verifica; `Snapshot` solo quando serve identificare controlli, testo, DOM o rimappare una schermata cambiata;
- riusa label, finestra e mappatura finché lo stato resta coerente;
- checkpoint immediati per condizioni, errori, conferme, invii e risultati finali;
- non caricare screenshot storici durante il percorso normale se le istruzioni testuali sono sufficienti;
- massimo due tentativi correttivi basati su stato fresco;
- il risparmio di token non giustifica mai un'azione ambigua, un contesto non verificato o un workaround più fragile dell'interazione diretta.

Raccogli gli input necessari, esegui, verifica il risultato finale e salva un report compatto in `runs\`. Non affermare mai un risultato non osservato.
