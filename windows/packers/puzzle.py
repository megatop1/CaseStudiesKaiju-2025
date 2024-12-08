import questionary
import subprocess
import os
from questionary import Style

def exe():
    # Display Choices for Encryption Type
    choice = questionary.select(
        "Select EXE Payload Encryption Type:",
        choices=["AES", "NULL", "Exit"],
        style=custom_style
    ).ask()
    if choice == "AES":
        aes()

def aes():
    # Define the directory
    directory = "/app/payloads"

    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    # Display all files in the directory
    files = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]

    # Check if there are files in the directory
    if not files:
        print("No files found in the directory.")
        return

    # Use Questionary to let the user select a file
    selected_file = questionary.select(
        "Select a file:",
        choices=files
    ).ask()

    # Store the user's choice in a variable
    if selected_file:
        selected_file_path = os.path.join(directory, selected_file)
        print(f"Payload selected: {selected_file_path}")
        # Run the Packer Script against the payload
        command = f"python Shellcode-Hide/3\\ -\\ Encrypting/1\\ -\\ AES/AES_cryptor.py {selected_file_path}"
        #command = "ls -lah"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        # Print output
        print(result.stdout)

def shellcode():
    print("Shellcode option selected.")  # Add logic for shellcode if needed

ascii_art = r"""
+-------------------------------------------------------------+
|                                                             |
|   __________ ____ _______________________.____ ___________  |
|   \______   \    |   \____    /\____    /|    |\_   _____/  |
|    |     ___/    |   / /     /   /     / |    | |    __)_   |
|    |    |   |    |  / /     /_  /     /_ |    | |        \  |
|    |____|   |______/ /_______ \/_______ \|____|/_______  /  |
|                          \/        \/        \/          \/ |
|                                                             |
|                        PUZZLE                               |
+-------------------------------------------------------------+
"""

print(f"\033[35m{ascii_art}\033[0m")

custom_style = Style([("choice", "fg:blue")])  # Choices will appear in blue

choice = questionary.select(
    "Payload Type:",
    choices=["EXE", "Shellcode", "Exit"],
    style=custom_style
).ask()

if choice == "EXE":
    print("Creating EXE from Shellcode...")
    exe()
elif choice == "Shellcode":
    print("Creating Shellcode...")
    shellcode()
elif choice == "Exit":
    print("Exiting the program. Goodbye!")
