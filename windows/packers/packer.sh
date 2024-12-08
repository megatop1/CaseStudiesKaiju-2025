cat << 'EOF'
__________                __                 
\______   \_____    ____ |  | __ ___________ 
 |     ___/\__  \ _/ ___\|  |/ // __ \_  __ \
 |    |     / __ \\  \___|    <\  ___/|  | \/
 |____|    (____  /\___  >__|_ \\___  >__|   
                \/     \/     \/    \/ 
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

aes() {
# Set the directory you want to list files from
DIRECTORY="../unencrypted_payloads"

# Check if the directory exists
if [ -d "$DIRECTORY" ]; then
    # Initialize a counter for file numbering
    i=1

    # Display each file with a corresponding number
    echo "Please choose a Payload to AES Encrypt:"
    for FILE in "$DIRECTORY"/*; do
        echo "$i) $(basename "$FILE")"
        eval "FILE_$i='$FILE'"
        i=$((i + 1))
    done

    # Prompt the user for a selection
    echo -n "Enter the number of the Payload you wish to AES Encrypt: "
    read choice

    # Check if the choice is valid and retrieve the file
    eval "SELECTED_FILE=\$FILE_$choice"
    if [ -n "$SELECTED_FILE" ]; then
        echo "You selected: $SELECTED_FILE"
        # Here you can add actions to perform with the selected file
        ColorGreen "[+] AES Encrypting Payload"
        python3 'Shellcode-Hide/3 - Encrypting/1 - AES/AES_cryptor.py' $SELECTED_FILE
    else
        echo "Invalid selection."
    fi
else
    echo "Directory does not exist."
fi
}

sigthief() {
    # Prompt User to Select Payload they wish to SigThief
    DIRECTORY="../unencrypted_payloads"

    # Check if the directory exists
    if [ -d "$DIRECTORY" ]; then
        # Initialize a counter for file numbering
        i=1

        # Display each file with a corresponding number
        echo "Please choose a Payload to SigThief:"
        for FILE in "$DIRECTORY"/*; do
            echo "$i) $(basename "$FILE")"
            eval "FILE_$i='$FILE'"
            i=$((i + 1))
        done

        # Prompt the user for a selection
        echo -n "Enter the number of the Payload you wish to SigThief: "
        read choice

        # Check if the choice is valid and retrieve the file
        eval "SELECTED_FILE=\$FILE_$choice"
        if [ -n "$SELECTED_FILE" ]; then
            echo "You selected: $SELECTED_FILE"
            ColorGreen "You are now ready to SigThief a Payload, please choose a file to steal the signature from"

            # Prompt User to Select File they wish to Steal the Signature From
            DIRECTORY_TO_STEAL_FROM="signatures/"  # Change this to your second directory path

            if [ -d "$DIRECTORY_TO_STEAL_FROM" ]; then
                # Initialize a counter for file numbering
                j=1

                # Display each file with a corresponding number
                echo "Please choose a file to steal the signature from:"
                for FILE in "$DIRECTORY_TO_STEAL_FROM"/*; do
                    echo "$j) $(basename "$FILE")"
                    eval "SIGNATURE_FILE_$j='$FILE'"
                    j=$((j + 1))
                done

                # Prompt the user for a selection
                echo -n "Enter the number of the file you wish to use for SigThief: "
                read sig_choice

                # Check if the choice is valid and retrieve the file
                eval "SIGNATURE_FILE=\$SIGNATURE_FILE_$sig_choice"
                if [ -n "$SIGNATURE_FILE" ]; then
                    echo "You selected: $SIGNATURE_FILE"
                    ColorGreen "[+] Proceeding with SigThief on Payload using selected signature file."
                    # Here, add the command to perform SigThief using $SELECTED_FILE and $SIGNATURE_FILE
                    python3 sigthief.py -i $SIGNATURE_FILE -t $SELECTED_FILE -o ../deploy/signatured_payload.exe
                else
                    echo "Invalid selection."
                fi
            else
                echo "Signature directory does not exist: $DIRECTORY_TO_STEAL_FROM"
            fi
        else
            echo "Invalid selection."
        fi
    else
        echo "Payload directory does not exist: $DIRECTORY"
    fi
}

menu() {
echo "
$(ColorGreen '1)') AES Encypt
$(ColorGreen '2)') SigThief
$(ColorGreen '0)') Exit
$(ColorBlue 'Choose an option:') "
        read a
        case $a in
                1) aes ; menu ;;
                2) sigthief ; menu ;;
                        0) exit 0 ;;
                        *) echo -e $red"Wrong option."$clear; WrongCommand;;
        esac
}

# Call the menu function to print it
menu
