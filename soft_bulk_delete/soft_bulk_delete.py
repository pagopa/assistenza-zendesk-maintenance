import os, requests, datetime
from urllib.parse import urlencode

def chunks(lst, n):
    # Yield successive n-sized chunks from lst
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

### ENTRY ###

days_to_keep = 395 # 365+30 (one year + grace period)
user = os.getenv('Z_USER')
api_token = os.getenv('Z_API_TOKEN')

# Build a query to find tickets CLOSED more than 1 year ago

date_limit = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
date_limit_s = f"{date_limit:%Y-%m-%d}"
search_params = {
    'query': 'type:ticket status:closed updated<' + date_limit_s,
    'sort_by': 'updated_at',
    'sort_order': 'asc'
}
search_url = 'https://pagopa.zendesk.com/api/v2/search.json?' + urlencode(search_params)

ticket_ids = []
while search_url:
    response = requests.get(search_url, auth=(user, api_token))
    if response.status_code == 422:
        break
    elif response.status_code != 200:
        print('Status:', response.status_code, 'Problem with the request. Exiting.')
        exit(1)
    data = response.json()
    for result in data['results']:
        ticket_ids.append(result['id'])
    search_url = data['next_page']

print('Found ' + str(len(ticket_ids)) + ' tickets to be deleted (closed BEFORE ' + date_limit_s + ').')

for tickets in list(chunks(ticket_ids, 100)):
    tickets_str = [str(item) for item in tickets]
    current_chunk = ','.join(tickets_str)
    soft_destroy_params = {
        'ids': current_chunk
    }
    soft_destroy_url = 'https://pagopa.zendesk.com/api/v2/tickets/destroy_many.json?' + urlencode(soft_destroy_params)
    response = requests.delete(soft_destroy_url, auth=(user, api_token))
    data = response.json()
    print('\nJob issued: soft-deleting tickets # ' + current_chunk)
    print(data['job_status']['url'])

print('<soft_bulk_delete.py> - END')
