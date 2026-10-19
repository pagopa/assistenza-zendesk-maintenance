import json
import os
import time
from urllib.parse import urlencode

import requests

BTOK_URL = os.getenv("BTOK_URL")
CUSTOM_ZD_CODE = os.getenv("CUSTOM_ZD_CODE")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_SCOPE = os.getenv("CLIENT_SCOPE")


def chunks(lst, n):
    # Yield successive n-sized chunks from lst
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def make_request_get(url: str, headers: dict):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"ERROR: {response.status_code}/{response.text}/{response.reason}"
        )
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

# Step 0: Get an access token

response = requests.post(
    BTOK_URL,
    headers={"Custom-Zendesk-Code": CUSTOM_ZD_CODE},
    json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": CLIENT_SCOPE,
        "expires_in": 21600,  # 6 hours in seconds
    },
)
if response.status_code != 200:
    raise Exception(
        f"Failed to get access token: {response.status_code}/{response.text}/{response.reason}"
    )
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {response.text}",
}

# Step 1: Query with filter

query = "aux_data:* role:end-user"
request_url = "https://pagopa.zendesk.com/api/v2/search/export.json?" + urlencode(
    {"filter[type]": "user", "page[size]": 100, "query": query}
)

# Fetch the initial page of data
data = make_request_get(request_url, headers)
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
        data = make_request_get(request_url, headers)
        export_rate_limit_count += 1
    else:
        request_url = ""

print("\nTotal users to be updated: " + str(users_count))

# Step 2: Bulk update

job_rate_limit_count = 0

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

    response = requests.put(update_many_url, data=payload, headers=headers)
    resp_data = response.json()
    print("\nJob issued: " + update_many_url)
    print("*** " + resp_data["job_status"]["url"])
    job_rate_limit_count += 1
