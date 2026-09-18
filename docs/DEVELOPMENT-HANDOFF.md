# Continuare lo sviluppo su un altro PC

Lo ZIP completo contiene sorgenti AIOS, backend PHP, dashboard, skill, plugin
Setup pubblicato, test, documentazione, installer e payload binari. Include anche
Windows MCP dal checkout upstream e OpenSteps v0.1.0 dal commit
`59def45d2d5ea3da98d4883eee4ac99a53e0efd7`, con le rispettive licenze.
`SOURCE-MANIFEST.json` identifica il commit AIOS e contiene hash e dimensione di
ogni file. Non contiene credenziali, database licenze, procedure personali,
ambienti virtuali, cache, vecchi ZIP o risultati di installazioni locali.

## Mappa

- `atpa-v1/`: runtime attuale 2.6.0, runner deterministico, licenze, dashboard,
  plugin operativo, template e payload necessari all'installer.
- `license-server/`: backend PHP 7.4+, pannello, API, esempi di configurazione e
  pagine pubblicate in `legal/`.
- `marketplace/agentic-ai-operator-system-setup/`: plugin pubblico Setup 1.0.0.
- `src/winbridge/`, `plugin/`, `installer/`: motore e installer legacy.
- `windows-mcp-package/upstream/`: sorgenti del componente Windows MCP.
- `third-party/opensteps/`: sorgenti del registratore, inclusi nello ZIP export.
- `tests/`, `docs/`, `tools/`, script `Build-*.ps1`: test, istruzioni e build.

## Ambiente Windows

Servono Git + Git LFS, Python 3.12 e PowerShell. Per il backend: PHP con sodium
e json. Per modificare/compilare OpenSteps: .NET 8 SDK Windows Desktop.
Non copiare una `.venv` da un altro PC: ricrearla.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest tests/test_configure.py tests/test_controller.py
py -3.12 -m venv .venv-runtime
.venv-runtime\Scripts\python -m pip install -r atpa-v1/runtime/dependencies.txt pytest
.venv-runtime\Scripts\python -m pytest tests/test_licensing_client.py tests/test_procedure_runner.py tests/test_dashboard_data.py tests/test_experience_runtime.py
php tests/license-server-test.php
php tests/delivery-message-test.php
```

I test desktop richiedono Windows e le dipendenze locali. Non eseguire procedure
di produzione o installer per verificare semplicemente che il progetto si apra.
I due ambienti sono separati perché il motore legacy e il runtime corrente
richiedono versioni differenti del pacchetto MCP.

## Git e aggiornamenti

Lo ZIP è uno snapshot senza `.git`. Per continuare con la cronologia:

```powershell
git clone https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system.git
cd agentic-ai-operator-system
git lfs pull
```

Il checkout annidato Windows MCP storico non dispone di `.gitmodules`: nello
ZIP i file sono già inclusi. In un clone nuovo, inizializzarlo manualmente solo
se la directory è vuota:

```powershell
git clone https://github.com/CursorTouch/Windows-MCP.git windows-mcp-package/upstream
git -C windows-mcp-package/upstream checkout 30c1472f807eefa44774a2fe23a5b10502a59f23
```

## Build

- Sistema Windows: `./Build-SystemRelease.ps1 -Version NUOVA_VERSIONE_SEMVER`.
  Aggiorna anche `release-manifest.json`: non ricompilare/sovrascrivere una
  release già pubblicata senza un nuovo numero di versione e verifica hash.
- Setup marketplace: `./tools/Build-SetupPlugin.ps1`.
- Export sviluppo: `./tools/Build-SourceArchive.ps1 -OutputPath C:\percorso\AIOS-Source.zip`.
  Richiede un clone Git e il checkout upstream, non il solo ZIP estratto.
- OpenSteps: nella sua directory, `dotnet build OpenSteps.sln` e
  `dotnet test OpenSteps.sln`.

## Configurazioni riservate

Il server Aruba esistente non è stato copiato o modificato per questo export.
Per un ambiente di sviluppo separato seguire `license-server/README.md`, usando
nuove chiavi e dati di prova. Non rigenerare le chiavi del server di produzione:
invaliderebbe la compatibilità con i client esistenti. Per trasferire la gestione
della produzione recuperare configurazione e database tramite un backup privato
cifrato, mai tramite GitHub o chat.

`Build-LicenseServerPackage.ps1` è un pacchetto di deploy PRIVATO: include il
provisioning e non deve essere pubblicato. Lo ZIP sorgenti usa invece una lista
di file Git e include solo gli esempi innocui di `license-server/private/`.

La pubblicazione del plugin e i link privacy/termini sono documentati in
`docs/marketplace-submission.md`. Gli account GitHub, Aruba e OpenAI vanno
autenticati separatamente sul nuovo PC; nessuna sessione è inclusa nello ZIP.
