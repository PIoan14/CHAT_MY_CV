import requests
import json
import logging

LOGGER = logging.getLogger(__name__)

def login_user(username, password):

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    json_data = {
        'username': username,
        'password': password,
        'CV_content': '',
        'text_summary': '',
    }

    try:
        response = requests.post('http://127.0.0.1:8000/loginUser', headers=headers, json=json_data)
        return response
    except Exception as e:
        LOGGER.error(f"Error in register_user: {e}")


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
        return response.status_code
    except Exception as e:
        LOGGER.error(f"Error in register_user: {e}")


def update_user(userID, element, value):

    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',
}

    params = {
        'doc_id': userID,
        'element': element,
        'value': value,
    }

    try:
        response = requests.post('http://127.0.0.1:8000/updateUser', headers=headers, params=params)
        return response.status_code
    except Exception as e:
        LOGGER.error(f"Error in update_user: {e}")


