import os
import time
from datetime import date, datetime, timedelta
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


#########
# ENTRY #
#########

print("START TIME: " + str(datetime.now()))

# working date = YESTERDAY
today = datetime.today()
working_date = date(today.year, today.month, today.day) - timedelta(1)
working_date_str = working_date.strftime("%Y-%m-%d")

search_params = {
    "query": "role:end-user -tags:created_for_side_conversation created:"
    + working_date_str,
    "page[size]": 100,
    "filter[type]": "user",
}
search_url = "https://pagopa.zendesk.com/api/v2/search/export.json?" + urlencode(
    search_params
)

# STAGE 1: collect users created on day x

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

print("# Users created on " + working_date_str + ": " + str(results_count))

# STAGE 2: narrow-down to users without a ticket

user_ids_selected = []
for user_id in user_ids:

    show_user_related_url = (
        "https://pagopa.zendesk.com/api/v2/users/" + str(user_id) + "/related.json"
    )

    data = make_request(show_user_related_url)
    requested_tickets = data["user_related"]["requested_tickets"]
    if requested_tickets == 0:
        user_ids_selected.append(user_id)
        print(user_id, end=" ")

print("\n # To be deleted: " + str(len(user_ids_selected)))

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
