Secure Real-Time Chat Application
A Python-based encrypted chat application using sockets, RSA, and AES encryption with a Streamlit frontend.
Features

End-to-End Encryption: RSA for key exchange, AES-256 (CBC) for messages, HMAC-SHA256 for integrity.
Real-Time Messaging: Supports multiple clients via threading.
Streamlit Dashboard: Send/receive messages, view chat history, load keys, export logs.
File Transfer: Send encrypted text files.
Emoji & Timestamps: Messages include timestamps and support emojis.
Offline Capability: Runs locally with no external dependencies.
Key Management: Auto-generates RSA keys or loads existing ones.

Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save chat_server.py, chat_client.py, crypto_utils.py, app.py, requirements.txt.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the Server:
In a terminal, run: python chat_server.py
Server listens on 127.0.0.1:12345 by default.


Run the Client (CLI or Streamlit):
CLI: Run python chat_client.py, enter messages or file:<path> to send files, quit to exit.
Streamlit: Run streamlit run app.py, configure username/host/port, connect, and use the UI.


View Outputs:
Server: Logs encrypted messages to chat_log.json (last 100 messages).
Client: Logs decrypted messages to <username>_chat_log.json.
Streamlit: Displays real-time chat, encryption status, and allows log export.



Usage

Server: Start chat_server.py first. It handles multiple clients and logs messages.
CLI Client: Run chat_client.py for a terminal-based chat. Use file:<path> for file transfer.
Streamlit UI: Use the web interface (app.py) for a user-friendly experience.
Key Management: Keys are auto-generated (<username>_private.pem, <username>_public.pem) or uploadable via Streamlit.
File Transfer: Upload text files in Streamlit or specify paths in CLI; files are encrypted.
Logs: Export chat history as JSON via Streamlit or check <username>_chat_log.json.

Encryption Details

RSA: 2048-bit keys for secure AES session key exchange.
AES: 256-bit CBC mode for message encryption.
HMAC: SHA256 for message integrity verification.
Messages are never sent or stored in plaintext.
Each client-server pair uses a unique AES session key.

Notes

Runs in <1 minute setup on a standard CPU.
Supports offline operation (localhost).
Includes unit tests for encryption in crypto_utils.py (run python crypto_utils.py).
Logs last 100 messages for performance.
Streamlit UI requires streamlit run app.py and a browser.
