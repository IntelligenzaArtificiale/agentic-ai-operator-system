# Server licenze AIOS

Requisiti: PHP 7.4+, HTTPS, estensioni `sodium` e `json`. Caricare il contenuto di questa cartella in una directory web dedicata, verificando che `private/` non sia raggiungibile via HTTP. La compatibilità PHP 7.4 è prevista per hosting legacy; per nuove installazioni è preferibile una versione PHP ancora supportata dal fornitore.

1. Esegui una sola volta `tools/generate-license-provisioning.py`: crea il file ignorato `private/provisioning.php` e restituisce la chiave pubblica da incorporare nel client prima della build.
2. Prima dell’upload genera localmente un token casuale di almeno 32 caratteri e salvalo come `private/setup-token.txt`; non condividerlo in chat.
3. Aprire una sola volta `https://dominio/percorso/setup.php`, inserire il token e impostare una password amministratore lunga. Token e provisioning vengono cancellati automaticamente.
4. Eliminare `setup.php` dal server.
5. Aprire `index.php`, accedere e creare la prima licenza.
6. Verificare che una richiesta diretta a `private/config.php` e `private/license.json` restituisca `403` o `404`.
7. Conservare un backup cifrato della cartella `private/`. Senza la chiave Ed25519, le concessioni firmate non sono recuperabili.

Il server non salva mai le chiavi di licenza in chiaro. La chiave appena creata viene mostrata una volta sola. L’API pubblica accetta soltanto `POST` JSON e applica limiti per IP e azione.

Su Nginx la regola `.htaccess` non viene letta: configurare esplicitamente il diniego HTTP per `/private/` prima della messa online.
