import requests
import json
import logging
import time
from config import get_config

config = get_config()

LOGGER = logging.getLogger(__name__)


def get_analytics(user_id):
    print(user_id)
    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',
    }

    params = {
        'doc_id': user_id,
    }

    response = requests.post(f'{config['url']['public']}/chatAnalytics', params=params, headers=headers)
    print(response.status_code)
    return response.json()


def delete_user(user_id):

    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',
    }

    params = {
        'document_id': user_id,
    }

    response = requests.post(f'{config['url']['public']}/deleteUser', params=params, headers=headers)
    return response.status_code
    

def chat_RAG_llm(user_id, question, RAG=False):

    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',
    }
    params = {
        'doc_id': user_id,
        'question': question,
        'RAG': RAG,
    }

    try:
        response = requests.post(f'{config['url']['public']}/chatCompletions', params=params, headers=headers, stream=True)
       
        for chunk in response.iter_content(chunk_size=1):
            if chunk:
                yield chunk.decode("utf-8") 
    except Exception as e:
        LOGGER.error(f"Error in chat_RAG_llm: {e}")

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
        response = requests.post(f'{config['url']['public']}/loginUser', headers=headers, json=json_data)
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
        response = requests.post(f'{config['url']['public']}/registerUser', headers=headers, json=json_data)
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
        response = requests.post(f'{config['url']['public']}/updateUser', headers=headers, params=params)
        return response.status_code
    except Exception as e:
        LOGGER.error(f"Error in update_user: {e}")


