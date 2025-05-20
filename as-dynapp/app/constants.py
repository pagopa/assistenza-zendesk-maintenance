"""all the constants"""

import os
from datetime import datetime, timedelta

APP_NAME = "AS-DynApp"
BUILD_NUMBER = "0045"
APP_VERSION = "2.1"
EMPTY = "N/A"
READY = "--------------------------\nREADY"
DONE_MESSAGE = f'\nESTRAZIONE COMPLETATA! Il file CSV è stato salvato nella cartella "ZD_script_reports" del tuo desktop.\n{READY}\n'
USER_HOME_DIR = os.path.expanduser("~")
CSV_TARGET_DIR = USER_HOME_DIR + "/Desktop/ZD_script_reports/"


GROUPS_MAP = {
    4417760459025: "App IO Auto",
    4414480689553: "App IO Dev",
    360010807858: "App IO L1 - deprecato",
    4419298717841: "App IO Test",
    22381574325137: "Assistenza L1",
    4413589597969: "Assistenza Specialistica DEV",
    11586656951825: "Collaudo Integrazioni",
    20853137736593: "Escalated - deprecato",
    28602622756753: "Lavorazioni Onerose",
    28040676657809: "Non lavorabili",
    9779895386897: "Operations L2",
    4419919552017: "Pagamenti Abbandonate IVR",
    1900001395493: "Pagamenti L1 - deprecato",
    5003770684689: "Pagamenti L1 CBILL - deprecato",
    10084745949457: "Pagamenti L3",
    18469197731601: "RADD L1",
    20372078637329: "SEND L1 - deprecato",
    4414112381713: "Service HUB - Assistenza Specialistica",
    4428058253713: "Suggerimenti IO",
    5118656026257: "Trash",
    23072343125521: "VA Spitch",
}

LABELS_GROUP = [
    "Assistenza L1 + Lavorazioni Onerose",
    "Assistenza L1 + Pagamenti L1 depr. + Lavorazioni Onerose",
    "Assistenza L1",
    "Pagamenti L1 depr.",
    "Lavorazioni Onerose",
    "custom...",
]
VALUES_GROUP = [
    'group:"Lavorazioni Onerose" group:"Assistenza L1"',
    'group:"Lavorazioni Onerose" group:"Assistenza L1" group:"Pagamenti L1 - deprecato"',
    'group:"Assistenza L1"',
    'group:"Pagamenti L1 - deprecato"',
    'group:"Lavorazioni Onerose"',
    "",
]

LABELS_TAG = ["BOpagoPA > PSP > Produzione > SCT storno", "custom..."]
VALUES_TAG = ["tags:bo_pagopa_psp_prod_sct_storno", ""]

LABELS_TIMERANGE = [
    "ultimi 7 gg",
    "ultimi 14 gg",
    "ultimo mese (30 gg)",
    "ultimi 3 mesi",
    "ultimi 6 mesi",
    "ieri",
    "oggi",
    "mese in corso",
    "anno in corso",
    "custom...",
]
VALUES_TIMERANGE = [
    f"created>{(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")}",
    f"created>{(datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")}",
    f"created>{(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")}",
    f"created>{(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")}",
    f"created>{(datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")}",
    f"created:{(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")}",
    f"created:{datetime.now().strftime("%Y-%m-%d")}",
    f"created>={datetime.now().year}-{datetime.now().month:02}-01",
    f"created>={datetime.now().year}-01-01",
    "",
]
