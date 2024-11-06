# assistenza-zendesk-maintenance

Contiene vari script e altro codice legato esclusivamente alle attività di manutenzione della piattaforma Zendesk o funzioni di supporto alla stessa. Il repository, pur essendo singolo, è stato pensato per ospitare pipeline multiple su Azure DevOps.

## soft_bulk_delete (DEPRECATED)

Un unico script Python schedulato 4 volte al giorno (0:00 AM, 6:00 AM, 12:00 PM, and 18:00 PM [UTC]) per la cancellazione dei ticket chiusi da oltre 365 giorni. La schedulazione di questo job è stata disattivata in data 6-nov-2024 per sostituzione con analoga funzionalità offerta direttamente dalla piattaforma Zendesk.

## soft_bulk_delete_user

Una collezione di script Python schedulati almeno una 1 volta al giorno (eg. 1:00 AM [UTC]) per la cancellazione: (a) dei nuovi profili utente creati nella giornata precedente, ai quali non è associato alcun ticket; (b) dei profili utente creati oltre 13 mesi addietro, ai quali non è associato alcun ticket.

## sso

Una WebApp che funge da endpoint per intercettare gli accessi di utenti non ancora autenticati ai vari Help Center di PagoPA. L'unico scopo di questa app è quello di redirezionare l'utente sulle homepage delle varie iniziative, in base alla URL su cui si è tentato di atterrare.
