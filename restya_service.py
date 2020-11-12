
import requests
import json


class RestyaService:

    def __init__(self, base_url, auth_token):
        self._base_url = base_url
        self._auth_token = auth_token

    def _basic_request(self, request_method, url_param):
        response = request_method(f"{self._base_url}/{url_param}", params={'token': self._auth_token})

        if response.ok:
            return json.loads(response.content)
        else:
            response.raise_for_status()

    def get_boards(self):
        return self._basic_request(requests.get, '/v1/boards.json')





