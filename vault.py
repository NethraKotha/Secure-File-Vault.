import os
import shutil
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime

# Load key
def load_key():
    return open("key.key", "rb").read()

key = load_key()
fernet = Fernet(key)

# Logging
def log_action(action):
    with open("logs.txt", "a") as log:
        log.write(f"{datetime.now()} - {action}\n")

# Hash function (NEW FEATURE)
def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

# Encrypt
def encrypt_file(file_path):
    original_hash = file_hash(file_path)

    with open(file_path, "rb") as file:
        data = file.read()

    encrypted = fernet.encrypt(data)

    filename = os.path.basename(file_path)
    save_path = "vault_data/" + filename + ".enc"

    with open(save_path, "wb") as f:
        f.write(encrypted)

    # Save hash
    with open("vault_data/" + filename + ".hash", "w") as f:
        f.write(original_hash)

    print("File encrypted successfully!")
    log_action("Encrypted " + filename)

# Decrypt
def decrypt_file(filename):
    path = "vault_data/" + filename

    with open(path, "rb") as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)

    original_name = filename[:-4]
    output = "vault_data/decrypted_" + original_name

    with open(output, "wb") as f:
        f.write(decrypted)

    # Verify integrity
    new_hash = file_hash(output)
    hash_file = "vault_data/" + original_name + ".hash"

    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            old_hash = f.read()

        if new_hash == old_hash:
            print("File verified ✔ (no tampering)")
        else:
            print("⚠ File modified or corrupted!")

    print("File decrypted successfully!")
    log_action("Decrypted " + filename)

# Backup
def backup():
    shutil.copytree("vault_data", "backup", dirs_exist_ok=True)
    print("Backup done!")
    log_action("Backup created")

# Login system
attempts = 0
PASSWORD = "1234"

def login():
    global attempts
    while attempts < 3:
        pwd = input("Enter password: ")
        if pwd == PASSWORD:
            print("Access granted")
            return True
        else:
            attempts += 1
            print("Wrong password")

    print("System locked!")
    log_action("Intrusion detected")
    return False

# Menu
def menu():
    while True:
        print("\n1. Encrypt")
        print("2. Decrypt")
        print("3. Backup")
        print("4. Exit")

        ch = input("Enter choice: ")

        if ch == "1":
            path = input("Enter file path: ").strip().replace('"', '')
            if os.path.exists(path):
                encrypt_file(path)
            else:
                print("File not found ❌")

        elif ch == "2":
            name = input("Enter file name (.enc): ")
            decrypt_file(name)

        elif ch == "3":
            backup()

        elif ch == "4":
            break

        else:
            print("Invalid choice")

# Run
if login():
    menu()
