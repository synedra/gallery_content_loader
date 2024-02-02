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
        
        return json.dumps(credentials)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage:
encoded_credentials = "ewogICJ0b2tlbiI6ICJ5YTI5LmEwQWZCX2J5REVELVFYcjl3eFVwU08tb1hzQ1h6b1U4cGVEVV9DN01faHc1UXhTU19nakIxWWFGNTdaSHByaDJWM0FSZEJkRUx1cC1ab3pYRE1lRDRrSGhYcHNnX0ZNZTNvS1Mtano4ODJud2RpTVNOaXIwUmJSbURDUUN6Q1JLV3FvSGlPMUk1VWVMa0haekM0WC1UNHNIdmRIdTBhUnZva1pIVGwyZ2FDZ1lLQVlZU0FSRVNGUUhHWDJNaWlnVVE1U0kwUTIyeVZKdFFhYjhvZkEwMTczIiwKICAicmVmcmVzaF90b2tlbiI6ICIxLy8wNnhLUkMzUUZaMmp2Q2dZSUFSQUFHQVlTTndGLUw5SXJXdVpGQ1pWR0JUUXkyRlI2UFk3UU9sRnlkeTRpMVZjZzNmVHpfQVQ0TDdXWlJBSTlZYW1MVF9hak83elBISW05NDhRIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiY2xpZW50X2lkIjogIjUxNzM5MTE0NzQ2MC0xZDducGdmNjBwajYwb3J1c2ZyNXBmdThuZmZrYWlycS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsCiAgImNsaWVudF9zZWNyZXQiOiAiR09DU1BYLWQtcV9XVkI0RU90Zzl4ak5MRGwwaTcyVXhKbDQiLAogICJzY29wZXMiOiBbCiAgICAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vYXV0aC95b3V0dWJlLnJlYWRvbmx5IgogIF0sCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIsCiAgImV4cGlyeSI6ICIyMDI0LTAxLTMxVDE5OjQ4OjMyLjExODMwN1oiCn0K"
decoded_credentials = decode_and_parse_credentials(encoded_credentials)

if decoded_credentials:
    print("Decoded Credentials:")
    print(decoded_credentials)
else:
    print("Failed to decode and parse credentials.")