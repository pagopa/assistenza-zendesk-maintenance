import os
import time
from datetime import datetime
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


def get_monthly_timeframe(month):
    match month:
        case 1:
            return "created<=2022-01-31"
        case 2:
            return "created<=2022-02-28 created>=2022-02-01"
        case 3:
            return "created<=2022-03-31 created>=2022-03-01"
        case 4:
            return "created<=2022-04-30 created>=2022-04-01"
        case 5:
            return "created<=2022-05-31 created>=2022-05-01"
        case 6:
            return "created<=2022-06-30 created>=2022-06-01"
        case 7:
            return "created<=2022-07-31 created>=2022-07-01"
        case 8:
            return "created<=2022-08-31 created>=2022-08-01"
        case 9:
            return "created<=2022-09-30 created>=2022-09-01"
        case 10:
            return "created<=2022-10-31 created>=2022-10-01"
        case 11:
            return "created<=2022-11-30 created>=2022-11-01"
        case 12:
            return "created<=2022-12-31 created>=2022-12-01"
        case 13:
            return "created<=2023-01-31 created>=2023-01-01"
        case 14:
            return "created<=2023-02-28 created>=2023-02-01"
        case 15:
            return "created<=2023-03-31 created>=2023-03-01"
        case 16:
            return "created<=2023-04-30 created>=2023-04-01"
        case 17:
            return "created<=2023-05-31 created>=2023-05-01"
        case 18:
            return "created<=2023-06-30 created>=2023-06-01"
        case 19:
            return "created<=2023-07-31 created>=2023-07-01"
        case 20:
            return "created<=2023-08-31 created>=2023-08-01"
        case 21:
            return "created<=2023-09-30 created>=2023-09-01"
        case 22:
            return "created<=2023-10-31 created>=2023-10-01"
        case 23:
            return "created<=2023-11-30 created>=2023-11-01"
        case 24:
            return "created<=2023-12-31 created>=2023-12-01"
        case _:
            return "created>=2024-01-01"


#########
# ENTRY #
#########

user = os.getenv("Z_USER")
api_token = os.getenv("Z_API_TOKEN")
print("START TIME: " + str(datetime.now()))

# build the query with a timeframe limited to a single month of years 2022 & 2023;
#  since we're running this in 2024, we can select every month of 2022, at each run
#  for 2023: each month is selected by cycling into the interval [1, current month]
month_n = (datetime.today().day % 24) + 1

if month_n > 12:
    month_n_limiter = (month_n % datetime.today().month) + 1
    month_n = 12 + month_n_limiter

timeframe = get_monthly_timeframe(month_n)
search_params = {
    "role": "end-user",
    "query": "-tags:referente_tecnico -tags:operatore_tecnico -tags:acq_referente_tecnico -tags:acq_operatore_tecnico -tags:created_for_side_conversation "
    + timeframe,
    "sort_by": "updated_at",
    "sort_order": "asc",
}
search_url = "https://pagopa.zendesk.com/api/v2/users.json?" + urlencode(search_params)
print("Selected month: " + str(month_n))
print("Working on timeframe: " + timeframe)

# STAGE 1: collect monthly generated users

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

print("# Users created: " + str(data["count"]))

# STAGE 2: narrow-down to users without a ticket

user_ids_selected = []
for user_id in user_ids:
    show_user_related_url = (
        "https://pagopa.zendesk.com/api/v2/users/" + str(user_id) + "/related.json"
    )

    for attempt_no in range(3):
        try:
            response = requests.get(show_user_related_url, auth=(user, api_token))
            data = response.json()
            requested_tickets = data["user_related"]["requested_tickets"]
            if requested_tickets == 0:
                user_ids_selected.append(user_id)
                print(user_id, end=" ")
            break
        except Exception as e:
            print(e)
            print("\nWait for 10 minutes and retry...\n")
            time.sleep(600)

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
