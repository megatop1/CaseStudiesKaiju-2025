import os
import subprocess
import readline
from questionary import Style, select

def list_ssh_keys(directory="/root/.ssh"):
    """List available SSH key files in the specified directory."""
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if not files:
            print(f"No SSH keys found in {directory}.")
            return []
        return files
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
        return []
    except PermissionError:
        print(f"Permission denied to access {directory}.")
        return []

def select_ssh_key(directory="/root/.ssh"):
    """Prompt the user to select an SSH key from the available files."""
    keys = list_ssh_keys(directory)
    if not keys:
        return None
    return select(
        "Select your SSH private key:",
        choices=keys,
        style=custom_style
    ).ask()

def rdp_masq():
    print("Initializing RDP masquerade...")
    rdp_username = input("Enter RDP Username: ")
    rdp_password = input("Enter RDP Password: ")
    rdp_target = input("Enter Target IP of RDP Target: ")

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
                command = (
                    f"chisel client {socks_ip}:{socks_port} R:socks & "
                    f"sleep 5 && xfreerdp /cert-ignore /u:{rdp_username} /p:{rdp_password} /v:{rdp_target}"
                )
            case "SSH Tunnel":
                ssh_tunnel_ip = input("Enter SSH Tunnel IP: ")
                ssh_tunnel_port = input("Enter SSH Tunnel Port (default: 22): ").strip() or "22"
                ssh_tunnel_user = input("Enter SSH Username for the Tunnel: ")

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
                        return
                    ssh_command_prefix = f"ssh -i /root/.ssh/{tunnel_key_file} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

                command = (
                    f"{ssh_command_prefix} -N -L 127.0.0.1:3389:{rdp_target}:3389 "
                    f"{ssh_tunnel_user}@{ssh_tunnel_ip} -p {ssh_tunnel_port} & "
                    f"sleep 5 && xfreerdp /cert-ignore /u:{rdp_username} /p:{rdp_password} /v:127.0.0.1"
                )
            case "TCP Tunnel":
                print("TCP Tunnel module is still under development.")
                return
            case "Exit":
                print("Exiting tunnel setup.")
                return
            case _:
                print("Invalid choice. Exiting RDP masquerade setup.")
                return
    else:
        command = f"xfreerdp /cert-ignore /u:{rdp_username} /p:{rdp_password} /v:{rdp_target}"

    print("Running command:", command)
    subprocess.run(command, shell=True)


def ssh_masq():
    print("Initializing SSH masquerade...")

    ssh_target_ip = input("Enter Target IP of SSH Target: ")
    ssh_target_port = input("Enter the Target's SSH Port (default: 22): ").strip() or "22"
    target_username = input("Enter SSH Username for the Target: ")

    target_auth_method = select(
        "Select SSH Authentication Method for the Target:",
        choices=["Password", "SSH Key"],
        style=custom_style
    ).ask()

    if target_auth_method == "Password":
        target_password = input("Enter SSH Password for the Target: ")
        target_ssh_prefix = f"sshpass -p '{target_password}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    elif target_auth_method == "SSH Key":
        target_key_file = select_ssh_key()
        if not target_key_file:
            print("No valid SSH key selected for the Target. Exiting.")
            return
        target_ssh_prefix = f"ssh -i /root/.ssh/{target_key_file} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

    proxy_question = input("Do you have to tunnel this connection through an intermediary? (Y/N): ").strip().lower()

    if proxy_question == "y":
        tunnel_choice = select(
            "Tunnel Type:",
            choices=["SOCKS Proxy", "SSH Tunnel", "TCP Tunnel", "Exit"],
            style=custom_style
        ).ask()

        match tunnel_choice:
            case "SOCKS Proxy":
                socks_ip = input("Enter SOCKS Proxy Server IP: ")
                socks_port = input("Enter SOCKS Proxy Server Port: ")
                command = (
                    f"chisel client {socks_ip}:{socks_port} R:socks & "
                    f"sleep 5 && {target_ssh_prefix} {target_username}@{ssh_target_ip} -p {ssh_target_port} /bin/bash"
                )
            case "SSH Tunnel":
                ssh_tunnel_ip = input("Enter SSH Tunnel IP: ")
                ssh_tunnel_port = input("Enter SSH Tunnel Port (default: 22): ").strip() or "22"
                tunnel_username = input("Enter SSH Username for the Tunnel: ")

                tunnel_auth_method = select(
                    "Select SSH Authentication Method for the Tunnel:",
                    choices=["Password", "SSH Key"],
                    style=custom_style
                ).ask()

                if tunnel_auth_method == "Password":
                    tunnel_password = input("Enter SSH Password for the Tunnel: ")
                    tunnel_ssh_prefix = f"sshpass -p '{tunnel_password}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
                elif tunnel_auth_method == "SSH Key":
                    tunnel_key_file = select_ssh_key()
                    if not tunnel_key_file:
                        print("No valid SSH key selected for the Tunnel. Exiting.")
                        return
                    tunnel_ssh_prefix = f"ssh -i /root/.ssh/{tunnel_key_file} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

                command = (
                    f"{tunnel_ssh_prefix} -L 127.0.0.1:2222:{ssh_target_ip}:{ssh_target_port} "
                    f"{tunnel_username}@{ssh_tunnel_ip} -p {ssh_tunnel_port} -f sleep 5 && "
                    f"{target_ssh_prefix} {target_username}@127.0.0.1 -p 2222 /bin/bash"
                )
            case "TCP Tunnel":
                print("TCP Tunnel is still under development.")
                return
            case "Exit":
                print("Exiting SSH masquerade setup.")
                return
            case _:
                print("Invalid choice. Exiting SSH masquerade setup.")
                return
    else:
        command = (
            f"{target_ssh_prefix} {target_username}@{ssh_target_ip} -p {ssh_target_port} /bin/bash"
        )

    print("Running command:", command)
    subprocess.run(command, shell=True)

# Define custom style
custom_style = Style([("choice", "fg:blue")])

ascii_art = """
_________ .____    ________      _____   ____  __.
\\_   ___ \\|    |   \\_____  \\    /  _  \\ |    |/ _|
/    \\  \\/|    |    /   |   \\  /  /_\\  \\|      <  
\\     \\___|    |___/    |    \\/    |    \\    |  \\ 
 \\______  /_______ \\_______  /\\____|__  /____|__ \\
        \\/        \\/       \\/         \\/        \\/
"""
print(f"\033[35m{ascii_art}\033[0m")

choice = select(
    "Select a Masquerade Type:",
    choices=["RDP", "SSH", "Exit"],
    style=custom_style
).ask()

if choice == "RDP":
    rdp_masq()
elif choice == "SSH":
    ssh_masq()
elif choice == "Exit":
    print("Exiting the program. Goodbye!")
