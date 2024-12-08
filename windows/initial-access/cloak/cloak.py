import subprocess
import os
import questionary
from questionary import Style


def rdp_masq():
    print("Initializing RDP masquerade...")

    # Prompt user for credentials and target IP
    username = input("Enter RDP Username: ")
    password = input("Enter RDP Password: ")
    target = input("Enter Target IP of RDP Target: ")

    # Prompt user for tunneling decision
    proxy_question = input("Do you have to tunnel this connection through an intermediary? (Y/N): ").strip().lower()

    if proxy_question == "y":
        print("You selected 'yes'.")
        choice2 = questionary.select(
            "Tunnel Type:",
            choices=["SOCKS Proxy", "SSH Tunnel", "TCP Tunnel", "Exit"],
            style=custom_style
        ).ask()

        if choice2 == "SOCKS Proxy":
            print("You selected SOCKS Proxy...")
            socks_ip = input("Enter SOCKS Server IP: ")
            socks_port = input("Enter SOCKS Server Port: ")

            # Build the Docker image
            docker_image = "rdp_masq_image"
            print("Building the Docker container...")
            try:
                subprocess.run(["sudo", "docker", "build", "-t", docker_image, "."], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while building Docker image: {e}")
                return

            # Ensure DISPLAY is set
            if "DISPLAY" not in os.environ:
                os.environ["DISPLAY"] = ":0.0"

            # Grant X11 access for the container
            print("Granting X11 permissions...")
            subprocess.run(["xhost", "+local:root"], check=True)

            try:
                # Start Chisel in the background and xfreerdp in the container
                print("Starting Chisel and xfreerdp session inside Docker container...")
                subprocess.run([
                    "sudo", "docker", "run", "--rm", "-it",
                    "-e", f"DISPLAY={os.environ['DISPLAY']}",
                    "-v", "/tmp/.X11-unix:/tmp/.X11-unix",
                    docker_image,
                    "bash", "-c",
                    f"chisel client {socks_ip}:{socks_port} R:socks & sleep 5 && xfreerdp /cert-ignore /u:{username} /p:{password} /v:{target}"
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred during xfreerdp execution: {e}")
            finally:
                # Revoke X11 permissions
                print("Revoking X11 permissions...")
                subprocess.run(["xhost", "-local:root"], check=True)

            print("RDP masquerade session complete!")

        elif choice2 == "SSH Tunnel":
            print("You selected SSH Tunnel...")
            ssh_ip = input("Enter the SSH Tunnel IP: ")
            ssh_port = input("Enter the SSH Tunnel Port (Usually 22): ")
            ssh_user = input("Enter the SSH username: ")
            print(f"Deploying SSH tunnel to {ssh_ip}:{ssh_port}")

            # Build the Docker image
            docker_image = "rdp_masq_image"
            print("Building the Docker container...")
            try:
                subprocess.run(["sudo", "docker", "build", "-t", docker_image, "."], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while building Docker image: {e}")
                return

            # Ensure DISPLAY is set
            if "DISPLAY" not in os.environ:
                os.environ["DISPLAY"] = ":0.0"

            # Grant X11 access for the container
            print("Granting X11 permissions...")
            subprocess.run(["xhost", "+local:root"], check=True)

            try:
                # Start SSH forward tunnel and xfreerdp in the container
                print("Starting SSH forward tunnel and xfreerdp session inside Docker container...")
                subprocess.run([
                    "sudo", "docker", "run", "--rm", "-it",
                    "-e", f"DISPLAY={os.environ['DISPLAY']}",
                    "-v", "/tmp/.X11-unix:/tmp/.X11-unix",
                    docker_image,
                    "bash", "-c",
                    f"ssh -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -N -L 127.0.0.1:3389:{target}:3389 -p {ssh_port} {ssh_user}@{ssh_ip} & sleep 5 && xfreerdp /cert-ignore /u:{username} /p:{password} /v:127.0.0.1"
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred during SSH tunnel or xfreerdp execution: {e}")
            finally:
                # Revoke X11 permissions
                print("Revoking X11 permissions...")
                subprocess.run(["xhost", "-local:root"], check=True)

            print("RDP masquerade session complete!")

        elif choice2 == "TCP Tunnel":
            print("Module Still in Development")
            print("Will Continue Development when we have implants that support TCP Tunneling like Sliver")

        elif choice2 == "Exit":
            print("Exiting the program. Goodbye!")
            return

    elif proxy_question == "n":
        print("You selected 'no'. Proceeding without intermediary.")
        # Run xfreerdp without tunneling
        docker_image = "rdp_masq_image"
        print("Building the Docker container...")
        try:
            subprocess.run(["sudo", "docker", "build", "-t", docker_image, "."], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Docker image: {e}")
            return

        # Ensure DISPLAY is set
        if "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":0.0"

        # Grant X11 access for the container
        print("Granting X11 permissions...")
        subprocess.run(["xhost", "+local:root"], check=True)

        try:
            # Start xfreerdp session inside Docker container
            print("Starting xfreerdp session inside Docker container...")
            subprocess.run([
                "sudo", "docker", "run", "--rm", "-it",
                "-e", f"DISPLAY={os.environ['DISPLAY']}",
                "-v", "/tmp/.X11-unix:/tmp/.X11-unix",
                docker_image,
                "xfreerdp", "/cert-ignore", f"/u:{username}", f"/p:{password}", f"/v:{target}"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during xfreerdp execution: {e}")
        finally:
            # Revoke X11 permissions
            print("Revoking X11 permissions...")
            subprocess.run(["xhost", "-local:root"], check=True)

        print("RDP masquerade session complete!")

    else:
        print("Invalid input. Please enter 'y' or 'n'. Exiting.")
        return


def ssh_masq():
    print("Initializing SSH masquerade...")

    username = input("Enter SSH Username: ")
    password = input("Enter SSH Password: ")
    ssh_target_ip = input("Enter Target IP of SSH Target: ")
    ssh_target_port = input("Enter the Target's SSH Port (default: 22): ").strip() or "22"

    proxy_question = input("Do you have to tunnel this connection through an intermediary? (Y/N): ").strip().lower()

    if proxy_question == "y":
        choice = questionary.select(
            "Tunnel Type:",
            choices=["SOCKS Proxy", "SSH Tunnel", "TCP Tunnel", "Exit"],
            style=custom_style
        ).ask()

        if choice == "SOCKS Proxy":
            print("SOCKS Proxy Chosen")

            # Prompt for Chisel server details
            socks_ip = input("Enter SOCKS Proxy Server IP: ")
            socks_port = input("Enter SOCKS Proxy Server Port: ")

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
                subprocess.run([
                    "sudo", "docker", "run", "--rm", "-it",
                    docker_image,
                    "bash", "-c",
                    f"chisel client {socks_ip}:{socks_port} R:socks & sleep 5 && sshpass -p '{password}' ssh -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' {username}@{ssh_target_ip} /bin/bash"
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while running Chisel or SSH in the container: {e}")
                return

            print("\033[32m[+] SOCKS Proxy and SSH session completed successfully!\033[0m")

        elif choice == "SSH Tunnel":
            print("You selected SSH Tunnel.")
            ssh_tunnel_ip = input("Enter SSH Tunnel IP: ")
            ssh_tunnel_port = input("Enter SSH Tunnel Port: ")
            ssh_tunnel_user = input("Enter SSH Tunnel Username: ")
            ssh_tunnel_pass = input("Enter SSH Tunnel Password: ")

            # Deploy Docker
            docker_image = "ssh_masq_image"
            print("Building Docker Image...")
            try:
                subprocess.run(["sudo", "docker", "build", "-t", docker_image, "."], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while building Docker image: {e}")
                return

            print("Deploying Docker container to execute the SSH command...")
            try:
                subprocess.run([
                    "sudo", "docker", "run", "--rm", "-it",
                    docker_image,
                    "bash", "-c",
                    f"sshpass -p '{ssh_tunnel_pass}' ssh -L 127.0.0.1:2222:{ssh_target_ip}:{ssh_target_port} {ssh_tunnel_user}@{ssh_tunnel_ip} -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -p {ssh_tunnel_port} -f sleep 5 && sshpass -p '{password}' ssh -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -p 2222 {username}@127.0.0.1 /bin/bash"
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while running the SSH command in the container: {e}")
                return

            print("\033[32m[+] SSH masquerade completed successfully!\033[0m")

        elif choice == "TCP Tunnel":
            print("You selected TCP Tunnel.")
            tcp_tunnel_ip = input("Enter TCP Tunnel IP: ")
            tcp_tunnel_port = input("Enter TCP Tunnel Port: ")
            print(f"Setting up TCP tunnel to {tcp_tunnel_ip}:{tcp_tunnel_port}...")

        elif choice == "Exit":
            print("Exiting SSH masquerade setup. Goodbye!")
            return

    elif proxy_question == "n":
        print("You selected 'no'. Proceeding without intermediary.")

        docker_image = "ssh_masq_image"
        print("Building Docker Image...")
        try:
            subprocess.run(["sudo", "docker", "build", "-t", docker_image, "."], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Docker image: {e}")
            return

        print("Deploying Docker container to execute the SSH command...")
        try:
            subprocess.run([
                "sudo", "docker", "run", "--rm", "-it",
                docker_image,
                "bash", "-c",
                f"sshpass -p '{password}' ssh -o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile=/dev/null' -p {ssh_target_port} {username}@{ssh_target_ip} /bin/bash"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running the SSH command in the container: {e}")
            return

        print("\033[32m[+] SSH masquerade completed successfully!\033[0m")

    else:
        print("Invalid input. Please enter 'y' or 'n'. Exiting.")
        return


# Define a custom style for the dropdown
custom_style = Style([("choice", "fg:blue")])  # Choices will appear in blue

ascii_art = """
_________ .____    ________      _____   ____  __.
\\_   ___ \\|    |   \\_____  \\    /  _  \\ |    |/ _|
/    \\  \\/|    |    /   |   \\  /  /_\\  \\|      <  
\\     \\___|    |___/    |    \\/    |    \\    |  \\ 
 \\______  /_______ \\_______  /\\____|__  /____|__ \\
        \\/        \\/       \\/         \\/        \\/
"""
print(f"\033[35m{ascii_art}\033[0m")

choice = questionary.select(
    "Select a Masquerade Type:",
    choices=["RDP", "SMB", "SSH", "Exit"],
    style=custom_style
).ask()

if choice == "RDP":
    rdp_masq()
elif choice == "SMB":
    print("You selected SMB. Setting up SMB masquerade...")
elif choice == "SSH":
    ssh_masq()
elif choice == "Exit":
    print("Exiting the program. Goodbye!")
