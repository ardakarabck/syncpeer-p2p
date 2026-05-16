import socket
import os
import json
import time

# ============================================================
# SİSTEM SABİTLERİ (FunctionalSpecification.pdf)
# ============================================================
BROADCAST_IP = "192.168.1.255"
UDP_PORT = 6000  # Dinleme portu 6000'dir
BROADCAST_PERIOD = 8  # 8 saniye
CHUNK_COUNT = 3  # Sabit 3 

class ChunkAnnouncer:
    def __init__(self):
        self.username = ""
        self.hosted_chunks = []
        self.user_log_file = "user_info.txt"
        self.chunk_dir = "."  # Klasör okuma için dinamik olarak güncellenecek

    # ─────────────────────────────────────────────
    # TASK 1 — Req 2.1.0-A: Startup & Folder Reading (Modified)
    # ─────────────────────────────────────────────
    # Step 1: Prompt user to enter their username via terminal input.
    # Step 2: Prompt user to enter the path/name of the folder they will initially host.
    # Step 3: Scan the folder to read existing image files instead of splitting.
    #         Assume every folder always has exactly 3 chunks/files.
    # Step 4: Store the username locally (write to a local text file or keep in memory).
    # Step 5: Print terminal message: state number of chunks created and that
    #         the process is starting to announce these files.
    def startup_and_split(self):
        # Step 1: Kullanıcı adı girişi
        self.username = input("Enter your username: ").strip()
        
        # Step 2: Klasör yolu girişi (Tek dosya yerine resimlerin olduğu klasör)
        folder_path = input("Enter the path of the folder containing the images (e.g., images): ").strip()
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            print(f"Error: Folder '{folder_path}' not found or is not a directory.")
            return False

        # Task 3'ün doğru dizine bakması için chunk_dir güncelleniyor
        self.chunk_dir = folder_path

        # Step 3: Klasör içindeki dosyaları kontrol etme
        all_files = [f for f in os.listdir(self.chunk_dir) if os.path.isfile(os.path.join(self.chunk_dir, f)) and not f.startswith('.')]
        
        if len(all_files) == 0:
            print(f"Error: No image files found in '{folder_path}'.")
            return False

        # Step 4: Kullanıcı adını yerel olarak saklama
        with open(self.user_log_file, "w") as log:
            log.write(self.username)

        # Step 5: Terminal bilgilendirmesi
        print(f"\n[System] {len(all_files)} chunks/files detected in target folder.")
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
        """Dizindeki mevcut parça isimlerini (resimleri) okur."""
        # Step 1 & 2: Belirtilen dizindeki tüm dosyaları oku
        all_files = os.listdir(self.chunk_dir)
        
        # Step 3: Klasör içindeki gerçek resim dosyalarını listeye ekle
        self.hosted_chunks = [f for f in all_files if os.path.isfile(os.path.join(self.chunk_dir, f)) and not f.startswith('.')]
        
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
        # Step 1: UDP Soket oluşturma
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Step 2: Broadcast seçeneğini etkinleştir
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            while True:
                try:
                    # Task 3: Güncel parça listesini oku
                    chunks_list = self.get_hosted_chunks()

                    # Task 4 Step 1: JSON Sözlüğü (Kritik anahtar isimleri)
                    payload = {
                        "username": self.username.lower().replace("_", ""), 
                        "chunks": chunks_list      
                    }
                    
                    # Task 4 Step 2 & 3: Serialize ve Encode
                    message = json.dumps(payload).encode('utf-8')
                    
                    # Task 2 Step 3 Gönderim (192.168.1.255:6000)
                    s.sendto(message, (BROADCAST_IP, UDP_PORT))
                    
                    print(f"[{time.strftime('%H:%M:%S')}] Duyuru gönderildi: {payload}")
                    
                    # Task 2 Step 5: 8 saniye bekle
                    time.sleep(BROADCAST_PERIOD)
                    
                except KeyboardInterrupt:
                    print("\n[SİSTEM] Duyuru durduruldu.")
                    break

if __name__ == "__main__":
    announcer = ChunkAnnouncer()
    if announcer.startup_and_split():
        announcer.start_announcing()
