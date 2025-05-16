import importlib.util
import io
import os
import shutil
import sys
import tempfile
import zipfile

import requests

APP_URL = "https://github.com/pagopa/assistenza-zendesk-maintenance/releases/latest/download/as-dynapp.zip"
APP_ENTRY = "main.py"
APP_DIR_NAME = "app"


def download_and_extract_zip(url, extract_to):
    print("Downloading app...")
    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(extract_to)
    print("App successfully extracted.")


def run_app(app_dir):
    project_path = os.path.join(app_dir, APP_DIR_NAME)
    main_path = os.path.join(project_path, APP_ENTRY)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)

    spec = importlib.util.spec_from_file_location("main", main_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["main"] = module
    spec.loader.exec_module(module)

    if hasattr(module, "main"):
        module.main(project_path)


def main():
    temp_dir = tempfile.mkdtemp(prefix="remote_app_")
    try:
        download_and_extract_zip(APP_URL, temp_dir)
        run_app(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
