import os
import time
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

import requests


def chunks(lst, n):
    # Yield successive n-sized chunks from lst
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def check_rate_limit():
    global rate_limit_count
    if rate_limit_count == 30:
        print("!!! reached rate limit --> wait for 1 minute...")
        time.sleep(60)
        rate_limit_count = 0


#########
# ENTRY #
#########

# run this script on even days of the week only
today = datetime.today()
today_n = today.isoweekday()
if today_n % 2 == 1:
    print("Weekday number is odd: skipping old users maintenance")
    exit(0)

user = os.getenv("Z_USER")
api_token = os.getenv("Z_API_TOKEN")
print("START TIME: " + str(datetime.now()))

# Work Date Range = (0, 13 months ago)
end_date = date(today.year, today.month, today.day) - timedelta(365 + 30)

end_date_str = end_date.strftime("%Y-%m-%d")
search_params = {
    "role": "end-user",
    "query": "-tags:referente_tecnico -tags:operatore_tecnico -tags:acq_referente_tecnico -tags:acq_operatore_tecnico -tags:created_for_side_conversation created<"
    + end_date_str,
    "sort_by": "updated_at",
    "sort_order": "asc",
}
search_url = "https://pagopa.zendesk.com/api/v2/users.json?" + urlencode(
    search_params
)

# STAGE 1: collect users created 13 months ago or earlier

user_ids = []
while search_url:

    response = requests.get(search_url, auth=(user, api_token))
    if response.status_code != 200:
        print(
            "ERROR: status_code = "
            + str(response.status_code)
            + " Reason: "
            + response.reason
        )
        exit(1)

    data = response.json()
    for result in data["users"]:
        user_ids.append(result["id"])
    search_url = data["next_page"]

print("# Users created before " + end_date_str + ": " + str(data["count"]))

# STAGE 2: narrow-down to users without a ticket

user_ids_selected = []
for user_id in user_ids:

    show_user_related_url = (
        "https://pagopa.zendesk.com/api/v2/users/"
        + str(user_id)
        + "/related.json"
    )
    response = requests.get(show_user_related_url, auth=(user, api_token))
    if response.status_code != 200:
        print(
            "ERROR: status_code = "
            + str(response.status_code)
            + " Reason: "
            + response.reason
        )
        exit(1)

    data = response.json()
    requested_tickets = data["user_related"]["requested_tickets"]
    if requested_tickets == 0:
        user_ids_selected.append(user_id)
        print(user_id, end=" ")

print("\n# To be deleted: " + str(len(user_ids_selected)))

# STAGE 3: bulk delete

rate_limit_count = 0
for users in list(chunks(user_ids_selected, 100)):

    check_rate_limit()
    users_str = [str(item) for item in users]
    current_chunk = ",".join(users_str)
    soft_destroy_params = {"ids": current_chunk}
    soft_destroy_url = (
        "https://pagopa.zendesk.com/api/v2/users/destroy_many.json?"
        + urlencode(soft_destroy_params)
    )
    response = requests.delete(soft_destroy_url, auth=(user, api_token))

    if response.status_code == 429:
        print("\nToo Many Requests! Wait for 10 minutes and retry...\n")
        time.sleep(600)
        response = requests.delete(soft_destroy_url, auth=(user, api_token))
    elif response.status_code != 200:
        print(
            "ERROR: status_code = "
            + str(response.status_code)
            + " Reason: "
            + response.reason
        )
        exit(1)

    data = response.json()
    print(" " + data["job_status"]["url"])
    rate_limit_count += 1

print("END TIME: " + str(datetime.now()))
