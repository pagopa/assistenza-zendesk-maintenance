import os

import keyring
from dotenv import load_dotenv, set_key

from constants import USER_HOME_DIR


class CredentialManager:
    def __init__(self, env_path=f"{USER_HOME_DIR}/.as-zd_env"):
        self.env_path = env_path
        load_dotenv(self.env_path)

    def credentials_exist(self):
        service = os.getenv("SERVICE")
        username = os.getenv("USERNAME")
        return bool(service and username)

    def get_credentials(self):
        if not self.credentials_exist():
            raise FileNotFoundError("File .as-zd_env is missing or incomplete.")

        service = os.getenv("SERVICE")
        username = os.getenv("USERNAME")
        password = keyring.get_password(service, username)

        if password is None:
            raise ValueError(
                "Credentials not found in the system keychain for this service/user."
            )

        print(f"Gathering credentials for service '{service}' -> OK")
        return {"service": service, "username": username, "password": password}

    def set_credentials(self, service, username, password):
        set_key(self.env_path, "SERVICE", service)
        set_key(self.env_path, "USERNAME", username)

        keyring.set_password(service, username, password)
        print(f"Credentials saved for service '{service}'.")
