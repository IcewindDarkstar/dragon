
import requests
import json

from typing import List, Dict, Callable, Union


class RestyaService:

    def __init__(self, base_url, auth_token):
        self._base_url = base_url
        self._auth_token = auth_token

    def _basic_request(self, request_method: Callable, url_param: str, payload: Dict = None) -> Union[Dict, List]:
        response = request_method(f"{self._base_url}/{url_param}", params={'token': self._auth_token}, json=payload)

        if response.ok:
            return json.loads(response.content)
        else:
            response.raise_for_status()

    def get_boards(self) -> List[Dict]:
        boards_response = self._basic_request(requests.get, 'v1/boards.json')
        return [] if isinstance(boards_response, dict) else boards_response

    def get_board(self, board_id) -> Dict:
        return self._basic_request(requests.get, f'v1/boards/{board_id}.json')

    def create_board(self, board_name: str, orga_id: int, template: str) -> Dict:
        board_response = self._basic_request(requests.post, 'v1/boards.json', {
            'board_visibility': '1',
            'codename_template': 'true',
            'name': board_name,
            'organization_id': str(orga_id),
            'template': template
        })
        return board_response if isinstance(board_response, dict) else None

    def get_board_lists(self, board_id) -> Dict:
        return self.get_board(board_id)['lists']

    def find_board_list(self, board_id, board_list_name) -> Dict:
        board_lists = self.get_board_lists(board_id)
        return next((board_list for board_list in board_lists if board_list['name'] == board_list_name), None)

    def add_card(self, board_id: int, title: str, board_list_name: str) -> Dict:
        board_list = self.find_board_list(board_id, board_list_name)
        if board_list is None:
            print(f"No board list with name '{board_list_name}' found.")
            raise ValueError(f"No board list with name '{board_list_name}' found.")
        list_id = board_list['id']

        return self._basic_request(requests.post, f'v1/boards/{board_id}/lists/{list_id}/cards.json', {
            'name': title,
            'title': title,
            'board_id': board_id,
            'list_id': list_id,
        })

    def get_activities(self) -> List[Dict]:
        return self._basic_request(requests.get, 'v1/activities.json')['data']

