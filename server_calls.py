import requests
import json
import logging

LOGGER = logging.getLogger(__name__)

def register_user(username, hashed_password):

    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    }

    json_data = {
        'username': f'{username}',
        'password': f'{hashed_password}',
    }

    try:
        response = requests.post('http://127.0.0.1:8000/registerUser', headers=headers, json=json_data)
        return response.json()
    except Exception as e:
        LOGGER.error(f"Error in register_user: {e}")