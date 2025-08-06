from flask import Flask, request, send_file, render_template, url_for
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from io import BytesIO
from dotenv import load_dotenv
import binascii

load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Get the AES key from the environment
key_hex = os.getenv('AES_KEY')
if not key_hex:
    raise ValueError("AES_KEY not set in environment!")
try:
    KEY = binascii.unhexlify(key_hex)
except binascii.Error:
    raise ValueError("Invalid AES_KEY format, must be hex-encoded")

def encrypt_file(data):
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return iv + encrypted  # Prepend IV to ciphertext

def decrypt_file(data):
    iv = data[:16]
    encrypted_data = data[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_data), AES.block_size)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        
        if uploaded_file.filename:
            file_data = uploaded_file.read()
            encrypted_data = encrypt_file(file_data)
            save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename + ".enc")
            with open(save_path, 'wb') as f:
                f.write(encrypted_data)
                
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".enc")]
    return render_template('index.htm', files=files)

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(filepath, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = decrypt_file(encrypted_data)

    # Send decrypted file as attachment
    original_name = filename.replace('.enc', '')
    return send_file(
        BytesIO(decrypted_data),
        as_attachment=True,
        download_name=original_name
    )

if __name__ == '__main__':
    app.run(debug=True)
