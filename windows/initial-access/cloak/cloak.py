import subprocess
import readline
from questionary import Style, select

def rdp_masq():
    print("Initializing RDP masquerade...")
    username = input("Enter RDP Username: ")
    password = input("Enter RDP Password: ")
    target = input("Enter Target IP of RDP Target: ")

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
                    f"sleep 5 && xfreerdp /cert-ignore /u:{username} /p:{password} /v:{target}"
                )
            case "SSH Tunnel":
                ssh_ip = input("Enter SSH Tunnel IP: ")
                ssh_port = input("Enter SSH Tunnel Port (default: 22): ") or "22"
                ssh_user = input("Enter SSH Username: ")
                command = (
                    f"ssh -N -L 127.0.0.1:3389:{target}:3389 -p {ssh_port} {ssh_user}@{ssh_ip} & "
                    f"sleep 5 && xfreerdp /cert-ignore /u:{username} /p:{password} /v:127.0.0.1"
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
        command = f"xfreerdp /cert-ignore /u:{username} /p:{password} /v:{target}"

    print("Running command:", command)
    subprocess.run(command, shell=True)

def ssh_masq():
    print("Initializing SSH masquerade...")
    username = input("Enter SSH Username: ")
    password = input("Enter SSH Password: ")
    ssh_target_ip = input("Enter Target IP of SSH Target: ")
    ssh_target_port = input("Enter the Target's SSH Port (default: 22): ").strip() or "22"

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
                    f"sleep 5 && sshpass -p '{password}' ssh -o 'StrictHostKeyChecking=no' "
                    f"-o 'UserKnownHostsFile=/dev/null' {username}@{ssh_target_ip} /bin/bash"
                )
            case "SSH Tunnel":
                ssh_tunnel_ip = input("Enter SSH Tunnel IP: ")
                ssh_tunnel_port = input("Enter SSH Tunnel Port (default: 22): ") or "22"
                ssh_tunnel_user = input("Enter SSH Tunnel Username: ")
                ssh_tunnel_pass = input("Enter SSH Tunnel Password: ")
                command = (
                    f"sshpass -p '{ssh_tunnel_pass}' ssh -L 127.0.0.1:2222:{ssh_target_ip}:{ssh_target_port} "
                    f"{ssh_tunnel_user}@{ssh_tunnel_ip} -o 'StrictHostKeyChecking=no' "
                    f"-o 'UserKnownHostsFile=/dev/null' -p {ssh_tunnel_port} -f sleep 5 && "
                    f"sshpass -p '{password}' ssh -o 'StrictHostKeyChecking=no' "
                    f"-o 'UserKnownHostsFile=/dev/null' -p 2222 {username}@127.0.0.1 /bin/bash"
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
            f"sshpass -p '{password}' ssh -o 'StrictHostKeyChecking=no' "
            f"-o 'UserKnownHostsFile=/dev/null' -p {ssh_target_port} {username}@{ssh_target_ip} /bin/bash"
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
