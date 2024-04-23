import requests
from blendr.config.settings import SERVER_URL, CLIENT_URL
import keyring



def listen():
    """Listen to Server Tasks"""
    token = keyring.get_password("system", "blendr_jwt_token")
    print(token)


