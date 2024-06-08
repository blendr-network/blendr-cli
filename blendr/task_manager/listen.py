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
        username = data['username']
        restricted_dir = f"/home/{username}/restricted"

        if not public_key:
            print("No public key found in the data")
            return

        # Create a new user with a restricted home directory
        try:
            subprocess.run(['sudo', 'useradd', '-m', '-d', restricted_dir, '-s', '/bin/bash', username], check=True)
            subprocess.run(['sudo', 'mkdir', '-p', restricted_dir], check=True)
            subprocess.run(['sudo', 'chown', f'{username}:{username}', restricted_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error creating user or directory: {e}")
            return

        # Ensure the .ssh directory exists for the user
        ssh_dir = os.path.join(restricted_dir, '.ssh')
        try:
            subprocess.run(['sudo', 'mkdir', '-p', ssh_dir], check=True)
            subprocess.run(['sudo', 'chown', f'{username}:{username}', ssh_dir], check=True)
            subprocess.run(['sudo', 'chmod', '700', ssh_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error setting up .ssh directory: {e}")
            return

        # Path to the authorized_keys file for the user
        authorized_keys_path = os.path.join(ssh_dir, 'authorized_keys')

        # Add the public key to the authorized_keys file
        try:
            with open('/tmp/temp_key', 'w') as f:
                f.write(public_key + '\n')
            subprocess.run(['sudo', 'mv', '/tmp/temp_key', authorized_keys_path], check=True)
            subprocess.run(['sudo', 'chown', f'{username}:{username}', authorized_keys_path], check=True)
            subprocess.run(['sudo', 'chmod', '600', authorized_keys_path], check=True)
            print("Public key added to authorized_keys")
        except Exception as e:
            print(f"An error occurred: {e}")

        # Configure SSH to restrict the user to the restricted directory
        sshd_config_addition = f"""
    Match User {username}
        ChrootDirectory {restricted_dir}
        AllowTCPForwarding no
        X11Forwarding no
        ForceCommand internal-sftp
        """

        try:
            with open('/tmp/temp_sshd_config', 'w') as f:
                f.write(sshd_config_addition)
            subprocess.run(['sudo', 'bash', '-c', 'cat /tmp/temp_sshd_config >> /etc/ssh/sshd_config'], check=True)
            subprocess.run(['sudo', 'rm', '/tmp/temp_sshd_config'], check=True)
            subprocess.run(['sudo', 'systemctl', 'restart', 'ssh'], check=True)
            print(f"SSH configured for user {username}")
        except Exception as e:
            print(f"An error occurred while configuring SSH: {e}")
            
    

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




