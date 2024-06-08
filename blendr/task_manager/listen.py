import keyring
import subprocess
from blendr.config.settings import SERVER_URL
from blendr.config.setup import load_config
from blendr.ai.tasks.fine_tune import fine_tune
from blendr.initiate_socket.initiate import sio, connect_to_server
import os

    
def listen():
    """Listen to Server Tasks"""
    token = keyring.get_password("system", "blendr_jwt_token")
    connect_to_server(SERVER_URL, token)
    print(sio.get_sid())
    @sio.event
    def connect():
        print("Connected to the server. Listening to Task..")
        # initialConfig = load_config()
        # sio.emit('initialconfig', initialConfig)

    @sio.event
    def connect_error(data):
        print("The connection failed!")
    
    @sio.event()
    def error(data):
        print(f"Error: {data.get('message')}")
        
    @sio.event
    def disconnect():
        print("I'm disconnected!")
    
  
# Process the task completion dat
#  mainEmitter.to(socketID).emit("MAIN: UserConnect", payload);


    # # Define event handlers
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
       
        if not public_key:
            print("No public key found in the data")
            return
        
        # Ensure the .ssh directory exists
        
        ssh_dir = os.path.expanduser("~/.ssh")
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, mode=0o700)
        
        # Path to the authorized_keys file
        authorized_keys_path = os.path.join(ssh_dir, "authorized_keys")
        
        # Add the public key to the authorized_keys file
        try:
            with open(authorized_keys_path, 'a') as f:
                f.write(public_key + '\n')
            
            # Ensure the file has the correct permissions
            os.chmod(authorized_keys_path, 0o600)
            print("Public key added to authorized_keys")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            
    

    @sio.on('BMAIN: COMMAND')
    def handle_command(data):
        print(f"Command received: {data['command']}")
        try:
            result = subprocess.run(data['command'], shell=True, capture_output=True, text=True)
            response = {
                    'output': result.stdout,
                    'error': result.stderr,
                    'returncode': result.returncode
                }
        except Exception as e:
            response = {
                    'output': '',
                    'error': str(e),
                    'returncode': -1
                }
            sio.emit('BMAIN: COMMAND_RESPONSE', response)
    # try:
    #     sio.connect(SERVER_URL, headers={"Authorization": f"Bearer {token}"})
        
    # except socketio.exceptions.ConnectionError as e:
    #     print(f"ConnectionError: {str(e)}")
    # except Exception as e:
    #     print(f"Unexpected error: {str(e)}")
    #     return
    


    # Start the event loop
    sio.wait()

    # Clean up and disconnect
    sio.disconnect()




