from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import os
import secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Generowanie klucza szyfrowania
def generate_key():
    return Fernet.generate_key()

# Funkcja do szyfrowania pliku
def encrypt_file(file_content, key):
    cipher = Fernet(key)
    encrypted_content = cipher.encrypt(file_content)
    return encrypted_content

# Funkcja do odszyfrowywania pliku
def decrypt_file(encrypted_content, key):
    cipher = Fernet(key)
    decrypted_content = cipher.decrypt(encrypted_content)
    return decrypted_content

# Funkcja do zapisywania zaszyfrowanego pliku na dysku
def save_encrypted_file(file, key):
    encrypted_content = encrypt_file(file.read(), key)
    unique_filename = secrets.token_hex(8) + secure_filename(file.filename)
    encrypted_file_path = os.path.join('zaszyfrowane_pliki', unique_filename)

    with open(encrypted_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_content)

    return encrypted_file_path

# Funkcja do odczytywania zaszyfrowanego pliku z dysku i zapisywania odszyfrowanego
def read_encrypted_file(file_path, key, save_path):
    with open(file_path, 'rb') as encrypted_file:
        encrypted_content = encrypted_file.read()
    decrypted_content = decrypt_file(encrypted_content, key)

    # Zapisz odszyfrowaną zawartość do pliku
    decrypted_file_path = os.path.join(save_path, 'odszyfrowany_plik.txt')
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_content)

    return decrypted_file_path

# Endpoint do przesyłania pliku
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'plik' not in request.files:
        return jsonify({'error': 'Brak pliku w zadaniu'}), 400

    file = request.files['plik']

    if file.filename == '':
        return jsonify({'error': 'Nazwa pliku jest pusta'}), 400

    key = generate_key()
    encrypted_file_path = save_encrypted_file(file, key)
    return jsonify({'wiadomosc': 'Plik zostal pomyslnie przeslany', 'zaszyfrowana_sciezka': encrypted_file_path, 'klucz': key.decode()})

# Endpoint do odszyfrowywania pliku i zapisywania odszyfrowanego
@app.route('/zapisz', methods=['POST'])
def save_decrypted_file():
    data = request.json
    encrypted_file_path = data.get('zaszyfrowana_sciezka')
    key = data.get('klucz')
    save_path = data.get('sciezka_do_zapisu')

    if not encrypted_file_path or not key or not save_path:
        return jsonify({'error': 'Brak scieżki do zaszyfrowanego pliku, klucza lub sciezki do zapisu w zadaniu'}), 400

    decrypted_file_path = read_encrypted_file(encrypted_file_path, key, save_path)
    return jsonify({'wiadomosc': 'Plik zostal pomyslnie odszyfrowany i zapisany w {}'.format(decrypted_file_path)})

if __name__ == '__main__':
    app.run(debug=True)
