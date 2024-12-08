cat << 'EOF'
.____     ________      _____ _________________________________________ 
|    |    \______ \    /  _  \\______   \______   \_   _____/\______   \
|    |     |    |  \  /  /_\  \|     ___/|     ___/|    __)_  |       _/
|    |___  |    `   \/    |    \    |    |    |    |        \ |    |   \
|_______ \/_______  /\____|__  /____|    |____|   /_______  / |____|_  /
        \/        \/         \/                           \/         \/
EOF

## Color Variables
green='\e[32m'
blue='\e[34m'
clear='\e[0m'

ColorGreen(){
        echo $green$1$clear
}

ColorBlue(){
        echo $blue$1$clear
}

all() {
# Prompt user for input
read -p "Target IP: " target
read -p "Domain: " domain
read -p "Username: " username
read -p "Password: " password
read -p "Directory to desired outfile (e.g., case-studies/texas): " outfile
domain_user="${domain}\\${username}"

ldapdomaindump "$target" -u "$domain\\$username" -p "$password" --no-json --no-grep -o "$outfile"

cat "$outfile"/*html > "$outfile"/combined.html

firefox "$outfile"/combined.html
}

all
