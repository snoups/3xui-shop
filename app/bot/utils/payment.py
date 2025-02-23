import base64
import hashlib
import json


async def generate_signature(payload: dict, api_key: str) -> str:
    encoded = json.dumps(payload).encode()
    base64_payload = base64.b64encode(encoded).decode()
    sign = hashlib.md5((base64_payload + api_key).encode()).hexdigest()
    return sign