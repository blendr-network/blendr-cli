import py3nvml.py3nvml as nvml
from colorama import Fore, Style

def detech_gpus():
    """Checking for available GPUs"""
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
            name = nvml.nvmlDeviceGetName(handle).decode('utf-8')
            memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
            gpus.append({
                "id": i,
                "name": name,
                "total_memory_mb": memory_info.total / (1024**2)
            })
            print(f"{Fore.YELLOW}{i}: {name} - Memory Total: {memory_info.total / (1024**2):.2f} MB{Style.RESET_ALL}")
            
    except nvml.NVMLError as e:
        print(f"{Fore.RED}Failed to initialize NVML: {str(e)}{Style.RESET_ALL}")
        return None
    



