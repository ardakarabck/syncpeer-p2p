import socket
import os
import json
import time
import math

# ============================================================
# SİSTEM SABİTLERİ (FunctionalSpecification.pdf)
# ============================================================
BROADCAST_IP = "192.168.1.255"
UDP_PORT = 6000  # Req 2.2.0-A: Dinleme portu 6000'dir
BROADCAST_PERIOD = 8  # Req 2.1.0-B: 8 saniye
CHUNK_COUNT = 3  # Req 2.1.0-A: Sabit 3 parça[cite: 1]

class ChunkAnnouncer:
    def __init__(self):
        self.username = ""
        self.hosted_chunks = []
        self.user_log_file = "user_info.txt"
        self.chunk_dir = "."  # Task 3 için gerekli dizin tanımı[cite: 1]

    # ─────────────────────────────────────────────
    # TASK 1 — Req 2.1.0-A: Startup & File Splitting
    # ─────────────────────────────────────────────
    # Step 1: Prompt user to enter their username via terminal input.
    # Step 2: Prompt user to enter the path/name of the file they will initially host.
    # Step 3: Call the provided splitting function to divide the file into N-byte chunks.
    #         Each chunk saved as a separate file with indexed naming (no .png suffix).
    #         Assume every file always has exactly 3 chunks.
    # Step 4: Store the username locally (write to a local text file or keep in memory).
    # Step 5: Print terminal message: state number of chunks created and that
    #         the process is starting to announce these files.
    def startup_and_split(self):
        # Step 1: Kullanıcı adı girişi[cite: 1]
        self.username = input("Enter your username: ").strip()
        
        # Step 2: Dosya yolu girişi[cite: 1]
        file_path = input("Enter the path of the file to host: ").strip()
        
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return False

        # Step 3: Dosyayı 3 parçaya bölme[cite: 1]
        file_size = os.path.getsize(file_path)
        chunk_size = math.ceil(file_size / CHUNK_COUNT)
        base_name = os.path.basename(file_path).split('.')[0]

        with open(file_path, 'rb') as f:
            for i in range(1, CHUNK_COUNT + 1):
                chunk_data = f.read(chunk_size)
                # İndeksli isimlendirme (suffix yok)[cite: 1]
                chunk_name = f"{base_name}_{i}"
                
                with open(chunk_name, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                self.hosted_chunks.append(chunk_name)

        # Step 4: Kullanıcı adını yerel olarak saklama[cite: 1]
        with open(self.user_log_file, "w") as log:
            log.write(self.username)

        # Step 5: Terminal bilgilendirmesi[cite: 1]
        print(f"\n[System] {len(self.hosted_chunks)} chunks created.")
        print(f"[System] Starting to announce files for user: {self.username}")
        return True

    # ─────────────────────────────────────────────
    # TASK 3 — Req 2.1.0-C: Read Hosted Chunk Names from Directory
    # ─────────────────────────────────────────────
    # Step 1: Point to the directory where chunk files are stored.
    # Step 2: Read all filenames in that directory.
    # Step 3: Collect chunk names into a Python list.
    # Step 4: This list feeds directly into the broadcast JSON payload (Task 4).
    def get_hosted_chunks(self):
        """Dizindeki mevcut parça isimlerini okur."""
        # Belirtilen dizindeki tüm dosyaları oku[cite: 1]
        all_files = os.listdir(self.chunk_dir)
        
        # Sadece bizim oluşturduğumuz parçaları (indeks içerenleri) listeye ekle[cite: 1]
        self.hosted_chunks = [f for f in all_files if "_" in f and "." not in f]
        return self.hosted_chunks

    # ─────────────────────────────────────────────
    # TASK 2 — Req 2.1.0-B: Periodic UDP Broadcast
    # ─────────────────────────────────────────────
    # Step 1: Create a UDP socket.
    # Step 2: Enable SO_BROADCAST socket option.
    # Step 3: Target broadcast IP: 192.168.1.255.
    # Step 4: Period: send once every 8 seconds.
    # Step 5: Run a loop — build message, send, sleep 8 seconds, repeat.
    
    # ─────────────────────────────────────────────
    # TASK 4 — Req 2.1.0-D: Construct & Send Broadcast JSON
    # ─────────────────────────────────────────────
    # Step 1: Build a dict with exactly two keys:
    #           key "username" (all lowercase, no underscore) → username string
    #           key "chunks"  (all lowercase)                 → list of chunk name strings
    # Step 2: Serialize dict to JSON string via json.dumps().
    # Step 3: Encode JSON string to bytes (UTF-8).
    # Step 4: Send encoded bytes via UDP broadcast socket to 192.168.1.255 on port 6000.
    def start_announcing(self):
        # Step 1: UDP Soket oluşturma[cite: 1]
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Step 2: Broadcast seçeneğini etkinleştir[cite: 1]
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            while True:
                try:
                    # Task 3: Güncel parça listesini oku[cite: 1]
                    chunks_list = self.get_hosted_chunks()

                    # Task 4 Step 1: JSON Sözlüğü (Kritik anahtar isimleri)[cite: 1]
                    payload = {
                        "username": self.username, # Req 2.1.0-D: Hepsi küçük harf[cite: 1]
                        "chunks": chunks_list      # Req 2.1.0-D: Hepsi küçük harf[cite: 1]
                    }
                    
                    # Task 4 Step 2 & 3: Serialize ve Encode[cite: 1]
                    message = json.dumps(payload).encode('utf-8')
                    
                    # Task 2 Step 3 & 4: Gönderim (192.168.1.255:6000)[cite: 1]
                    s.sendto(message, (BROADCAST_IP, UDP_PORT))
                    
                    print(f"[{time.strftime('%H:%M:%S')}] Duyuru gönderildi: {payload}")
                    
                    # Task 2 Step 5: 8 saniye bekle[cite: 1]
                    time.sleep(BROADCAST_PERIOD)
                    
                except KeyboardInterrupt:
                    print("\n[SİSTEM] Duyuru durduruldu.")
                    break

# ============================================================
# ANA ÇALIŞTIRMA BLOĞU
# ============================================================
if __name__ == "__main__":
    announcer = ChunkAnnouncer()
    if announcer.startup_and_split():
        announcer.start_announcing()