from blendr.config.settings import SERVER_URL
from blendr.config.setup import load_config
import keyring
import socketio
import requests



def listen():
    """Listen to Server Tasks"""
    token = keyring.get_password("system", "blendr_jwt_token")
    # print("Listening for task updates...")

     # Create a Socket.IO client
    http_session = requests.Session()
    http_session.verify = False
    sio = socketio.Client(http_session=http_session)
    
    @sio.event
    def connect():
        print("Connected to the server. Listening to Task..")
        initialConfig = load_config()
        # print(initialConfig)
        sio.emit('initialconfig', initialConfig)

    @sio.event
    def connect_error(data):
        print("The connection failed!")
    
    @sio.event()
    def error(data):
        print(f"Error: {data.get('message')}")
        
    @sio.event
    def disconnect():
        print("I'm disconnected!")
    
  
# Process the task completion data
    
#  mainEmitter.to(socketID).emit("MAIN: UserConnect", payload);


    # # Define event handlers
    # @sio.on('task_update')
    # def handle_task_update(data):
    #     print(f"Received task update: {data}")
    #     time.sleep(2)
    #     print("emiting..")
    #     sio.emit('test', {'foo': 'bar'})

    #     # Process the task update data

 
        # Process the task completion data
        
    # @sio.on('task_completed')
    # def handle_task_completed(data):
    #     print(f"Task completed: {data}")
    #     # Process the task completion data

    # # Listen for the 'error' event
    # @sio.event
    # def error_handler(data):
    #     print(data)
    #     print(f"Error: {data['message']}")
    #     sio.disconnect()

    # # Listen for the 'disconnect' event
    # @sio.event
    # def disconnect_handler():
    #     print("Disconnected from server")

    try:
        sio.connect(SERVER_URL, headers={"Authorization": f"Bearer {token}"})
        
    except socketio.exceptions.ConnectionError as e:
        print(f"ConnectionError: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return
    

 



    # Start the event loop
    sio.wait()

    # Clean up and disconnect
    # sio.disconnect()




