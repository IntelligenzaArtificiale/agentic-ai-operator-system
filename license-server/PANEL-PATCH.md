# Aggiornamento messaggio di installazione — 2.5.2

Prima fai una copia dei due file interessati, se presenti.
Carica `templates/admin.php` e `src/DeliveryMessage.php` nelle rispettive cartelle
di `/ai-os/` sul tuo hosting. Il secondo file è nuovo.

Non toccare `private/`, `config.php`, `license.json`, le chiavi di firma o i dati
delle licenze. Non serve eseguire nuovamente setup.php.

Il messaggio da inviare al cliente ora separa la chiave personale dal prompt da
incollare in chat. Il cliente inserisce la chiave soltanto nella finestra locale
aperta dall'icona Desktop. L'installer non apre finestre automaticamente.

Questa patch modifica le istruzioni di consegna, non il protocollo API.
Gli interventi sul client Windows sono contenuti nello ZIP Windows 2.5.2.
