# whatsapp_python

`whatsapp_python` is a Python package designed to simplify the integration and management of WhatsApp messaging flows. It provides a robust set of features for sending messages, handling media, and ensuring secure communication through encryption.

## Features

- **Message Sending**: Send text, audio, video, and document messages seamlessly via WhatsApp.
- **Interactive Messages**: Handle interactive message types such as location requests and call-to-action (CTA) buttons.
- **Media Management**: Download and decrypt WhatsApp media files with ease.
- **Encryption Support**: Encrypt and decrypt data to ensure secure communication.

## Installation

Install the package using pip:

```bash
pip install whatsapp_python
```

## Usage

### Sending a Text Message

The following example demonstrates how to send a text message using the `WhatsappMessage` class:

```python
from whatsapp_python import WhatsappMessage

# Initialize the WhatsappMessage object with your credentials
whatsapp = WhatsappMessage(
    api_token="your_api_token",
    api_version="v15.0",
    whatsapp_phone_id="your_phone_id"
)

# Send a text message
response = whatsapp.send_text_message(
    phone="1234567890",
    message="Hello, World!"
)

# Print the response
print(response)
```

### Decrypting Media

The `WhatsappMedia` class allows you to download and decrypt media files securely. Here's an example:

```python
from whatsapp_python import WhatsappMedia

# Define media metadata
media_data = {
    "file_name": "example.jpg",
    "media_id": "media_id",
    "cdn_url": "https://cdn.example.com/media",
    "encryption_metadata": {
        "encryption_key": "base64_key",
        "hmac_key": "base64_hmac",
        "iv": "base64_iv",
        "plaintext_hash": "hash",
        "encrypted_hash": "hash"
    }
}

# Initialize the WhatsappMedia object
media = WhatsappMedia(media_data)

# Save the decrypted media to a file
success, message = media.save_media(output_path="output.jpg")

# Print the result
print(message)
```

### Handling Interactive Messages

You can also handle interactive messages such as location requests or CTA buttons. Here's a quick example:

```python
from whatsapp_python import WhatsappInteractive

# Initialize the WhatsappInteractive object
interactive = WhatsappInteractive(
    api_token="your_api_token",
    api_version="v15.0",
    whatsapp_phone_id="your_phone_id"
)

# Send a location request
response = interactive.send_location_request(
    phone="1234567890",
    latitude=37.7749,
    longitude=-122.4194,
    name="San Francisco",
    address="California, USA"
)

# Print the response
print(response)
```

## Documentation

For detailed documentation, including advanced usage and API references, please visit the [official documentation](https://https://github.com/sarthaksnh5/whatsapp_python).

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Support

If you encounter any issues or have questions, feel free to open an issue on the [GitHub repository](https://https://github.com/sarthaksnh5/whatsapp_python) or contact us at sarthaksnh5@gmail.com.
