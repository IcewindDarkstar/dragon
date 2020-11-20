
import requests
import json

from typing import List, Dict, Callable, Union


class RestyaService:

    def __init__(self, base_url, auth_token):
        self._base_url = base_url
        self._auth_token = auth_token

    def _basic_request(self, request_method: Callable, url_param: str, payload: Dict = {}) -> Union[Dict, List]:
        response = request_method(f"{self._base_url}/{url_param}", params={'token': self._auth_token}, json=payload)

        if response.ok:
            return json.loads(response.content)
        else:
            response.raise_for_status()

    def get_boards(self) -> List[Dict]:
        boards_response = self._basic_request(requests.get, 'v1/boards.json')
        return [] if isinstance(boards_response, dict) else boards_response

    def create_board(self, board_name: str, orga_id: int, template: str):
        board_response = self._basic_request(requests.post, 'v1/boards.json', {
            'board_visibility': '1',
            'codename_template': 'true',
            'name': board_name,
            'organization_id': str(orga_id),
            'template': template
        })
        return board_response if isinstance(board_response, dict) else None

    def get_board(self, board_id):
        return self._basic_request(requests.get, f'v1/boards/{board_id}.json')

