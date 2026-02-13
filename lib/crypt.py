import base64

def ToBase64String(text):
    byte_data = text.encode('utf-8')
    base64_encoded = base64.b64encode(byte_data)
    return base64_encoded.decode('utf-8')

def FromBase64String(text):
    decoded_bytes = base64.b64decode(text)
    return decoded_bytes.decode('utf-8')