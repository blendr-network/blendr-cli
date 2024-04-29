
import json
import shutil
import GPUtil
import psutil


def setup_initial_config():
    print("Welcome to the Initial Setup for Blendr GPU Lending")
    node_name = select_nodename()
    disk_space = allocate_space()
    ram_info= allocate_ram()
    gpu = select_gpu()
    storage_path = input("Enter the storage path: ")
    
    save_preferences(node_name,disk_space,ram_info,gpu,storage_path)




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



def allocate_space():
    free_space = check_disk_space()
    while True:
        try:
            allocation = float(input("Enter the amount of space to allocate (in GiB): "))
            if allocation * (2**30) > free_space:
                print("Error: Not enough free space. Please enter a smaller amount.")
            else:
                print(f"{allocation} GiB allocated successfully.")
                return allocation
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
            

def check_disk_space():
    total, used, free = shutil.disk_usage("/")
    print(f"Total: {total // (2**30)} GiB")
    print(f"Used: {used // (2**30)} GiB")
    print(f"Free: {free // (2**30)} GiB")
    return free


def allocate_ram():
    total_ram = psutil.virtual_memory().total / (2**30)  # Convert bytes to GiB
    print(f"Total RAM available: {total_ram:.2f} GiB")
    while True:
        try:
            ram_allocation = float(input("Enter the amount of RAM to allocate (in GiB): "))
            if ram_allocation > total_ram:
                print("Error: Not enough RAM. Please enter a smaller amount.")
            else:
                print(f"{ram_allocation} GiB of RAM allocated successfully.")
                return ram_allocation
        except ValueError:
            print("Invalid input. Please enter a numeric value.")



def save_preferences(node_name, disk_space, ram_info, gpu, storage_path):
    config = {
        'node_name': node_name,
        'disk_space_gib': disk_space,
        'ram_gib': ram_info,
        'gpu_id': gpu.id if gpu else None,
        'gpuType': 'Nvidia 3080Ti',
        'storage_path': storage_path,
        'cpu': "Intel Core i7-8700K",
    }
    with open('node-config.json', 'w') as f:
        json.dump(config, f)
    print("Configuration saved.")
    
    

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