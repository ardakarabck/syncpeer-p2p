import socket
import os
import json
import time
import math

# ============================================================
# SİSTEM SABİTLERİ (FunctionalSpecification.pdf)
# ============================================================

BROADCAST_IP = "127.0.0.1"
# BROADCAST_IP = "192.168.1.255" will be changed according to the end-hosts IP addr
UDP_PORT = 6000  # Dinleme portu 6000'dir
BROADCAST_PERIOD = 8  # 8 saniye
CHUNK_COUNT = 3  # Sabit 3

# ─────────────────────────────────────────────
# TASK 1 — Req 2.1.0-A: Split Original File Into 3 Chunks
# ─────────────────────────────────────────────
# Step 1: Receive the original file path and the chunk directory.
# Step 2: If the chunk directory does not exist, create it.
# Step 3: Extract the original file name, pure name, and extension.
#         Example: tree.png → pure name: tree, extension: .png
# Step 4: Read the original file as binary bytes.
# Step 5: Divide the file bytes into exactly 3 chunks.
# Step 6: Save the chunks with indexed names:
#         tree_1.png, tree_2.png, tree_3.png
# Step 7: Return the created chunk names so they can be announced.

def split_chunks(file_path, chunk_dir):

    if not os.path.exists(chunk_dir):
        os.makedirs(chunk_dir)

    file_name = os.path.basename(file_path)       # tree.png
    pure_name = os.path.splitext(file_name)[0]    # tree
    extension = os.path.splitext(file_name)[1]    # .png

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    total_size = len(file_bytes)
    chunk_size = math.ceil(total_size / CHUNK_COUNT)
    chunk_names = []

    for i in range(CHUNK_COUNT):
        start = i * chunk_size
        end = min(start + chunk_size, total_size)

        chunk_data = file_bytes[start:end]
        chunk_name = f"{pure_name}_{i + 1}{extension}"
        chunk_path = os.path.join(chunk_dir, chunk_name)

        with open(chunk_path, "wb") as chunk_file:
            chunk_file.write(chunk_data)
        chunk_names.append(chunk_name)

    return chunk_names
# ─────────────────────────────────────────────
# TASK 2 — Req 2.1.0-A: Startup & Initial Hosting Setup
# ─────────────────────────────────────────────
# Step 1: Prompt user to enter their username via terminal input.
# Step 2: Check that username is not empty.
# Step 3: Prompt user to enter the original file they will initially host.
#         Example: test_images/tree.png
# Step 4: Check that the entered file exists and is really a file.
# Step 5: Prompt user to enter the folder where chunks will be stored.
#         Example: test_images
# Step 6: Split the original file into exactly 3 chunks.
# Step 7: Store the username locally in user_info.txt.
# Step 8: Print terminal message stating number of chunks created and that
#         the process is starting to announce these chunks.
def startup_and_split():

    # Step 1: Kullanıcı adı girişi
    username = input("Enter your username: ").strip()
    if username == "":
        print("Error: Username cannot be empty.")
        return None, None

    # Step 2: Orijinal dosya yolu girişi
    file_path = input("Enter the original file to host (e.g., test_images/tree.png): ").strip()
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None, None

    # Step 3: Chunk'ların saklanacağı klasör yolu girişi
    folder_path = input("Enter the folder where chunks will be stored (e.g., test_images): ").strip()
    if folder_path == "":
        folder_path = "test_images"

    # Task 3'ün doğru dizine bakması için chunk_dir güncelleniyor
    chunk_dir = folder_path

    # Step 4: Orijinal dosyayı 3 chunk'a bölme
    hosted_chunks = split_chunks(file_path, chunk_dir)

    # Step 5: Kullanıcı adını yerel olarak saklama
    with open("user_info.txt", "w") as log:
        log.write(username)

    # Step 6: Terminal bilgilendirmesi
    print(f"\n[System] {len(hosted_chunks)} chunks/files created in target folder.")
    print(f"[System] Starting to announce chunks for user: {username}")
    return username, chunk_dir

