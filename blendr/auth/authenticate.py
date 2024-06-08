import requests
from blendr.config.settings import SERVER_URL, CLIENT_URL
import webbrowser
import time
# from cryptography.fernet import Fernet
import keyring


def login():
    """Handles user login with server validation."""
    
      # Request session ID from server
    print("Requesting session ID from the server...")
    response = requests.post(f'{SERVER_URL}/api/generate/session-id', json={'deviceID': 'macOS'})
    session_id = response.json().get('sessionId')

    # Open browser for user login and confirmation
    print("Opening browser for user login and confirmation...")
    print(f'URL: {CLIENT_URL}/verify?sessionId={session_id}')
    webbrowser.open(f'{CLIENT_URL}/verify?sessionId={session_id}')

    # Poll the server for the CLI token
    while True:
        token_response = requests.post(f'{SERVER_URL}/api/check/session-id/{session_id}')
        if token_response.status_code == 200:
            token = token_response.json().get('token')
            publicAddress = token_response.json().get('publicAddress')
            keyring.set_password("system", "blendr_jwt_token",token)
            print(f"Login successful. Public Address: {publicAddress}")

            break
        time.sleep(5)  # Wait before polling again


    # # Prepare the payload and headers
    # payload = {'username': username, 'password': password}
    # headers = {'Content-Type': 'application/json'}

    # # Sending a POST request to the server
    # response = requests.post(f"{SERVER_URL}/login", json=payload, headers=headers)

    # if response.status_code == 200:
    #     print("Login successful.")
    #     # Here, you would handle the received auth token securely
    #     # For example, save the token in an environment variable or a secure token storage
    #     return response.json()  # Assuming the server responds with a JSON that includes the auth token
    # else:
    #     print("Login failed. Please check your credentials.")
    #     return None
