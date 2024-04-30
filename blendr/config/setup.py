
import json
import shutil
import GPUtil
import psutil
from speedtest import Speedtest
import cpuinfo

def setup_initial_config():
    print("Welcome to the Initial Setup for Blendr GPU Lending")
    node_name = select_nodename()
    disk_space = allocate_space()
    ram_info = allocate_ram()
    gpu = select_gpu()
    storage_path = input("Enter the storage path: ")
    cpu_info = get_cpu_info()
    network_speeds = check_network_speed()

    save_preferences(node_name, disk_space, ram_info, gpu, storage_path, cpu_info, network_speeds)




def select_nodename():
    while True:
        node_name = input("Enter the name of the node: ")
        if node_name.strip():
            return node_name
        else:
            print("Invalid input. Please enter a non-empty name.")


def select_gpu():
    gpus = GPUtil.getGPUs()
    if not gpus:
        print("No GPUs available.")
        return None
    print("Available GPUs:")
    for i, gpu in enumerate(gpus):
        print(f"{i}: {gpu.name} (ID: {gpu.id})")

    while True:
        choice = input("Enter the number of the GPU you wish to rent: ")
        if choice.isdigit() and int(choice) < len(gpus):
            print(f"GPU {gpus[int(choice)].name} selected.")
            return gpus[int(choice)]
        else:
            print("Invalid selection. Please enter a valid number.")


def get_cpu_info():
    try:
        print("Getting CPU information...")
        info = cpuinfo.get_cpu_info()  # Get all CPU information
        print(f"Model: {info['brand_raw']}")
        return {
            "model": info['brand_raw'],  # CPU model name
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": info.get('hz_advertised_friendly', "N/A"),  # Advertised frequency
            "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
        }
    except Exception as e:
        print(f"Failed to retrieve CPU information: {str(e)}")
        return {}

    

def check_network_speed():
    try:
        print("Checking network speed...")
        st = Speedtest()
        st.get_best_server()
        download_speed = st.download() / (10**6)  # Convert to Mbps
        upload_speed = st.upload() / (10**6)  # Convert to Mbps
        return {
            "download_speed_mbps": download_speed,
            "upload_speed_mbps": upload_speed
        }
    except Exception as e:
        print(f"Failed to check network speeds: {str(e)}")
        return {
             "download_speed_mbps": 0,
            "upload_speed_mbps": 0
        }

def check_disk_space():
    total, used, free = shutil.disk_usage("/")
    print(f"Total: {total // (2**30)} GiB")
    print(f"Used: {used // (2**30)} GiB")
    print(f"Free: {free // (2**30)} GiB")
    return free


def allocate_space():
    free_space = check_disk_space()  # This will still retrieve the space in bytes
    while True:
        try:
            allocation = float(input("Enter the amount of space to allocate (in MB): "))
            allocation_bytes = allocation * (2**20)  # Convert MB to bytes
            if allocation_bytes > free_space:
                print("Error: Not enough free space. Please enter a smaller amount.")
            else:
                print(f"{allocation} MB allocated successfully.")
                return allocation  # Return the allocation in MB
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def allocate_ram():
    total_ram = psutil.virtual_memory().total / (2**20)  # Convert bytes to MB
    print(f"Total RAM available: {total_ram:.2f} MB")
    while True:
        try:
            ram_allocation = float(input("Enter the amount of RAM to allocate (in MB): "))
            if ram_allocation > total_ram:
                print("Error: Not enough RAM. Please enter a smaller amount.")
            else:
                print(f"{ram_allocation} MB of RAM allocated successfully.")
                return ram_allocation  # Return the allocation in MB
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
            

def save_preferences(node_name, disk_space, ram_info, gpu, storage_path, cpu_info, network_speeds):
    try:
        config = {
            'node_name': node_name,
            'disk_space_gib': disk_space,
            'ram_gib': ram_info,
            'gpu_id': gpu.id if gpu else None,
            'gpu_name': gpu.name if gpu else None,
            'storage_path': storage_path,
            'cpu_info': cpu_info,
            'network_speeds': network_speeds
        }
        with open('node-config.json', 'w') as f:
            json.dump(config, f)
        print("Configuration saved.")
    except Exception as e:
        print(f"Failed to save configuration: {str(e)}")
    

def load_config():
    """Load the configuration from a JSON file."""
    try:
        with open('node-config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Configuration file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding the configuration file.")
        return {}
    
    