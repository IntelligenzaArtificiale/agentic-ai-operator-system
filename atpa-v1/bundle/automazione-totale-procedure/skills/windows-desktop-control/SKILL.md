---
name: windows-desktop-control
description: Controlla applicazioni e desktop Windows attraverso Windows-MCP con osservazione e verifica adattive. Usala per qualsiasi interazione richiesta con programmi Windows.
---

# Controllo Windows efficiente

Usa gli strumenti nativi `windows-mcp` per l'intero flusso. Non passare a Browser, Chrome, Computer Use o script di mouse se Windows-MCP è disponibile.

Prima di ogni gruppo di azioni, rendi certo il contesto destinatario: applicazione e finestra corrette, vista o documento corretto e controllo pronto a ricevere input. Non assumere che il focus o il contenuto precedente siano quelli desiderati. Quando si cambia destinazione, usa un'azione esplicita e idempotente che sostituisca lo stato precedente invece di concatenarsi accidentalmente ad esso.

Usa normalmente l'interfaccia dell'applicazione tramite Windows-MCP. Per aprire o controllare un programma non avviare terminali, PowerShell, prompt dei comandi o script come workaround, salvo richiesta dell'utente, necessità intrinseca della procedura o indisponibilità dell'interfaccia dopo verifica. Non usare la shell soltanto perché sembra ridurre una chiamata.

Ottimizza solo dopo aver preservato correttezza: raggruppa azioni deterministiche nello stesso contesto stabile; `Screenshot` per contesto e checkpoint; `Snapshot` solo per struttura UI, label, DOM o rimappatura. Se il costo di un controllo è inferiore al rischio di agire sul bersaglio sbagliato, controlla. Verifica dopo gruppi coerenti e subito nei bivi o nelle azioni critiche. Un tool riuscito non prova che lo stato sia cambiato. Verifica sempre il risultato finale e limita a due i tentativi correttivi basati su stato fresco.

Per le procedure catalogate, usa le skill centrali invece di improvvisare il flusso.
