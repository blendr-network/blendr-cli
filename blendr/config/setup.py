import json
import shutil
import psutil
from speedtest import Speedtest
import platform
import subprocess
import py3nvml.py3nvml as nvml
from colorama import Fore, Style, init
import requests

# Initialize colorama
init(autoreset=True)

def setup_initial_config():
    print(f"{Fore.CYAN}Welcome to the Initial Setup for Blendr GPU Lending{Style.RESET_ALL}")
    node_name = select_nodename()
    price = get_price()
    port = get_port()
    storage_info = get_storage_info()
    gpu_info = select_gpu()
    cpu_info = get_cpu_info()
    network_info = check_network_speed()
    public_ip = get_public_ip()

    save_preferences(node_name, storage_info, gpu_info, cpu_info, network_info,public_ip,price,port)

def select_nodename():
    while True:
        node_name = input(f"{Fore.GREEN}Enter the name of the node: {Style.RESET_ALL}")
        if node_name.strip():
            return node_name
        else:
            print(f"{Fore.RED}Invalid input. Please enter a non-empty name.{Style.RESET_ALL}")

def select_gpu():
    try:
        nvml.nvmlInit()
        device_count = nvml.nvmlDeviceGetCount()
        if device_count == 0:
            print(f"{Fore.RED}No GPUs available.{Style.RESET_ALL}")
            return None

        print(f"{Fore.CYAN}Available GPUs:{Style.RESET_ALL}")
        gpus = []
        for i in range(device_count):
            handle = nvml.nvmlDeviceGetHandleByIndex(i)
            name = nvml.nvmlDeviceGetName(handle)
            memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
            gpus.append({
                "id": i,
                "name": name,
                "total_memory_mb": memory_info.total / (1024**2)
            })
            print(f"{Fore.YELLOW}{i}: {name} - Memory Total: {memory_info.total / (1024**2):.2f} MB{Style.RESET_ALL}")

        while True:
            choice = input(f"{Fore.GREEN}Enter the number of the GPU you wish to rent: {Style.RESET_ALL}")
            if choice.isdigit() and int(choice) < len(gpus):
                selected_gpu = gpus[int(choice)]
                print(f"{Fore.BLUE}GPU {selected_gpu['name']} selected.{Style.RESET_ALL}")
                nvml.nvmlShutdown()
                return selected_gpu
            else:
                print(f"{Fore.RED}Invalid selection. Please enter a valid number.{Style.RESET_ALL}")
    except nvml.NVMLError as e:
        print(f"{Fore.RED}Failed to initialize NVML: {str(e)}{Style.RESET_ALL}")
        return None

def get_cpu_info():
    try:
        print(f"{Fore.CYAN}Getting CPU information...{Style.RESET_ALL}")
        info = psutil.cpu_freq()
        cpu_info = {
            "model": platform.processor(),
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": info.max if info else "N/A",
            "current_frequency": info.current if info else "N/A"
        }
        print(f"{Fore.BLUE}CPU Info: {cpu_info}{Style.RESET_ALL}")
        return cpu_info
    except Exception as e:
        print(f"{Fore.RED}Failed to retrieve CPU information: {str(e)}{Style.RESET_ALL}")
        return {}

def check_network_speed():
    try:
        print(f"{Fore.CYAN}Checking network speed...{Style.RESET_ALL}")
        st = Speedtest()
        st.get_best_server()
        download_speed = st.download() / (10**6)
        upload_speed = st.upload() / (10**6)
        network_info = {
            "download_speed_mbps": download_speed,
            "upload_speed_mbps": upload_speed
        }
        print(f"{Fore.BLUE}Network Info: {network_info}{Style.RESET_ALL}")
        return network_info
    except Exception as e:
        print(f"{Fore.RED}Failed to check network speeds: {str(e)}{Style.RESET_ALL}")
        return {
            "download_speed_mbps": 0,
            "upload_speed_mbps": 0
        }

