import GPUtil



def detech_gpus():
    """Checking for available GPUs"""
    gpus = GPUtil.getGPUs()
    if len(gpus) == 0:
        print("No GPUs found on this system.")
        return



