import hashlib
import hmac
import requests
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


class WhatsappMedia:
    """
    Helper class to download and decrypt WhatsApp media files from CDN URLs.
    Handles the complete process of verification and decryption.
    """
    
    def __init__(self, media_data):
        """
        Initialize with WhatsApp media data
        
        Args:
            media_data (dict): Dictionary containing file metadata and encryption details
        """
        self.file_name = media_data.get('file_name')
        self.media_id = media_data.get('media_id')
        self.cdn_url = media_data.get('cdn_url')
        
        # Extract and decode encryption metadata
        encryption_metadata = media_data.get('encryption_metadata', {})
        self.encryption_key = base64.b64decode(encryption_metadata.get('encryption_key', ''))
        self.hmac_key = base64.b64decode(encryption_metadata.get('hmac_key', ''))
        self.iv = base64.b64decode(encryption_metadata.get('iv', ''))
        self.plaintext_hash = encryption_metadata.get('plaintext_hash')
        self.encrypted_hash = encryption_metadata.get('encrypted_hash')
        self.debug_mode = False
        self.keep_temp_files = False
        
    def download_from_cdn(self):
        """
        Download file from CDN URL
            
        Returns:
            bytes: The downloaded file content
        """
        response = requests.get(self.cdn_url)
        response.raise_for_status()
        return response.content
    
    def verify_enc_hash(self, cdn_file):
        """
        Verify the SHA256 hash of the downloaded file
        
        Args:
            cdn_file (bytes): Downloaded file content
            
        Returns:
            bool: True if hash matches, False otherwise
        """
        calculated_hash = hashlib.sha256(cdn_file).hexdigest()
        expected_hash = self.encrypted_hash
        
        if self.debug_mode:
            print(f"Calculated hash: {calculated_hash}")
            print(f"Expected hash: {expected_hash}")
        
        # First try direct comparison
        if calculated_hash == expected_hash:
            return True
            
        # Try comparing with the base64 decoded version
        try:
            decoded_hash = base64.b64decode(expected_hash).hex()
            return calculated_hash == decoded_hash
        except:
            pass
            
        return False
    
    def validate_hmac(self, ciphertext, hmac10):
        """
        Validate the HMAC-SHA256 of the ciphertext
        
        Args:
            ciphertext (bytes): The encrypted media content
            hmac10 (bytes): First 10 bytes of the expected HMAC
            
        Returns:
            bool: True if HMAC matches, False otherwise
        """
        h = hmac.new(self.hmac_key, self.iv + ciphertext, hashlib.sha256)
        calculated_hmac = h.digest()
        return calculated_hmac[:10] == hmac10
    
    def decrypt_media(self, ciphertext):
        """
        Decrypt the media content using AES-CBC
        
        Args:
            ciphertext (bytes): The encrypted media content
            
        Returns:
            bytes: Decrypted media content
        """
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, self.iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        
        # Remove PKCS7 padding
        return unpad(decrypted_padded, AES.block_size)
    
    def verify_plaintext_hash(self, decrypted_media):
        """
        Verify the SHA256 hash of the decrypted media
        
        Args:
            decrypted_media (bytes): Decrypted media content
            
        Returns:
            bool: True if hash matches, False otherwise
        """
        calculated_hash = hashlib.sha256(decrypted_media).hexdigest()
        expected_hash = self.plaintext_hash
        
        # First try direct comparison
        if calculated_hash == expected_hash:
            return True
            
        # Try comparing with the base64 decoded version
        try:
            decoded_hash = base64.b64decode(expected_hash).hex()
            return calculated_hash == decoded_hash
        except:
            pass
            
        return False
    
    def cleanup_temp_files(self):
        """
        Remove any temporary files created during processing
        """
        temp_files = [
            f"{self.file_name}.raw", 
            f"{self.file_name}.decrypted"
        ]
        
        for file_path in temp_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    if self.debug_mode:
                        print(f"Failed to remove {file_path}: {str(e)}")
    
    def process_media(self):
        """
        Complete pipeline to download, verify, decrypt, and validate WhatsApp media
            
        Returns:
            tuple: (decrypted_media, success_flag, message)
        """
        temp_files_created = []
        
        try:
            # Step 1: Download file from CDN
            cdn_file = self.download_from_cdn()
            
            # Save raw downloaded file for debugging if needed
            if self.debug_mode and self.keep_temp_files:
                raw_path = f"{self.file_name}.raw"
                with open(raw_path, "wb") as f:
                    f.write(cdn_file)
                temp_files_created.append(raw_path)
            
            # Step 2: Verify encrypted file hash
            if not self.verify_enc_hash(cdn_file):
                return None, False, "Encrypted file hash verification failed"
            
            # Split the cdn_file into ciphertext and hmac10
            hmac10 = cdn_file[-10:]
            ciphertext = cdn_file[:-10]
            
            # Step 3: Validate HMAC
            if not self.validate_hmac(ciphertext, hmac10):
                return None, False, "HMAC validation failed"
            
            # Step 4: Decrypt media content
            decrypted_media = self.decrypt_media(ciphertext)
            
            # Save decrypted media for debugging if needed
            if self.debug_mode and self.keep_temp_files:
                decrypted_path = f"{self.file_name}.decrypted"
                with open(decrypted_path, "wb") as f:
                    f.write(decrypted_media)
                temp_files_created.append(decrypted_path)
            
            # Step 5: Validate decrypted media hash
            if not self.verify_plaintext_hash(decrypted_media):
                # Clean up any temporary files if not keeping them
                if not self.keep_temp_files:
                    for file_path in temp_files_created:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                return None, False, "Plaintext hash verification failed"
            
            return decrypted_media, True, "Media successfully decrypted and verified"
            
        except Exception as e:
            # Clean up any temporary files if not keeping them
            if not self.keep_temp_files:
                for file_path in temp_files_created:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            return None, False, f"Error during processing: {str(e)}"
        
    def save_media(self, output_path=None):
        """
        Process and save the media to a file
        
        Args:
            output_path (str, optional): Path to save the file. If None, uses the original file name
            
        Returns:
            tuple: (success_flag, message)
        """
        decrypted_media, success, message = self.process_media()
        
        if not success:
            return False, message
            
        # If we don't have decrypted media, we can't save anything
        if decrypted_media is None:
            return False, "No decrypted media to save"
            
        # Determine output file path
        if output_path is None:
            output_path = self.file_name
            
        # Save the file
        try:
            with open(output_path, "wb") as f:
                f.write(decrypted_media)
            
            # Clean up any temporary files
            self.cleanup_temp_files()
            
            return True, output_path
        except Exception as e:
            return False, f"Failed to save media: {str(e)}"
            
    def bypass_verifications(self, output_path=None):
        """
        Process the media without hash verifications
        
        Args:
            output_path (str, optional): Path to save the file. If None, uses the original file name
            
        Returns:
            tuple: (success_flag, message)
        """
        try:
            # Download file
            cdn_file = self.download_from_cdn()
            
            # Split the cdn_file into ciphertext and hmac10
            hmac10 = cdn_file[-10:]
            ciphertext = cdn_file[:-10]
            
            # Decrypt media content
            decrypted_media = self.decrypt_media(ciphertext)
            
            # Determine output file path
            if output_path is None:
                output_path = self.file_name
                
            # Save the file
            with open(output_path, "wb") as f:
                f.write(decrypted_media)
            
            # Clean up any temporary files
            self.cleanup_temp_files()
            
            return True, f"Media saved to {output_path} (bypassed verification)"
            
        except Exception as e:
            return False, f"Error during processing: {str(e)}"