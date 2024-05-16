from blendr.config.settings import SERVER_URL
from blendr.config.setup import load_config
import keyring
from blendr.ai.tasks.fine_tune import fine_tune
from blendr.initiate_socket.initiate import sio, connect_to_server

    
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




