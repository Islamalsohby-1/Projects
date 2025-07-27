from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

class CryptoUtils:
    def __init__(self):
        """Initialize cryptographic utilities."""
        self.private_key = None
        self.public_key = None
        self.public_key_pem = None

    def generate_keys(self):
        """Generate new RSA key pair."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKey
        )

    def load_public_key(self, public_key_pem):
        """Load public key from PEM bytes."""
        return serialization.load_pem_public_key(public_key_pem, backend=default_backend())

    def load_or_generate_keys(self, key_file_prefix):
        """Load existing keys or generate new ones."""
        private_key_file = f'{key_file_prefix}_private.pem'
        public_key_file = f'{key_file_prefix}_public.pem'
        
        if os.path.exists(private_key_file) and os.path.exists(public_key_file):
            with open(private_key_file, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
            with open(public_key_file, 'rb') as f:
                self.public_key_pem = f.read()
                self.public_key = self.load_public_key(self.public_key_pem)
        else:
            self.generate_keys()
            with open(private_key_file, 'wb') as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            with open(public_key_file, 'wb') as f:
                f.write(self.public_key_pem)

    def generate_session_key(self):
        """Generate a random AES session key."""
        return os.urandom(32)  # 256-bit key

    def encrypt_with_public_key(self, data, public_key):
        """Encrypt data with RSA public key."""
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt_with_private_key(self, encrypted_data):
        """Decrypt data with RSA private key."""
        return self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_message(self, message, session_key):
        """Encrypt message with AES and generate HMAC."""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad message to be multiple of 16 bytes
        padded_message = message.encode() + b'\0' * (16 - len(message.encode()) % 16)
        encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
        
        # Generate HMAC
        h = hmac.HMAC(session_key, hashes.SHA256(), backend=default_backend())
        h.update(encrypted_message)
        message_hmac = h.finalize()
        
        return encrypted_message, iv, message_hmac

    def decrypt_message(self, encrypted_message, session_key, iv, received_hmac):
        """Decrypt AES-encrypted message and verify HMAC."""
        # Verify HMAC
        h = hmac.HMAC(session_key, hashes.SHA256(), backend=default_backend())
        h.update(encrypted_message)
        h.verify(received_hmac)
        
        # Decrypt message
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted_message) + decryptor.finalize()
        decrypted_message = decrypted_padded.rstrip(b'\0').decode()
        
        return decrypted_message

# Unit tests
if __name__ == '__main__':
    import unittest

    class TestCryptoUtils(unittest.TestCase):
        def setUp(self):
            self.crypto = CryptoUtils()
            self.crypto.generate_keys()
            self.session_key = self.crypto.generate_session_key()

        def test_encrypt_decrypt_message(self):
            message = "Test message"
            encrypted, iv, hmac = self.crypto.encrypt_message(message, self.session_key)
            decrypted = self.crypto.decrypt_message(encrypted, self.session_key, iv, hmac)
            self.assertEqual(message, decrypted)

        def test_key_exchange(self):
            session_key = self.crypto.generate_session_key()
            encrypted_key = self.crypto.encrypt_with_public_key(session_key, self.crypto.public_key)
            decrypted_key = self.crypto.decrypt_with_private_key(encrypted_key)
            self.assertEqual(session_key, decrypted_key)

    unittest.main()
    