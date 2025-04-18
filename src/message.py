import requests

from src.utils import get_env_variable


class WhatsappMessage:
    def __init__(self, api_token=None, api_version=None, whatsapp_phone_id=None):
        """
        Initialize the WhatsappWebhook class with API token and version.
        :param api_token: The API token for authentication.
        :param api_version: The API version for the WhatsApp API.
        :param whatsapp_phone_id: The WhatsApp phone ID for the organisation.
        """

        self.api_token = api_token or get_env_variable('WHATSAPP_TOKEN')
        self.api_version = api_version or get_env_variable('WHATSAPP_VERSION')
        self.whatsapp_phone_id = whatsapp_phone_id or get_env_variable('WHATSAPP_PHONE_ID')

        self.base_url = f"https://graph.facebook.com/{self.api_version}/"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def ask_for_text_location(self, phone, country_code="91", message="Thanks for your order! Tell us what address you'd like this order delivered to."):
        """
        Send a message to ask for the user's address.
        :param phone: The phone number of the user.
        :param country_code: The country code of the user's phone number.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "type": "interactive",
            "interactive": {
                "type": "address_message",
                "body": {
                    "text": "Thanks for your order! Tell us what address you'd like this order delivered to."
                },
                "action": {
                    "name": "address_message",
                    "parameters": {
                        "country" :country_code
                    }
                }
            }
        }

        return self.__send_request(data)
    
    def ask_for_map_location(self, phone, message="Thanks for your order! Tell us what address you'd like this order delivered to."):
        """
        Send a message to ask for the user's address.
        :param phone: The phone number of the user.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "type": "interactive",
            "interactive": {
                "type": "location_request_message",
                "body": {
                    "text": message
                },
                "action": {
                    "name": "send_location"
                }
            }
        }

        return self.__send_request(data)
    
    def send_audio_message(self, phone, file_path):
        """
        Send an audio message to the user.
        :param phone: The phone number of the user.
        :param file_path: The path to the audio file.
        """
        media_id = self.__upload_media(file_path)

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "audio",
            "audio": {
                "id": media_id
            }
        }

        return self.__send_request(data)
    
    def send_contact_message(self, phone, contact_name, contact_phone):
        """
        Send a contact message to the user.
        :param phone: The phone number of the user.
        :param contact_name: The name of the contact.
        :param contact_phone: The phone number of the contact.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "contacts",
            "contacts": [
                {                                        
                    "name": {
                        "formatted_name": contact_name
                    },
                    "phones": [
                        {
                            "phone": contact_phone
                        }
                    ]
                }
            ]
        }

        return self.__send_request(data)
    
    def send_document_message(self, phone, file_path, caption="Here is your document!"):
        """
        Send a document message to the user.
        :param phone: The phone number of the user.
        :param file_path: The path to the document file.
        :param caption: The caption for the document.
        """
        media_id = self.__upload_media(file_path)

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "document",
            "document": {
                "id": media_id,
                "caption": caption,
                "filename": file_path.split("/")[-1]                
            }
        }

        return self.__send_request(data)
    
    def send_image_message(self, phone, file_path, caption="Here is your image!"):
        """
        Send an image message to the user.
        :param phone: The phone number of the user.
        :param file_path: The path to the image file.
        :param caption: The caption for the image.
        """
        media_id = self.__upload_media(file_path)

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "image",
            "image": {
                "id": media_id,
                "caption": caption
            }
        }

        return self.__send_request(data)
    
    def send_cta_message(self, phone, header="This is header", body="This will be your body content", footer="Simplifying Life", cta_text="Click me", cta_url="https://www.google.com"):
        """
        Send a CTA message to the user.
        :param phone: The phone number of the user.
        :param header: The header text for the message.
        :param body: The body text for the message.
        :param footer: The footer text for the message.
        :param cta_text: The text for the call-to-action button.
        :param cta_url: The URL for the call-to-action button.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": {
                "type": "cta_url",
                "header": {
                    "type": "text",
                    "text": header
                },
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": cta_text,
                        "url": cta_url
                    }
                }
            }
        }

        return self.__send_request(data)
    
    def send_flow_message(self, phone, flow_id, flow_mode="published", header="This is header", body="This will be your body content", footer="Simplifying Life", cta_text="Click me", flow_payload={}):
        """
        Send a flow message to the user.
        :param phone: The phone number of the user.
        :param flow_id: The ID of the flow to be sent.
        :param flow_mode: The mode of the flow (published or draft).
        :param header: The header text for the message.
        :param body: The body text for the message.
        :param footer: The footer text for the message.
        :param cta_text: The text for the call-to-action button.
        :param flow_payload: The payload for the flow.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",            
            "to": phone,
            "type": "interactive",
            "interactive": {                
                "header": {      
                    "type": "text",             
                    "text": header
                },
                "body": {                                
                    "text": body
                }, 
                "type": "flow", 
                "footer": {                                 
                    "text": footer
                },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": 3,
                        "flow_id": flow_id,
                        "mode": flow_mode,
                        "flow_cta": cta_text,
                        "flow_action": "navigate",                        
                    }
                }
            },
        }

        if flow_payload:
            data["interactive"]["action"]["parameters"]["flow_action_payload"] = flow_payload 

        return self.__send_request(data)
    
    def send_interactive_list_message(self, phone, sections, header="This is header", body="This will be your body content", footer="Simplifying Life", button_text="Click me"):
        """
        Send an interactive list message to the user.
        :param phone: The phone number of the user.
        :param header: The header text for the message.
        :param body: The body text for the message.
        :param footer: The footer text for the message.
        :param button_text: The text for the button.
        :param sections: 
            sections_example = [
                {
                    "title": "Section 1",
                    "rows": [
                        {
                            "id": "row_1",
                            "title": "Row 1"
                        },
                        {
                            "id": "row_2",
                            "title": "Row 2"
                        }
                    ]
                },
                {
                    "title": "Section 2",
                    "rows": [
                        {
                            "id": "row_3",
                            "title": "Row 3"
                        }
                    ]
                }
            ]
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header
                },
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }

        return self.__send_request(data)
    
    def send_interactive_location_message(self, phone, latitude, longitude, location_name="", location_address=""):
        """
        Send an interactive location message to the user.
        :param phone: The phone number of the user.
        :param latitude: The latitude of the location.
        :param longitude: The longitude of the location.
        :param location_name: The name of the location.
        :param location_address: The address of the location.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "name": location_name,
                "address": location_address
            }
        }

        return self.__send_request(data)
    
    def send_sticker_message(self, phone, file_path):

        media_id = self.__upload_media(file_path)

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "sticker",
            "image": {
                "id": media_id,
            }
        }

        return self.__send_request(data)
    
    def send_text_message(self, phone, message):
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {                
                "body": message
            }
        }

        return self.__send_request(data)
    
    def send_template_text_message(self, phone, template_name, template_language="en_US", template_components=None):
        """
        Send a template text message to the user.
        :param phone: The phone number of the user.
        :param template_name: The name of the template.
        :param template_language: The language of the template.
        :param template_components: The components of the template.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": template_language
                }
            }
        }

        if template_components:
            data["template"]["components"] = template_components

        return self.__send_request(data)
    
    def send_template_media_message(self, phone, template_name, media_url, template_language="en_US", template_components=None):
        """
        Send a template media message to the user.
        :param phone: The phone number of the user.
        :param template_name: The name of the template.
        :param media_url: The URL of the media.
        :param template_language: The language of the template.
        :param template_components: The components of the template.
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": template_language
                },
                "components": [
                    {
                        "type": "header",
                        "image": {
                            "link": media_url
                        }
                    }
                ]
            }
        }

        if template_components:
            data["template"]["components"].append(template_components)

        return self.__send_request(data)
    
    def send_video_message(self, phone, file_path):
        media_id = self.__upload_media(file_path)

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "video",
            "video": {
                "id": media_id
            }
        }

        return self.__send_request(data)

    def __upload_media(self, file_path):
        """
        Upload media to the WhatsApp API.
        :param file_path: The path to the media file.
        :return: The media ID of the uploaded file.
        """
        url = f"{self.base_url}/{self.whatsapp_phone_id}/media"
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, headers=self.headers, files=files)

        if response.status_code == 200:
            return response.json()['id']
        else:
            raise ValueError(response.content)

    def __send_request(self, data):
        response = requests.post(f"{self.base_url}/{self.whatsapp_phone_id}/messages", headers=self.headers, json=data)

        if response.status_code == 200:                  
            return response.json()
        else:
            raise ValueError(response.content)    