def check_disk_space(path):
    total, used, free = shutil.disk_usage(path)
    print(f"{Fore.CYAN}Total: {total // (2**30)} GiB")
    print(f"Used: {used // (2**30)} GiB")
    print(f"Free: {free // (2**30)} GiB{Style.RESET_ALL}")
    return total, used, free

def get_storage_type(path):
    os_type = platform.system()
    if os_type == "Windows":
        command = f"wmic diskdrive get MediaType"
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        output = result.stdout.strip()
        if "SSD" in output:
            return "SSD"
        else:
            return "HDD"
    elif os_type == "Linux":
        command = f"lsblk -no NAME,TYPE {path} | grep disk"
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        output = result.stdout.strip()
        if 'ssd' in output:
            return "SSD"
        else:
            return "HDD"
    else:
        print(f"{Fore.RED}Unsupported operating system: {os_type}{Style.RESET_ALL}")
        return "Unknown"

def get_storage_info():
    while True:
        storage_path = input(f"{Fore.GREEN}Enter the storage path where you'd like to allocate space: {Style.RESET_ALL}")
        if shutil.disk_usage(storage_path):
            total, used, free = check_disk_space(storage_path)
            break
        else:
            print(f"{Fore.RED}Invalid path. Please enter a valid path.{Style.RESET_ALL}")

    while True:
        try:
            allocation_mb = float(input(f"{Fore.GREEN}Enter the amount of space to allocate (in MB): {Style.RESET_ALL}"))
            if allocation_mb > free / (2**20):
                print(f"{Fore.RED}Error: Not enough free space. Please enter a smaller amount.{Style.RESET_ALL}")
            else:
                print(f"{Fore.BLUE}{allocation_mb} MB allocated successfully at {storage_path}.{Style.RESET_ALL}")
                break
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a numeric value.{Style.RESET_ALL}")

    storage_type = get_storage_type(storage_path)

    storage_info = {
        "path": storage_path,
        "total_gb": total / (2**30),
        "allocated_mb": allocation_mb,
        "storage_type": storage_type,
    }

    print(f"{Fore.BLUE}Storage Info: {storage_info}{Style.RESET_ALL}")
    return storage_info

def get_price():
        try:
            price = float(input(f"{Fore.GREEN}Enter the price per hour for renting the node: {Style.RESET_ALL}"))
            return price
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a numeric value.{Style.RESET_ALL}")

def save_preferences(node_name, storage_info, gpu_info, cpu_info, network_info,public_ip,price,port):
    try:
        config = {
            'node_name': node_name,
            'gpu_info': gpu_info if gpu_info else None,
            'storage_info': storage_info,
            'cpu_info': cpu_info,
            'network_info': network_info,
            'public_ip': public_ip,
            'price': price,
            'port': port
        }
        with open('node-config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print(f"{Fore.GREEN}Configuration saved.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Failed to save configuration: {str(e)}{Style.RESET_ALL}")

def load_config():
    try:
        with open('node-config.json', 'r') as f:
            config = json.load(f)
        print(f"{Fore.GREEN}Configuration loaded: {config}{Style.RESET_ALL}")
        return config
    except FileNotFoundError:
        print(f"{Fore.RED}Configuration file not found.{Style.RESET_ALL}")
        return {}
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error decoding the configuration file.{Style.RESET_ALL}")
        return {}
    
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        public_ip = response.text
        return public_ip
    except requests.RequestException as e:
        print(f"{Fore.RED}Failed to get public IP: {str(e)}{Style.RESET_ALL}")
        return "Unavailable"

def get_port():
    try:
        port = float(input(f"{Fore.GREEN}Enter the ssh port for the node: {Style.RESET_ALL}"))
        return port
    except requests.RequestException as e:
        print(f"{Fore.RED}Failed to get Port: {str(e)}{Style.RESET_ALL}")
        return "22"