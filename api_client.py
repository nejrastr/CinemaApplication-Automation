import os

import requests
from dotenv import load_dotenv

load_dotenv()


class ApiClient:
    def init_client(self):
        self.base_api_url = os.getenv("BASE_API_URL")
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def get(self, endpoint, **kwargs):
        return self.session.get(self.base_api_url + endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.session.post(self.base_api_url + endpoint, **kwargs)