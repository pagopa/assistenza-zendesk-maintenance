# assistenza-zendesk-maintenance

Contiene vari script e altro codice legato esclusivamente alle attività di manutenzione della piattaforma Zendesk o funzioni di supporto alla stessa. Il repository, pur essendo singolo, è stato pensato per ospitare pipeline multiple su Azure DevOps.

## sync_user_displayname

Uno script python schedulato 1 volta al giorno (0:15 AM [UTC]) per l'allineamento delle etichette degli utenti finali (display names) con la porzione sinistra delle rispettive email. Il display name originario viene preservato solo se il similarity score (tra display name attuale e email) supera il 70%.

## soft_bulk_delete (DEPRECATED)

Un unico script Python schedulato 4 volte al giorno (0:00 AM, 6:00 AM, 12:00 PM, and 18:00 PM [UTC]) per la cancellazione dei ticket chiusi da oltre 365 giorni. La schedulazione di questo job è stata disattivata in data 6-nov-2024 per sostituzione con analoga funzionalità offerta direttamente dalla piattaforma Zendesk.

## soft_bulk_delete_user (DEPRECATED)

Una collezione di script Python schedulati almeno una 1 volta al giorno (eg. 1:00 AM [UTC]) per la cancellazione: (a) dei nuovi profili utente creati nella giornata precedente, ai quali non è associato alcun ticket; (b) dei profili utente creati oltre 13 mesi addietro, ai quali non è associato alcun ticket.

La schedulazione di questo job è stata disattivata in data 10-feb-2025 per sostituzione con analoga funzionalità offerta direttamente dalla piattaforma Zendesk.

## sso (DEPRECATED)

Una WebApp che funge da endpoint per intercettare gli accessi di utenti non ancora autenticati ai vari Help Center di PagoPA. L'unico scopo di questa app è quello di redirezionare l'utente sulle homepage delle varie iniziative, in base alla URL su cui si è tentato di atterrare.

La funzionalità è stata spostata su piattaforma AWS.