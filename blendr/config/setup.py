
import json
import shutil
import GPUtil
import psutil
from speedtest import Speedtest
import cpuinfo
import platform
import subprocess

def setup_initial_config():
    print("Welcome to the Initial Setup for Blendr GPU Lending")
    node_name = select_nodename()
    storage_info = get_storage_info()
    gpu_info = select_gpu()
    cpu_info = get_cpu_info()
    network_info = check_network_speed()

    save_preferences(node_name, storage_info, gpu_info, cpu_info, network_info)



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
        print(f"{i}: {gpu.name} (ID: {gpu.id}) - Memory Total: {gpu.memoryTotal:.2f} MB")

    while True:
        choice = input("Enter the number of the GPU you wish to rent: ")
        if choice.isdigit() and int(choice) < len(gpus):
            selected_gpu = gpus[int(choice)]
            gpu_info = {
                "name": selected_gpu.name,
                "id": selected_gpu.id,
                "total_memory_mb": selected_gpu.memoryTotal,
            }
            print(f"GPU {selected_gpu.name} selected.")
            return gpu_info
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
        
        


#    ==========================
#   Getting Storage Information
#   ===========================

def check_disk_space(path):
    total, used, free = shutil.disk_usage(path)
    print(f"Total: {total // (2**30)} GiB")
    print(f"Used: {used // (2**30)} GiB")
    print(f"Free: {free // (2**30)} GiB")
    return total, used, free

def get_storage_type_linux(path):
    command = f"lsblk -no NAME,TYPE {path} | grep disk"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    output = result.stdout.strip()
    if 'ssd' in output:
        return "SSD"
    else:
        return "HDD"

def get_storage_type_windows(path):
    drive = path[0]
    command = f"wmic diskdrive where Index=0 get MediaType"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    output = result.stdout.strip()
    if "SSD" in output:
        return "SSD"
    else:
        return "HDD"
    
def get_storage_type(path):
    os_type = platform.system()
    if os_type == "Windows":
        return get_storage_type_windows(path)
    elif os_type == "Linux":
        return get_storage_type_linux(path)
    else:
        print(f"Unsupported operating system: {os_type}")
        return "Unknown"

def get_storage_info():
    while True:
        storage_path = input("Enter the storage path where you'd like to allocate space: ")
        if shutil.disk_usage(storage_path):
            total, used, free = check_disk_space(storage_path)
            break
        else:
            print("Invalid path. Please enter a valid path.")

    while True:
        try:
            allocation_mb = float(input("Enter the amount of space to allocate (in MB): "))
            if allocation_mb > free / (2**20):  # Convert bytes to MB for comparison
                print("Error: Not enough free space. Please enter a smaller amount.")
            else:
                print(f"{allocation_mb} MB allocated successfully at {storage_path}.")
                break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    storage_type = get_storage_type(storage_path)

    storage_info = {
        "path": storage_path,
        "total_gb": total / (2**30),
        "allocated_mb": allocation_mb,
        "storage_type": storage_type,
    }

    return storage_info

                      

def save_preferences(node_name,storage_info, gpu_info, cpu_info, network_info):
    try:
        config = {
            'node_name': node_name,
            'gpu_info': gpu_info if gpu_info else None,
            'storage_info': storage_info,
            'cpu_info': cpu_info,
            'network_info': network_info
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
    
    