import keyring
from blendr.config.settings import SERVER_URL
from blendr.lend.setup import create_linux_user, create_windows_user, revoke_linux_user, revoke_windows_user
from blendr.ai.tasks.fine_tune import fine_tune
from blendr.initiate_socket.initiate import sio, connect_to_server
import platform

    
def listen():
    """Listen to Server Tasks"""
    token = keyring.get_password("system", "blendr_jwt_token")
    connect_to_server(SERVER_URL, token)
    
    @sio.event
    def connect():
        print("Connected to the server. Listening to Task..")

    @sio.event
    def connect_error(data):
        print("The connection failed!")
    
    @sio.event()
    def error(data):
        print(f"Error: {data.get('message')}")
        
    @sio.event
    def disconnect():
        print("I'm disconnected!")
    
  
    # Define event handlers
    @sio.on('BMAIN: NEW_TASK')
    def handle_new_task(data):
        print(f"New task received: {data}")
        # Based on the task type, decide the function to call
        if data['taskType'] == 'FINE_TUNE':
            try:
                fine_tune(data)
            except Exception as e:
                print(f"An error occurred during task execution: {str(e)}")
                
    
    @sio.on('BMAIN: LEND_GPU')
    def handle_lending(data):
        public_key = data['publicKey']
        username = data['username']

        if not public_key:
            print("No public key found in the data")
            return

        try:
            os_type = platform.system()
            if os_type == "Windows":
                create_windows_user(username, public_key)
            else:
                create_linux_user(username, public_key)
                
        except Exception as e:
            print(f"An error occurred during task execution: {str(e)}")
                
       
    
    @sio.on('BMAIN: REVOKE_LENDING')
    def handle_revokeLending(data):
        username = data['username']
        
        if not username:
            print("No username provided for revoking access.")
            return
    
        try:
            os_type = platform.system()
            if os_type == "Windows":
                revoke_windows_user(username)
            else:
                revoke_linux_user(username)
                
        except Exception as e:
            print(f"An error occurred during task execution: {str(e)}")
                
    

    sio.wait()

    # Clean up and disconnect
    sio.disconnect()





