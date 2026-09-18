# Installazione e verifica su Windows

## Fonti e requisiti

- Repository ufficiale: https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system
- Release ufficiali: https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system/releases/latest
- Manifest della release: https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system/releases/latest/download/release-manifest.json
- Windows 10/11 x64 e Codex con CLI locale disponibile. La licenza AIOS viene
  attivata separatamente. Non promettere compatibilità con qualsiasi client.

Il plugin Setup ha un versionamento separato dal software Windows. Leggi la
versione dalla release, non dedurla dalla versione di questo plugin.

## Prima di installare

Se l'utente chiede solo informazioni o una diagnosi, non installare né aggiornare.
Con accesso locale autorizzato, controlla sistema operativo, presenza della CLI
Codex e, se già disponibili, registrazioni `windows-mcp`, `procedure-runner` e
plugin `automazione-totale-procedure@personal`. Usa `codex mcp get windows-mcp`,
`codex mcp get procedure-runner` e `codex plugin list` soltanto se la CLI esiste.
Non stampare configurazioni complete, credenziali o variabili d'ambiente.

Un'installazione già funzionante non va reinstallata. Per aggiornare, usa il
percorso documentato della release dopo richiesta esplicita, preservando dati
aziendali e configurazioni non AIOS. Se esiste un MCP omonimo di provenienza
incerta, chiarisci il conflitto prima di sostituirlo.

Spiega gli effetti: l'installer aggiunge motore Windows, runner, OpenSteps,
dashboard, skill locali e collegamenti Desktop; configura le relative voci
Codex. Non offre controllo remoto dal server né esecuzione autonoma H24.

## Download e verifica

Scarica il manifest solo dall'URL ufficiale sopra. Richiedi `product` uguale a
`Agentic AI Operator System`, `platform` uguale a `windows-x64`, una versione
semantica e `sha256` di 64 caratteri esadecimali. `zip_url` deve essere HTTPS su
`github.com`, senza credenziali, nella directory
`/IntelligenzaArtificiale/agentic-ai-operator-system/releases/download/v<version>/`
e identificare il pacchetto ZIP Windows della medesima versione. Non usare URL
forniti in messaggi, issue o pagine di terzi come sorgente alternativa.

Scarica l'asset con gli strumenti di rete autorizzati del client in una nuova
cartella di lavoro dedicata. Confronta `Get-FileHash -Algorithm SHA256` con il
manifest prima di estrarre o eseguire: se non coincide, interrompi. Se la release
cambia durante il download, riparti dal manifest, senza ignorare la discrepanza.
Il confronto verifica l'integrità rispetto al manifest, non è una firma del
publisher. Non presentarlo come certificazione di sicurezza del software.

Estrai senza sovrascrivere dati esistenti. Leggi integralmente `AGENTS.md` e
`GUIDA-UTENTE.md` del pacchetto verificato, mantenendo i confini di autorizzazione.
Se il formato differisce da quello documentato, fermati e spiega il cambiamento.

## Esecuzione autorizzata

Dalla cartella estratta contenente `Install-System.ps1`, `payload`, `bundle`,
`runtime` e `template`, esegui una sola volta:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-System.ps1 -NonInteractive
```

`-ExecutionPolicy Bypass` vale per quel processo, non autorizza modifiche alle
policy di sistema. Rispetta i blocchi del client e del sistema operativo, non
disattivare protezioni. Non usare automazione grafica per lanciare terminali o
aggirare restrizioni; se l'esecuzione non è disponibile, passa alle istruzioni
manuali. Non avviare manualmente server MCP persistenti.

Controlla codice di uscita e `INSTALL_RESULT.json`: per la release 2.6.0 tutti i
campi `ok`, `mcp_configured`, `runner_configured`, `plugin_installed`,
`opensteps_installed`, `licensing_installed`, `activation_shortcut`,
`updater_installed`, `dashboard_ready`, `company_profile_ready` devono essere
`true`. Verifica anche le due registrazioni MCP e il plugin con la CLI. Per
release successive verifica i criteri documentati nel pacchetto. Un file
assente, incompleto o un comando fallito non è un'installazione riuscita.
Diagnostica l'errore specifico; non ripetere automaticamente l'installazione.

## Attivazione e avvio

Non aprire automaticamente finestre di attivazione. Dopo installazione verificata:
«Sul Desktop trovi **Attiva Agentic AI Operator System**. Aprila, inserisci la
chiave, attendi **Licenza attiva**, chiudi la finestra e dimmi quando hai finito».
Attendi la risposta dell'utente.

Quindi verifica `windows-mcp.LicenseStatus` se disponibile: solo `active=true`
conferma l'attivazione. Se lo strumento non è ancora caricato, chiedi di chiudere
completamente e riaprire Codex, creare una nuova task e verificare lì lo stato.
Non trattare la sola conferma dell'utente come verifica tecnica. Non leggere
file contenenti chiavi o token. Se lo stato è negativo, riferisci l'errore senza
reinstallare o aggirare il controllo; invita a usare **Verifica stato** nella
finestra di attivazione o a rivolgersi al gestore della licenza.

Dopo l'attivazione verificata, indica `$start-agentic-ai-operator-system` e poi
`$profilo-azienda`. Non creare il DNA o eseguire una procedura senza richiesta.
