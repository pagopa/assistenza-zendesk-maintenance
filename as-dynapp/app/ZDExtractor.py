import csv
import os
import threading
import time
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests
from constants import CSV_TARGET_DIR, DONE_MESSAGE, EMPTY, GROUPS_MAP
from requests import RequestException


class ZDExtractor:
    def __init__(self, zd_bearer, output_queue, end_task_callback):
        self.zd_bearer = zd_bearer
        self.output_queue = output_queue
        self.end_task_callback = end_task_callback
        self.rate_limit_count = 0
        self.csv_writer = None

    def set_bearer(self, zd_bearer):
        self.zd_bearer = zd_bearer

    def check_rate_limit(self):
        if self.rate_limit_count == 100:
            self.output_queue.put("reached rate limit (100 reqs/min)...delaying 60s\n")
            time.sleep(60)
            self.rate_limit_count = 0

    def make_request(self, url: str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.zd_bearer}",
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.output_queue.put(
                    f"ERR {response.status_code}: {response.reason}\n"
                )
                return None
        except RequestException as ex:
            self.output_queue.put(repr(ex))
            self.output_queue.put("\n")
            return None

        return response.json()

    def utc_to_local(self, utc_string: str):
        # Convert from string to object; expect milliseconds by default
        try:
            dt_utc = datetime.strptime(utc_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            dt_utc = datetime.strptime(utc_string, "%Y-%m-%dT%H:%M:%SZ")

        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

        # Do the conversion
        timestamp = dt_utc.timestamp()
        dt_local = datetime.fromtimestamp(timestamp)

        # Format output: GG-MM-AAAA HH:MM:SS
        output = dt_local.strftime("%d-%m-%Y %H:%M:%S")
        return output

    def print_participants(
        self,
        participants: list,
        tck_created_at: str,
        created_at: str,
        ticket_id: int,
        group_id: int,
        index: int,
    ):
        emails_column = ""
        for item in participants:
            email = item["email"].lower() if item["email"] else EMPTY
            if (
                not email.endswith("@tecnocall.eu")
                and not email.endswith("@soft.it")
                and not email.endswith("@smi-cons.it")
            ):
                emails_column += str(item["email"]) + " "

        self.output_queue.put("...")
        self.csv_writer.writerow(
            [
                self.utc_to_local(tck_created_at),
                self.utc_to_local(created_at),
                str(ticket_id),
                "Side conversation (email) " + str(index),
                emails_column.strip(),
                GROUPS_MAP.get(group_id, "UNKNOWN"),
            ]
        )

    def search_all_participants(
        self, ticket_id: int, tck_created_at: str, group_id: int
    ):
        side_conversations_url = (
            "https://pagopa.zendesk.com/api/v2/tickets/"
            + str(ticket_id)
            + "/side_conversations"
        )
        side_conversations_list = []

        while side_conversations_url:
            data = self.make_request(side_conversations_url)
            if not data:
                break
            for side_conv in data["side_conversations"]:
                if not "targetTicketId" in side_conv["external_ids"]:
                    side_conversations_list.append(
                        {
                            "participants": side_conv["participants"],
                            "created_at": side_conv["created_at"],
                        }
                    )
            side_conversations_url = data["next_page"]

        if len(data["side_conversations"]) == 0:
            self.csv_writer.writerow(
                [
                    self.utc_to_local(tck_created_at),
                    EMPTY,
                    str(ticket_id),
                    EMPTY,
                    EMPTY,
                    GROUPS_MAP.get(group_id, "UNKNOWN"),
                ]
            )
            return

        # sort list by date (descending order)
        side_conversations_sorted = sorted(
            side_conversations_list,
            key=lambda x: datetime.strptime(x["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            reverse=True,
        )

        side_conv_counter = 0
        for item in side_conversations_sorted:
            side_conv_counter += 1
            self.print_participants(
                item["participants"],
                tck_created_at,
                item["created_at"],
                ticket_id,
                group_id,
                side_conv_counter,
            )

    def run_query(self, groups: str, tags: str, timerange: str):
        threading.Thread(
            target=self._run_query, args=(groups, tags, timerange), daemon=True
        ).start()

    def _run_query(self, groups: str, tags: str, timerange: str):
        self.output_queue.put("\nUsing filters:")
        self.output_queue.put("\n " + groups)
        self.output_queue.put("\n " + tags)
        self.output_queue.put("\n " + timerange)
        self.output_queue.put("\n\n")
        #
        # STEP 1: Search a list of tickets
        #
        search_params = {
            "query": f"{groups} {tags} {timerange}",
            "page[size]": 100,
            "filter[type]": "ticket",
        }
        search_url = (
            "https://pagopa.zendesk.com/api/v2/search/export.json?"
            + urlencode(search_params)
        )

        # Fetch the initial page of data
        tck_data = self.make_request(search_url)

        results_count = 0
        ticket_list = []
        while search_url:
            if not tck_data:
                self.end_task_callback()
                return
            results_count += len(tck_data["results"])
            for tck in tck_data["results"]:
                ticket_list.append(
                    {
                        "id": tck["id"],
                        "created_at": tck["created_at"],
                        "group_id": tck["group_id"],
                    }
                )

            self.output_queue.put(f"Tickets found: {results_count}\n")
            if tck_data["meta"]["has_more"]:
                search_url = tck_data["links"]["next"]
                self.check_rate_limit()
                tck_data = self.make_request(search_url)
                self.rate_limit_count += 1
            else:
                search_url = ""
        #
        # STEP 2: Look for outbound emails
        #
        file_handler = None
        if len(ticket_list) > 0:
            self.output_queue.put("Looking for outbound emails (side conversations)\n")

            if not os.path.exists(CSV_TARGET_DIR):
                os.makedirs(CSV_TARGET_DIR)

            epoch = datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
            file_handler = open(
                f"{CSV_TARGET_DIR}ZD_list_all_participants_{epoch}.csv", "w"
            )
            self.csv_writer = csv.writer(file_handler)
            self.csv_writer.writerow(
                [
                    "Data creazione ticket",
                    "Data creazione conv.laterale",
                    "# Ticket",
                    "# Conv.laterale",
                    "Email/s",
                    "Gruppo lavorazione",
                ]
            )
            for ticket_info in ticket_list:
                self.search_all_participants(
                    ticket_info["id"],
                    ticket_info["created_at"],
                    ticket_info["group_id"],
                )

            self.output_queue.put(DONE_MESSAGE)

        if file_handler:
            file_handler.close()

        self.end_task_callback()
