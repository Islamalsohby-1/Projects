import socket
import threading
import json
import os
from datetime import datetime
from crypto_utils import CryptoUtils
from base64 import b64encode, b64decode

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12345):
        """Initialize the chat server with host and port."""
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}
        self.crypto = CryptoUtils()
        self.crypto.load_or_generate_keys('server_keys')
        self.log_file = 'chat_log.json'
        self.chat_log = []

    def start(self):
        """Start the server and listen for connections."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        
        while True:
            client_socket, addr = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            client_thread.start()

    def handle_client(self, client_socket, addr):
        """Handle a single client connection."""
        # Key exchange
        client_pub_key = self.crypto.load_public_key(client_socket.recv(4096))
        client_socket.send(self.crypto.public_key_pem)
        
        # Generate and send AES session key
        session_key = self.crypto.generate_session_key()
        encrypted_session_key = self.crypto.encrypt_with_public_key(session_key, client_pub_key)
        client_socket.send(encrypted_session_key)
        
        client_id = f"{addr[0]}:{addr[1]}"
        self.clients[client_id] = {'socket': client_socket, 'session_key': session_key}
        print(f"Client {client_id} connected")

        try:
            while True:
                # Receive encrypted message
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Decrypt and verify message
                message_data = json.loads(data.decode())
                encrypted_message = b64decode(message_data['message'])
                iv = b64decode(message_data['iv'])
                hmac = b64decode(message_data['hmac'])
                
                decrypted_message = self.crypto.decrypt_message(
                    encrypted_message, session_key, iv, hmac
                )
                
                # Log message with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = {
                    'timestamp': timestamp,
                    'sender': client_id,
                    'message': decrypted_message
                }
                self.chat_log.append(log_entry)
                self.save_log()
                
                # Broadcast message to all clients
                self.broadcast(client_id, decrypted_message, timestamp)
                
        except Exception as e:
            print(f"Error with client {client_id}: {e}")
        finally:
            self.clients.pop(client_id, None)
            client_socket.close()
            print(f"Client {client_id} disconnected")

    def broadcast(self, sender_id, message, timestamp):
        """Broadcast message to all connected clients."""
        for client_id, client in self.clients.items():
            session_key = client['session_key']
            encrypted_message, iv, hmac = self.crypto.encrypt_message(message, session_key)
            message_data = {
                'timestamp': timestamp,
                'sender': sender_id,
                'message': b64encode(encrypted_message).decode(),
                'iv': b64encode(iv).decode(),
                'hmac': b64encode(hmac).decode()
            }
            try:
                client['socket'].send(json.dumps(message_data).encode())
            except:
                print(f"Failed to send to {client_id}")

    def save_log(self):
        """Save chat log to file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.chat_log[-100:], f, indent=2)

if __name__ == '__main__':
    server = ChatServer()
    server.start()