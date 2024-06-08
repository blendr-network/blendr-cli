import click
from blendr.auth import authenticate
from blendr.task_manager import listen 
from blendr.gpu_manager import detect
from blendr.config import setup
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define ASCII Art
BLENDR_ASCII_ART = r"""
__________.__                     .___       
\______   \  |   ____   ____    __| _/______ 
 |    |  _/  | _/ __ \ /    \  / __ |\_  __ \
 |    |   \  |_\  ___/|   |  \/ /_/ | |  | \/
 |______  /____/\___  >___|  /\____ | |__|   
        \/          \/     \/      \/      
"""



@click.group()
def cli():
    """
======================
BLENDR CLI
======================
The Blender CLI is a command-line interface that connects users with the Blendr platform. It allows users to lend their GPU for computational tasks.
By running the CLI, users can log in to the system, perform initial setup, check for available GPUs,  nd listen for incoming tasks. 
The CLI provides a convenient way for users to interact with the Blendr platform and contribute their GPU resources.
    """
    pass

@cli.command()
def info():
    """Blendr Info."""
    click.echo(Fore.BLUE + Style.BRIGHT + BLENDR_ASCII_ART + Style.RESET_ALL)
    click.echo(Fore.YELLOW + "Welcome to Blendr!")
    click.echo(Fore.CYAN+"The Blender CLI is a command-line interface that connects users with the Blendr platform.")
    # click.echo(Style.RESET_ALL)

@cli.command()
def login():
    """Log in to the system using credentials."""
    authenticate.login()

@cli.command()
def initalsetup():
    """initial setup"""
    setup.setup_initial_config()

@cli.command()
def detech_gpus():
    """check for cpus"""
    detect.detech_gpus()

@cli.command()
def listentask():
    """Listen to incoming tasks"""
    listen.listen()



def main():
    click.echo(Fore.BLUE + Style.BRIGHT + BLENDR_ASCII_ART + Style.RESET_ALL)  
    cli()

if __name__ == "__main__":
    main()