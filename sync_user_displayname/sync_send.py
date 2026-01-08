import json
import os
import time
from difflib import SequenceMatcher
from urllib.parse import urlencode

import requests

ZD_USER = os.getenv("Z_USER")
API_TOKEN = os.getenv("Z_API_TOKEN")

headers = {"content-type": "application/json"}
ORG = "_users_hc_send"


def make_request(url: str):
    response = requests.get(url, auth=(ZD_USER, API_TOKEN))
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


def update_is_needed(s1: str, s2: str) -> bool:
    similarity_score = SequenceMatcher(None, s1.casefold(), s2.casefold()).ratio()
    return not (similarity_score > 0.5)


#########
# ENTRY #
#########

# Select end users from a specific org

search_params = {
    "query": 'role:end-user organization:"' + ORG + '"',
    "page[size]": 100,
    "filter[type]": "user",
}
search_url = "https://pagopa.zendesk.com/api/v2/search/export?" + urlencode(
    search_params
)

# Fetch the initial page of data
data = make_request(search_url)

export_rate_limit_count = 1
results_count = 0
updated_count = 0

while search_url:
    results_count += len(data["results"])
    print("Collecting search results... " + str(results_count))

    for u in data["results"]:
        u_id = str(u["id"])
        old_name = u["name"]
        email = u["email"]
        new_name = email.split("@")[0]
        print(u_id, end="")

        if not update_is_needed(old_name, new_name):
            print(" ... Skipping!")
            continue

        update_user_url = "https://pagopa.zendesk.com/api/v2/users/" + u_id + ".json"
        json_data = {"user": {"name": new_name}}
        payload = json.dumps(json_data)
        response = requests.put(
            update_user_url, data=payload, auth=(ZD_USER, API_TOKEN), headers=headers
        )
        if response.status_code != 200:
            print("ERR " + str(response.status_code) + " " + response.reason)
            exit(1)

        print(" ... OK")
        updated_count += 1
        time.sleep(2)

    if data["meta"]["has_more"]:
        search_url = data["links"]["next"]
        check_export_rate_limit()
        data = make_request(search_url)
        export_rate_limit_count += 1
    else:
        search_url = ""

print("# Total users found: " + str(results_count))
print(" of which: " + str(updated_count) + " updated.")
time.sleep(60)
