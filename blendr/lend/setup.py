import subprocess


def create_windows_user(username, public_key):
    # Create user
    subprocess.run(["powershell", "-Command", f"New-LocalUser -Name {username} -NoPassword"], check=True)

    # Create SSH directory
    user_ssh_dir = f'C:\\Users\\{username}\\.ssh'
    subprocess.run(["powershell", "-Command", f"New-Item -Path {user_ssh_dir} -ItemType Directory"], check=True)

    # Setup authorized_keys file
    authorized_keys_path = f'{user_ssh_dir}\\authorized_keys'
    with open(authorized_keys_path, 'w') as file:
        file.write(public_key)

    # Set appropriate permissions (example using ICACLS to set permissions)
    subprocess.run(["icacls", authorized_keys_path, "/grant", f"{username}:(R,W)"], check=True)
    
    
def revoke_windows_user(username):
    # Disable user account
    subprocess.run(["powershell", "-Command", f"Disable-LocalUser -Name {username}"], check=True)

    # Remove SSH keys
    subprocess.run(["powershell", "-Command", f"Remove-Item -Path C:\\Users\\{username}\\.ssh\\authorized_keys"], check=True)
    

def create_linux_user(username, public_key):
    try:
        # Create the user with a restricted shell
        subprocess.run(['sudo', 'useradd', '-m', '-s', '/bin/rbash', username], check=True)
        subprocess.run(['sudo', 'mkdir', '-p', f'/home/{username}/.ssh'], check=True)
        subprocess.run(['sudo', 'chown', f'{username}:{username}', f'/home/{username}/.ssh'], check=True)
        subprocess.run(['sudo', 'chmod', '700', f'/home/{username}/.ssh'], check=True)

        # Set up the bin directory
        subprocess.run(['sudo', 'mkdir', '-p', f'/home/{username}/bin'], check=True)
        subprocess.run(['sudo', 'chown', f'{username}:{username}', f'/home/{username}/bin'], check=True)
        subprocess.run(['sudo', 'chmod', '755', f'/home/{username}/bin'], check=True)
        # Copy necessary binaries (e.g., ls, mkdir) to the bin directory
        commands_to_allow = ['ls', 'mkdir']
        for cmd in commands_to_allow:
            subprocess.run(['sudo', 'cp', f'/bin/{cmd}', f'/home/{username}/bin/{cmd}'], check=True)

        # Write the public key to the authorized_keys file
        authorized_keys_path = f'/home/{username}/.ssh/authorized_keys'
        with open(f'/tmp/{username}_pubkey', 'w') as temp_key_file:
            temp_key_file.write(public_key)

        subprocess.run(['sudo', 'mv', f'/tmp/{username}_pubkey', authorized_keys_path], check=True)
        subprocess.run(['sudo', 'chown', f'{username}:{username}', authorized_keys_path], check=True)
        subprocess.run(['sudo', 'chmod', '600', authorized_keys_path], check=True)

        # Set user's PATH to only include the bin directory
        with open(f'/home/{username}/.profile', 'w') as profile:
            profile.write('PATH=$HOME/bin\n')
            profile.write('export PATH\n')

        print(f"User {username} created with restricted access and public key installed.")
    except subprocess.CalledProcessError as e:
            print(f"Failed to complete setup for {username}: {str(e)}")
            

def revoke_linux_user(username):
    try:
        # Lock the user account
        subprocess.run(['sudo', 'usermod', '-L', username], check=True)
        # Remove SSH key access
        subprocess.run(['sudo', 'rm', f'/home/{username}/.ssh/authorized_keys'], check=True)
            
        print(f"Access revoked for {username}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to revoke access for {username}: {str(e)}")