# ─────────────────────────────────────────────
# TASK 3 — Req 2.1.0-C: Read Hosted Chunk Names from Directory
# ─────────────────────────────────────────────
# Step 1: Point to the directory where chunk files are stored.
# Step 2: Read all filenames in that directory.
# Step 3: Ignore hidden files and folders.
# Step 4: Only collect indexed chunk files.
#         Example: tree_1.png, tree_2.png, tree_3.png
# Step 5: Do not announce the original full file.
#         Example: tree.png should NOT be announced.
# Step 6: This chunk list feeds directly into the broadcast JSON payload.
def get_hosted_chunks(chunk_dir):
    """Dizindeki mevcut parça isimlerini (chunk dosyalarını) okur."""
    # Step 1 & 2: Belirtilen dizindeki tüm dosyaları oku
    all_files = os.listdir(chunk_dir)

    # Step 3: Klasör içindeki gerçek chunk dosyalarını listeye ekle
    hosted_chunks = []
    for f in all_files:
        file_path = os.path.join(chunk_dir, f)

        if not os.path.isfile(file_path):
            continue

        if f.startswith('.'):
            continue

        name_without_ext = os.path.splitext(f)[0]

        if "_" in name_without_ext:
            last_part = name_without_ext.rsplit("_", 1)[1]
            if last_part.isdigit():
                hosted_chunks.append(f)
    return hosted_chunks
# ─────────────────────────────────────────────
# TASK 4 — Req 2.1.0-B: Periodic UDP Broadcast
# ─────────────────────────────────────────────
# Step 1: Create a UDP socket.
# Step 2: Enable SO_BROADCAST socket option.
# Step 3: Target broadcast IP: 192.168.1.255.
#         For local testing, 127.0.0.1 can be used.
# Step 4: Period: send once every 8 seconds.
# Step 5: Run a loop — build message, send, sleep 8 seconds, repeat.
# ─────────────────────────────────────────────
# TASK 5 — Req 2.1.0-D: Construct & Send Broadcast JSON
# ─────────────────────────────────────────────
# Step 1: Build a dict with exactly two keys:
#           key "username" (all lowercase, no underscore) → username string
#           key "chunks"  (all lowercase)                 → list of chunk name strings
# Step 2: Serialize dict to JSON string via json.dumps().
# Step 3: Encode JSON string to bytes (UTF-8).
# Step 4: Send encoded bytes via UDP broadcast socket to 192.168.1.255 on port 6000.
def start_announcing(username, chunk_dir):
    # Step 1: UDP Soket oluşturma
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Step 2: Broadcast seçeneğini etkinleştir
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            try:
                # Task 3: Güncel parça listesini oku
                chunks_list = get_hosted_chunks(chunk_dir)

                # Task 5 Step 1: JSON Sözlüğü (Kritik anahtar isimleri)
                payload = {
                    "username": username,
                    "chunks": chunks_list
                }

                # Task 5 Step 2 & 3: Serialize ve Encode
                message = json.dumps(payload).encode('utf-8')

                # Task 4 Step 3 Gönderim (192.168.1.255:6000)
                s.sendto(message, (BROADCAST_IP, UDP_PORT))
                print(f"[{time.strftime('%H:%M:%S')}] Duyuru gönderildi: {payload}")

                # Task 4 Step 5: 8 saniye bekle
                time.sleep(BROADCAST_PERIOD)
            except KeyboardInterrupt:
                print("\n[SİSTEM] Duyuru durduruldu.")
                break

# ─────────────────────────────────────────────
# MAIN — Program Entry Point
# ─────────────────────────────────────────────
# Step 1: Run startup setup.
# Step 2: If username and chunk directory are valid, start periodic announcements.
if __name__ == "__main__":
    username, chunk_dir = startup_and_split()
    if username is not None and chunk_dir is not None:
        start_announcing(username, chunk_dir)
