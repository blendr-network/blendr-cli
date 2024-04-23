
import json
import shutil
import GPUtil


def setup_initial_config():
    print("Welcome to the Initial Setup for Blendr GPU Lending")
    disk_space = allocate_space()
    gpu = select_gpu()
    storage_path = input("Enter the storage path: ")
    save_preferences(disk_space, gpu,storage_path)



def save_preferences(disk_space, gpu,storage_path):
    config = {
        'disk_space_gib': disk_space,
        'gpu_id': gpu.id if gpu else None,
        'storage_path': storage_path
    }
    with open('config.json', 'w') as f:
        json.dump(config, f)
    print("Configuration saved.")


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



def check_disk_space():
    total, used, free = shutil.disk_usage("/")
    print(f"Total: {total // (2**30)} GiB")
    print(f"Used: {used // (2**30)} GiB")
    print(f"Free: {free // (2**30)} GiB")
    return free


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