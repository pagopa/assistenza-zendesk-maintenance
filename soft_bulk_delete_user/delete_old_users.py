import os
import time
from datetime import datetime
from urllib.parse import urlencode

import requests

USER = os.getenv("Z_USER")
API_TOKEN = os.getenv("Z_API_TOKEN")


def make_request(url: str):
    response = requests.get(url, auth=(USER, API_TOKEN))
    if response.status_code != 200:
        print("ERROR: status_code = " + str(response.status_code) + " " + response.text)
        exit(1)
    return response.json()


def make_delete_request(url: str):
    response = requests.delete(url, auth=(USER, API_TOKEN))
    if response.status_code == 429:
        print("\nToo Many Requests! Wait for 10 minutes and retry...\n")
        time.sleep(600)
        response = requests.delete(url, auth=(USER, API_TOKEN))
    elif response.status_code != 200:
        print("ERROR: status_code = " + str(response.status_code) + " " + response.text)
        exit(1)
    return response.json()


def chunks(lst, n):
    # Yield successive n-sized chunks from lst
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def check_search_rate_limit():
    global search_rate_limit_count
    if search_rate_limit_count == 100:
        print(
            "!!! reached search rate limit (10000 requests per minute) --> delaying 300s..."
        )
        # According to Zendesk docs, 60 seconds should be enough, even if we wait for 5 mins...
        time.sleep(300)
        search_rate_limit_count = 0


def check_job_rate_limit():
    global job_rate_limit_count
    if job_rate_limit_count == 30:
        print(
            "!!! reached job rate limit (30 queued/running jobs at once) --> delaying 60s..."
        )
        time.sleep(60)
        job_rate_limit_count = 0


def get_monthly_timeframe(month):
    match month:
        case 1:
            return "created<=2022-02-28"
        case 2:
            return "created<=2022-04-30 created>=2022-03-01"
        case 3:
            return "created<=2022-06-30 created>=2022-05-01"
        case 4:
            return "created<=2022-08-31 created>=2022-07-01"
        case 5:
            return "created<=2022-10-31 created>=2022-09-01"
        case 6:
            return "created<=2022-12-31 created>=2022-11-01"
        case 7:
            return "created<=2023-01-31 created>=2023-01-01"
        case 8:
            return "created<=2023-02-28 created>=2023-02-01"
        case 9:
            return "created<=2023-03-31 created>=2023-03-01"
        case 10:
            return "created<=2023-04-30 created>=2023-04-01"
        case 11:
            return "created<=2023-05-31 created>=2023-05-01"
        case 12:
            return "created<=2023-06-30 created>=2023-06-01"
        case 13:
            return "created<=2023-07-31 created>=2023-07-01"
        case 14:
            return "created<=2023-08-31 created>=2023-08-01"
        case 15:
            return "created<=2023-09-30 created>=2023-09-01"
        case 16:
            return "created<=2023-10-31 created>=2023-10-01"
        case 17:
            return "created<=2023-11-30 created>=2023-11-01"
        case 18:
            return "created<=2023-12-31 created>=2023-12-01"
        case 19:
            return "created<=2024-01-31 created>=2024-01-01"
        case 20:
            return "created<=2024-02-29 created>=2024-02-01"
        case 21:
            return "created<=2024-03-31 created>=2024-03-01"
        case 22:
            return "created<=2024-04-30 created>=2024-04-01"
        case 23:
            return "created<=2024-05-31 created>=2024-05-01"
        case 24:
            return "created<=2024-06-30 created>=2024-06-01"
        case 25:
            return "created<=2024-07-31 created>=2024-07-01"
        case 26:
            return "created<=2024-08-31 created>=2024-08-01"
        case 27:
            return "created<=2024-09-30 created>=2024-09-01"
        case 28:
            return "created<=2024-10-31 created>=2024-10-01"
        case 29:
            return "created<=2024-11-30 created>=2024-11-01"
        case 30:
            # This timeframe will be unreachable until Jan 2026!
            return "created<=2024-12-31 created>=2024-12-01"


#########
# ENTRY #
#########

print("START TIME: " + str(datetime.now()))

# build the query with a timeframe spanning two-by-two months in 2022, or
#  month-by-month in 2023; for 2024, each month is selected by cycling into
#  the interval [1, current month-1]
month_n = datetime.today().day

if month_n > 18:
    month_n_limiter = month_n % datetime.today().month
    month_n = 18 + month_n_limiter

timeframe = get_monthly_timeframe(month_n)
search_params = {
    "query": "role:end-user -tags:created_for_side_conversation " + timeframe,
    "page[size]": 100,
    "filter[type]": "user",
}
search_url = "https://pagopa.zendesk.com/api/v2/search/export.json?" + urlencode(
    search_params
)
print("Selected month: " + str(month_n))
print("Working on timeframe: " + timeframe)

# STAGE 1: collect monthly generated users

# Fetch the initial page of data
data = make_request(search_url)

results_count = 0
search_rate_limit_count = 1
user_ids = []

while search_url:
    results_count += len(data["results"])
    print("Collecting search results... " + str(results_count))

    for user in data["results"]:
        user_ids.append(user["id"])

    if data["meta"]["has_more"]:
        search_url = data["links"]["next"]
        check_search_rate_limit()
        data = make_request(search_url)
        search_rate_limit_count += 1
    else:
        search_url = ""

print("# Users created: " + str(results_count))

# STAGE 2: narrow-down to users without a ticket

user_ids_selected = []
for user_id in user_ids:
    show_user_related_url = (
        "https://pagopa.zendesk.com/api/v2/users/" + str(user_id) + "/related.json"
    )

    for attempt_no in range(3):
        try:
            data = make_request(show_user_related_url)
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

job_rate_limit_count = 0
for users in list(chunks(user_ids_selected, 100)):

    check_job_rate_limit()

    users_str = [str(item) for item in users]
    current_chunk = ",".join(users_str)
    soft_destroy_params = {"ids": current_chunk}
    soft_destroy_url = (
        "https://pagopa.zendesk.com/api/v2/users/destroy_many.json?"
        + urlencode(soft_destroy_params)
    )

    data = make_delete_request(soft_destroy_url)
    print(" " + data["job_status"]["url"])
    job_rate_limit_count += 1

print("END TIME: " + str(datetime.now()))
