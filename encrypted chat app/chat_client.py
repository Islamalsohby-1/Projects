import socket
import threading
import json
import os
from datetime import datetime
from crypto_utils import CryptoUtils
from base64 import b64encode, b64decode

class ChatClient:
    def __init__(self, host='127.0.0.1', port=12345, username='User'):
        """Initialize the chat client."""
        self.host = host
        self.port = port
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.crypto = CryptoUtils()
        self.crypto.load_or_generate_keys(f'{username}_keys')
        self.session_key = None
        self.chat_log = []
        self.running = False

    def connect(self):
        """Connect to the server and perform key exchange."""
        self.client_socket.connect((self.host, self.port))
        
        # Key exchange
        self.client_socket.send(self.crypto.public_key_pem)
        server_pub_key_pem = self.client_socket.recv(4096)
        server_pub_key = self.crypto.load_public_key(server_pub_key_pem)
        
        # Receive encrypted session key
        encrypted_session_key = self.client_socket.recv(4096)
        self.session_key = self.crypto.decrypt_with_private_key(encrypted_session_key)
        print(f"Connected to server {self.host}:{self.port}")

    def start(self):
        """Start the client and begin receiving messages."""
        self.running = True
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def receive_messages(self):
        """Receive and decrypt incoming messages."""
        while self.running:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                message_data = json.loads(data.decode())
                encrypted_message = b64decode(message_data['message'])
                iv = b64decode(message_data['iv'])
                hmac = b64decode(message_data['hmac'])
                
                decrypted_message = self.crypto.decrypt_message(
                    encrypted_message, self.session_key, iv, hmac
                )
                
                log_entry = {
                    'timestamp': message_data['timestamp'],
                    'sender': message_data['sender'],
                    'message': decrypted_message
                }
                self.chat_log.append(log_entry)
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self, message, is_file=False):
        """Encrypt and send a message or file."""
        if is_file:
            with open(message, 'rb') as f:
                message_content = f.read().decode('utf-8', errors='ignore')
        else:
            message_content = message
        
        encrypted_message, iv, hmac = self.crypto.encrypt_message(message_content, self.session_key)
        message_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'sender': self.username,
            'message': b64encode(encrypted_message).decode(),
            'iv': b64encode(iv).decode(),
            'hmac': b64encode(hmac).decode()
        }
        self.client_socket.send(json.dumps(message_data).encode())
        
        # Log sent message
        self.chat_log.append({
            'timestamp': message_data['timestamp'],
            'sender': self.username,
            'message': message_content
        })

    def save_log(self):
        """Save chat log to file."""
        with open(f'{self.username}_chat_log.json', 'w') as f:
            json.dump(self.chat_log[-100:], f, indent=2)

    def stop(self):
        """Stop the client and close connection."""
        self.running = False
        self.client_socket.close()

if __name__ == '__main__':
    client = ChatClient(username='TestUser')
    client.connect()
    client.start()
    try:
        while True:
            message = input("Enter message (or 'quit' to exit, 'file:<path>' to send file): ")
            if message == 'quit':
                break
            elif message.startswith('file:'):
                client.send_message(message[5:], is_file=True)
            else:
                client.send_message(message)
            client.save_log()
    finally:
        client.stop()