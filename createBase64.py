import json
import base64

def read_and_base64_encode_credentials(credentials_file_path):
    try:
        # Read JSON data from the credentials file
        with open(credentials_file_path, 'r') as file:
            credentials = json.load(file)
        
        # Convert the JSON data to a string
        credentials_str = json.dumps(credentials)
        
        # Encode the string as bytes
        credentials_bytes = credentials_str.encode('utf-8')
        
        # Base64 encode the bytes
        encoded_credentials = base64.b64encode(credentials_bytes).decode('utf-8')
        
        print(encoded_credentials)
        return encoded_credentials
    except FileNotFoundError:
        print(f"File not found: {credentials_file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

read_and_base64_encode_credentials('token.json')

