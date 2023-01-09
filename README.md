# assistenza-zendesk-maintenance

Contiene vari script e altro codice legato esclusivamente alle attività di manutenzione della piattaforma Zendesk o funzioni di supporto alla stessa. Il repo, pur essendo singolo, è stato pensato per ospitare pipeline multiple su Azure DevOps.

## soft_bulk_delete

E' un semplice script Python schedulato 4 volte al giorno (0:00 AM, 6:00 AM, 12:00 PM, and 18:00 PM [UTC]) per la cancellazione dei ticket chiusi da oltre 1 anno (+ 1 mese di grace period)

## sso

Una WebApp che funge da endpoint per l’autenticazione degli utenti finali dei soli brand che la prevedono. Per ciascuno di tali brand, il codice va personalizzato al fine di generare l’opportuno token JWT che viene infine passato a Zendesk per l’accesso al relativo Help Center (creazione e gestione diretta dei ticket da parte dell’utente finale).