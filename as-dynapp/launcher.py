import io
import os
import shutil
import subprocess
import tarfile
import tempfile

import requests

APP_NAME = "AS-DynApp"
APP_URL = f"https://github.com/pagopa/assistenza-zendesk-maintenance/releases/latest/download/{APP_NAME}.tar.gz"


def download_and_extract(url, extract_to):
    print("Preparing app...")
    response = requests.get(url)
    response.raise_for_status()
    with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar_ref:
        tar_ref.extractall(path=extract_to)

    print("App is ready.")


def run_app(app_path):
    try:
        print("[INFO] Starting app...")
        subprocess.run([app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {e}")


def main():
    temp_p = tempfile.mkdtemp(prefix="remote_app_")
    try:
        download_and_extract(APP_URL, temp_p)
        bin_p = os.path.join(temp_p, f"{APP_NAME}.app", "Contents", "MacOS", APP_NAME)
        run_app(bin_p)
    finally:
        shutil.rmtree(temp_p, ignore_errors=True)


if __name__ == "__main__":
    main()
