#!/usr/bin/env python3
import os
import argparse
import secrets
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def generate_key():
    """Generate a secure 256-bit AES key."""
    return secrets.token_bytes(32)

def pad_data(data):
    """Apply PKCS7 padding to data."""
    padder = padding.PKCS7(128).padder()
    return padder.update(data) + padder.finalize()

def unpad_data(padded_data):
    """Remove PKCS7 padding from data."""
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()

def encrypt_file(input_path, output_path, key):
    """Encrypt a single file using AES-256-CBC."""
    iv = secrets.token_bytes(16)  # Generate random IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(input_path, 'rb') as f:
        data = f.read()
    
    padded_data = pad_data(data)
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    with open(output_path, 'wb') as f:
        f.write(iv + ciphertext)  # Prepend IV to ciphertext
    
    print(f"Encrypted: {input_path} → {output_path}")

def decrypt_file(input_path, output_path, key):
    """Decrypt a single file using AES-256-CBC."""
    with open(input_path, 'rb') as f:
        data = f.read()
    
    iv, ciphertext = data[:16], data[16:]  # Extract IV and ciphertext
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    plaintext = unpad_data(padded_data)
    
    with open(output_path, 'wb') as f:
        f.write(plaintext)
    
    print(f"Decrypted: {input_path} → {output_path}")

def process_folder(input_dir, output_dir, key, mode):
    """Process all files in a folder for encryption or decryption."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for file_path in Path(input_dir).rglob('*'):
        if file_path.is_file():
            rel_path = file_path.relative_to(input_dir)
            if mode == 'encrypt':
                output_path = Path(output_dir) / f"{rel_path}.enc"
                encrypt_file(file_path, output_path, key)
            elif mode == 'decrypt' and file_path.suffix == '.enc':
                output_path = Path(output_dir) / rel_path.with_suffix('')
                decrypt_file(file_path, output_path, key)

def main():
    """Main function to handle CLI arguments and orchestrate encryption/decryption."""
    parser = argparse.ArgumentParser(
        description="File encryption/decryption tool using AES-256-CBC.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--encrypt', action='store_true', help='Encrypt the input file or folder'
    )
    parser.add_argument(
        '--decrypt', action='store_true', help='Decrypt the input file or folder'
    )
    parser.add_argument(
        '--input', required=True, help='Path to input file or folder'
    )
    parser.add_argument(
        '--output', required=True, help='Path to output file or folder'
    )
    parser.add_argument(
        '--key', help='AES key (32 bytes, hex-encoded) or generate if omitted'
    )
    
    args = parser.parse_args()

    if args.encrypt == args.decrypt:
        parser.error("Exactly one of --encrypt or --decrypt must be specified")
    
    mode = 'encrypt' if args.encrypt else 'decrypt'
    key = bytes.fromhex(args.key) if args.key else generate_key()
    
    if len(key) != 32:
        parser.error("Key must be 32 bytes (64 hex characters)")
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if input_path.is_file():
        if mode == 'encrypt':
            output_file = output_path if output_path.suffix == '.enc' else output_path.with_suffix('.enc')
            encrypt_file(input_path, output_file, key)
        else:
            if input_path.suffix != '.enc':
                parser.error("Input file must have .enc extension for decryption")
            output_file = output_path
            decrypt_file(input_path, output_file, key)
    elif input_path.is_dir():
        process_folder(input_path, output_path, key, mode)
    else:
        parser.error("Input path does not exist")
    
    if not args.key:
        print(f"Generated key (hex): {key.hex()}")

if __name__ == "__main__":
    main()