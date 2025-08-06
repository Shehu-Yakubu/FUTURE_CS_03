# Generate a Secure AES-256 Key
from Crypto.Random import get_random_bytes
print(get_random_bytes(32).hex())
