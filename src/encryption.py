import json
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

class WhatsappEncryption:
    """
    A class to handle encryption and decryption of data for WhatsApp-like communication.
    It uses RSA for encrypting/decrypting AES keys and AES-GCM for encrypting/decrypting data.

    Attributes:
        private_key_path (str): Path to the RSA private key file.
        PRIVATE_KEY: Loaded RSA private key used for decryption.
    """

    def __init__(self, private_key_path):
        """
        Initialize the WhatsappEncryption class with the path to the private key.

        Args:
            private_key_path (str): Path to the RSA private key file.
        """
        self.private_key_path = private_key_path
        self.PRIVATE_KEY = self._load_private_key()

    def _load_private_key(self):
        """
        Load the RSA private key from the specified file.

        Returns:
            private_key: The loaded RSA private key.
        """
        with open(self.private_key_path, 'rb') as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)
        return private_key

    def decrypt_request(self, encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
        """
        Decrypt the incoming request data.

        Args:
            encrypted_flow_data_b64 (str): Base64-encoded encrypted flow data.
            encrypted_aes_key_b64 (str): Base64-encoded encrypted AES key.
            initial_vector_b64 (str): Base64-encoded initialization vector (IV).

        Returns:
            tuple: A tuple containing:
                - decrypted_data (dict): The decrypted flow data as a dictionary.
                - aes_key (bytes): The decrypted AES key.
                - iv (bytes): The initialization vector.
        """
        # Decode the base64-encoded inputs
        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)

        # Decrypt the AES encryption key using the RSA private key
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)
        aes_key = self.PRIVATE_KEY.decrypt(
            encrypted_aes_key,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the flow data using AES-GCM
        encrypted_flow_data_body = flow_data[:-16]  # Extract the encrypted data
        encrypted_flow_data_tag = flow_data[-16:]  # Extract the GCM tag
        decryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, encrypted_flow_data_tag)
        ).decryptor()
        decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))  # Convert bytes to JSON
        return decrypted_data, aes_key, iv

    def encrypt_response(self, response, aes_key, iv):
        """
        Encrypt the response data to send back to the client.

        Args:
            response (dict): The response data to be encrypted.
            aes_key (bytes): The AES key to use for encryption.
            iv (bytes): The initialization vector (IV) used for encryption.

        Returns:
            str: Base64-encoded encrypted response data.
        """
        # Flip the initialization vector by XORing each byte with 0xFF
        flipped_iv = bytearray()
        for byte in iv:
            flipped_iv.append(byte ^ 0xFF)

        # Encrypt the response data using AES-GCM
        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(flipped_iv)
        ).encryptor()
        encrypted_data = encryptor.update(json.dumps(response).encode("utf-8")) + encryptor.finalize()
        return b64encode(encrypted_data + encryptor.tag).decode("utf-8")