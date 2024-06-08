import socketio
import requests
from blendr.config.setup import load_config

http_session = requests.Session()
http_session.verify = False
sio = socketio.Client(http_session=http_session)

def connect_to_server(server_url, token):

    """Connect to the server with a given token."""
    try:
        # print(f"Connecting to the server at {server_url}...")
        sio.connect(server_url, headers={"Authorization": f"Bearer {token}"})
        print("Connected to the server.")
        initialConfig = load_config()
        sio.emit('initialconfig', initialConfig)
    except socketio.exceptions.ConnectionError as e:
        print(f"ConnectionError: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")