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
            # Create the user with a restricted shell
            subprocess.run(['sudo', 'useradd', '-m', '-s', '/bin/rbash', username], check=True)
            subprocess.run(['sudo', 'mkdir', '-p', f'/home/{username}/.ssh'], check=True)
            subprocess.run(['sudo', 'chown', f'{username}:{username}', f'/home/{username}/.ssh'], check=True)
            subprocess.run(['sudo', 'chmod', '700', f'/home/{username}/.ssh'], check=True)

            # Set up the bin directory
            subprocess.run(['sudo', 'mkdir', '-p', f'/home/{username}/bin'], check=True)
            subprocess.run(['sudo', 'chown', f'{username}:{username}', f'/home/{username}/bin'], check=True)
            subprocess.run(['sudo', 'chmod', '755', f'/home/{username}/bin'], check=True)
            # Copy necessary binaries (e.g., ls, mkdir) to the bin directory
            commands_to_allow = ['ls', 'mkdir']
            for cmd in commands_to_allow:
                subprocess.run(['sudo', 'cp', f'/bin/{cmd}', f'/home/{username}/bin/{cmd}'], check=True)

            # Write the public key to the authorized_keys file
            authorized_keys_path = f'/home/{username}/.ssh/authorized_keys'
            with open(f'/tmp/{username}_pubkey', 'w') as temp_key_file:
                temp_key_file.write(public_key)

            subprocess.run(['sudo', 'mv', f'/tmp/{username}_pubkey', authorized_keys_path], check=True)
            subprocess.run(['sudo', 'chown', f'{username}:{username}', authorized_keys_path], check=True)
            subprocess.run(['sudo', 'chmod', '600', authorized_keys_path], check=True)

            # Set user's PATH to only include the bin directory
            with open(f'/home/{username}/.profile', 'w') as profile:
                profile.write('PATH=$HOME/bin\n')
                profile.write('export PATH\n')

            print(f"User {username} created with restricted access and public key installed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to complete setup for {username}: {str(e)}")
            
    

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

    # Start the event loop
    sio.wait()

    # Clean up and disconnect
    sio.disconnect()





