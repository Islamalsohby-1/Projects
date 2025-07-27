File Encryption/Decryption Tool
A Python tool for encrypting and decrypting files using AES-256-CBC.
Requirements

Python 3.8+
Install dependencies: pip install -r requirements.txt

Usage
# Encrypt a single file
python file_crypto.py --encrypt --input test_files/test1.txt --output test_files/encrypted/test1.txt.enc

# Decrypt a single file
python file_crypto.py --decrypt --input test_files/encrypted/test1.txt.enc --output test_files/decrypted/test1.txt --key <hex_key>

# Encrypt a folder
python file_crypto.py --encrypt --input test_files --output test_files/encrypted

# Decrypt a folder
python file_crypto.py --decrypt --input test_files/encrypted --output test_files/decrypted --key <hex_key>

Notes

If --key is not provided, a random 256-bit key is generated and printed.
Encrypted files have .enc extension.
Decrypted files restore the original extension.
Use the same key for encryption and decryption.
The tool is binary-safe, ensuring decrypted files match originals.
Sample files are in test_files/.

Example
# Encrypt all test files
python file_crypto.py --encrypt --input test_files --output test_files/encrypted
# Note the generated key (e.g., 1a2b3c...)
# Decrypt all test files
python file_crypto.py --decrypt --input test_files/encrypted --output test_files/decrypted --key 1a2b3c...
