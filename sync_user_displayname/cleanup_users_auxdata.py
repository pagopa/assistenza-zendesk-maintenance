import json
import os
import time
from urllib.parse import urlencode

import requests

ZD_USER = os.getenv("Z_USER")
API_TOKEN = os.getenv("Z_API_TOKEN")


def chunks(lst, n):
    # Yield successive n-sized chunks from lst
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def make_request_get(url: str):
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, auth=(ZD_USER, API_TOKEN), headers=headers)
    if response.status_code != 200:
        print("ERR " + str(response.status_code) + " " + response.reason)
        exit(1)
    return response.json()


def check_export_rate_limit():
    global export_rate_limit_count
    if export_rate_limit_count == 100:
        print("!!! reached export rate limit (100 reqs per minute) --> delaying 60s...")
        time.sleep(60)
        export_rate_limit_count = 0


def check_job_rate_limit():
    global job_rate_limit_count
    if job_rate_limit_count == 30:
        print("!!! reached job rate limit (30 queued jobs at once) --> delaying 60s...")
        time.sleep(60)
        job_rate_limit_count = 0


# ENTRY

query = "aux_data:* role:end-user"
request_url = "https://pagopa.zendesk.com/api/v2/search/export.json?" + urlencode(
    {"filter[type]": "user", "page[size]": 100, "query": query}
)

# Step 1: Query with filter

# Fetch the initial page of data
data = make_request_get(request_url)
export_rate_limit_count = 1
users_count = 0
all_users = []

while request_url:
    users_count += len(data["results"])
    for user in data["results"]:
        all_users.append(user["id"])

    print("Fetched users: " + str(users_count))

    if data["meta"]["has_more"]:
        request_url = data["links"]["next"]
        check_export_rate_limit()
        data = make_request_get(request_url)
        export_rate_limit_count += 1
    else:
        request_url = ""

print("\nTotal users to be updated: " + str(users_count))

# Step 2: Bulk update

job_rate_limit_count = 0
headers = {"Content-Type": "application/json"}

for users in list(chunks(all_users, 100)):

    check_job_rate_limit()

    users_str = [str(item) for item in users]
    current_chunk = ",".join(users_str)
    update_many_params = {"ids": current_chunk}
    update_many_url = (
        "https://pagopa.zendesk.com/api/v2/users/update_many.json?"
        + urlencode(update_many_params)
    )
    json_data = {"user": {"user_fields": {"aux_data": None, "log_data": None}}}
    payload = json.dumps(json_data)

    response = requests.put(
        update_many_url, data=payload, auth=(ZD_USER, API_TOKEN), headers=headers
    )
    resp_data = response.json()
    print("\nJob issued: " + update_many_url)
    print("*** " + resp_data["job_status"]["url"])
    job_rate_limit_count += 1
