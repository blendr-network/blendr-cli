import os
import requests

def download_file(url, local_path):
    """Download a file from a URL to a local path if not exists."""
    if not os.path.exists(local_path):
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request succeeds
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {local_path}")
    else:
        print(f"Using cached version: {local_path}")

def setup_local_cache(urls, cache_dir='./cache'):
    """Ensure all files are downloaded and cached."""
    os.makedirs(cache_dir, exist_ok=True)
    local_paths = {}
    for key, url in urls.items():
        local_file = os.path.join(cache_dir, url.split('/')[-1])  # Assumes filename is the last segment of URL
        download_file(url, local_file)
        local_paths[key] = local_file
    return local_paths
