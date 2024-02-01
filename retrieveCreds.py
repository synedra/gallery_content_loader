import json
import base64

def decode_and_parse_credentials(encoded_credentials):
    try:
        # Decode the base64 string to bytes
        credentials_bytes = base64.b64decode(encoded_credentials)
        
        # Convert bytes to a JSON string
        credentials_str = credentials_bytes.decode('utf-8')
        
        # Parse the JSON string into a dictionary
        credentials = json.loads(credentials_str)
        
        return credentials
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage:
encoded_credentials = "eyJ0b2tlbiI6ICJ5YTI5LmEwQWZCX2J5REVELVFYcjl3eFVwU08tb1hzQ1h6b1U4cGVEVV9DN01faHc1UXhTU19nakIxWWFGNTdaSHByaDJWM0FSZEJkRUx1cC1ab3pYRE1lRDRrSGhYcHNnX0ZNZTNvS1Mtano4ODJud2RpTVNOaXIwUmJSbURDUUN6Q1JLV3FvSGlPMUk1VWVMa0haekM0WC1UNHNIdmRIdTBhUnZva1pIVGwyZ2FDZ1lLQVlZU0FSRVNGUUhHWDJNaWlnVVE1U0kwUTIyeVZKdFFhYjhvZkEwMTczIiwgInJlZnJlc2hfdG9rZW4iOiAiMS8vMDZ4S1JDM1FGWjJqdkNnWUlBUkFBR0FZU053Ri1MOUlyV3VaRkNaVkdCVFF5MkZSNlBZN1FPbEZ5ZHk0aTFWY2czZlR6X0FUNEw3V1pSQUk5WWFtTFRfYWpPN3pQSEltOTQ4USIsICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLCAiY2xpZW50X2lkIjogIjUxNzM5MTE0NzQ2MC0xZDducGdmNjBwajYwb3J1c2ZyNXBmdThuZmZrYWlycS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsICJjbGllbnRfc2VjcmV0IjogIkdPQ1NQWC1kLXFfV1ZCNEVPdGc5eGpOTERsMGk3MlV4Smw0IiwgInNjb3BlcyI6IFsiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vYXV0aC95b3V0dWJlLnJlYWRvbmx5Il0sICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iLCAiZXhwaXJ5IjogIjIwMjQtMDEtMzFUMTk6NDg6MzIuMTE4MzA3WiJ9"  # Replace with your encoded credentials
decoded_credentials = decode_and_parse_credentials(encoded_credentials)

if decoded_credentials:
    print("Decoded Credentials:")
    print(decoded_credentials)
else:
    print("Failed to decode and parse credentials.")