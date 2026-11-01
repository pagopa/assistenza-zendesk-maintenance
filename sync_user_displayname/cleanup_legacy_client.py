import os
import sys
import time
from urllib.parse import urlencode

import requests

BTOK_URL = os.getenv("BTOK_URL")
CUSTOM_ZD_CODE = os.getenv("CUSTOM_ZD_CODE")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_SCOPE = os.getenv("CLIENT_SCOPE")


def make_request_get(url: str, headers: dict):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"ERROR: {response.status_code}/{response.text}/{response.reason}"
        )
    return response


def make_request_post(url: str, payload: dict, headers: dict):
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(
            f"ERROR: {response.status_code}/{response.text}/{response.reason}"
        )
    return response


def check_export_rate_limit():
    global export_rate_limit_count
    if export_rate_limit_count == 100:
        print("!!! reached export rate limit (100 reqs per minute) --> delaying 60s...")
        time.sleep(60)
        export_rate_limit_count = 0


def get_tokens(client_id: int, headers: dict):
    global export_rate_limit_count

    url = f"https://pagopa.zendesk.com/api/v2/oauth/tokens?" + urlencode(
        {"page[size]": 100, "client_id": client_id, "all": True}
    )
    # Fetch the initial page of data
    data = make_request_get(url, headers).json()

    export_rate_limit_count = 1
    items_count = 0
    all_items = []

    while url:
        items_count += len(data["tokens"])
        for item in data["tokens"]:
            all_items.append(item)

        print("Fetched items: " + str(items_count))

        if data["meta"]["has_more"]:
            url = data["links"]["next"]
            check_export_rate_limit()
            data = make_request_get(url, headers).json()
            export_rate_limit_count += 1
        else:
            url = ""

    return all_items


def filter_tokens(tokens):
    """Filter out tokens created today and return their IDs only"""
    today = time.strftime("%Y-%m-%d")
    return [
        token["id"] for token in tokens if not token["created_at"].startswith(today)
    ]


def chunks(lst, n):
    # Yield successive n-sized chunks from lst
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def revoke_many_tokens(tokens_ids: list, headers: dict):
    url = f"https://pagopa.zendesk.com/api/v2/oauth/tokens/delete_many"
    make_request_post(url, payload={"token_ids": tokens_ids}, headers=headers)


#########
# ENTRY #
#########

if len(sys.argv) < 2:
    print("Usage: python cleanup_legacy_client.py <legacy-client-id>")
    sys.exit(1)

# Get an access token

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

# Select end users from a specific org

LEGACY_CLIENT_ID = sys.argv[1]
print("Running for legacy client id '" + LEGACY_CLIENT_ID + "'")

export_rate_limit_count = 0
all_tokens = get_tokens(LEGACY_CLIENT_ID, headers)
token_ids = filter_tokens(all_tokens)

print(f"Disposing {len(token_ids)} items...")

export_rate_limit_count = 0
for tokens in list(chunks(token_ids, 100)):
    current_chunk = [item for item in tokens]
    revoke_many_tokens(current_chunk, headers)

    export_rate_limit_count += 1
    check_export_rate_limit()
    print(current_chunk)
