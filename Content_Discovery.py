# ============================================================
# Content_Discovery Tasks
# ============================================================

# ─────────────────────────────────────────────
# TASK 1 — Req 2.2.0-A: Listen for UDP Broadcasts
# ─────────────────────────────────────────────
# Step 1: Create a UDP socket.
# Step 2: Bind it to port 6000 (listen on all interfaces).
# Step 3: Enter a continuous receive loop using recvfrom().

# ─────────────────────────────────────────────
# TASK 2 — Req 2.2.0-B: Parse Each Incoming Broadcast
# ─────────────────────────────────────────────
# Step 1: Decode received bytes to string (UTF-8).
# Step 2: Parse string as JSON using json.loads() → extract "username" and "chunks".
# Step 3: Extract sender IP address from the recvfrom() return value (address tuple).

# ─────────────────────────────────────────────
# TASK 3 — Req 2.2.0-C: Maintain IP-to-Username Dictionary
# ─────────────────────────────────────────────
# Step 1: Maintain a dict: key = sender IP address, value = username.
# Step 2: On each received broadcast, insert/update: ip_to_user[sender_ip] = username.
# Step 3: Persist this dict to a shared local text file so Chunk Uploader
#         and Chunk Downloader can read it.
# Step 4: Whenever printing "from whom" in any component, look up this dict
#         to display username instead of raw IP.

# ─────────────────────────────────────────────
# TASK 4 — Req 2.2.0-D: Maintain Content Dictionary (chunk → user list)
# ─────────────────────────────────────────────
# Step 1: Maintain a separate content dict:
#         key = chunk name (e.g., "forest 1"), value = list of usernames holding that chunk.
# Step 2: For each chunk name in received "chunks" list:
#         if chunk name not in dict → create new entry with [username]
#         if chunk name already in dict → append username if not already present.
# Step 3: Persist this content dict to a shared local text file so
#         Chunk Downloader can read it.

# ─────────────────────────────────────────────
# TASK 5 — Req 2.2.0-E: Maintain Username-to-IP Dictionary
# ─────────────────────────────────────────────
# Step 1: Maintain a third dict: key = username, value = IP address.
# Step 2: On each broadcast, insert/update: user_to_ip[username] = sender_ip.
# Step 3: This dict is used by Chunk Downloader to resolve which IP to open
#         a TCP session with when a chunk owner's username is known.
# Step 4: Persist to a shared local text file accessible by Chunk Downloader.

# ─────────────────────────────────────────────
# TASK 6 — Req 2.2.0-F: Console Display on Each Insertion
# ─────────────────────────────────────────────
# Step 1: After every update to the content dictionary, print to console:
#         "<username> : <chunk1>, <chunk2>, <chunk3>"
#         Example: "Ece : vid 1, vid 2, vid 3"
# Step 2: This must trigger on every insertion, not on a timer.

# ─────────────────────────────────────────────
# TASK 7 — Req 2.2.0-G: Wipe Content Dictionary Every Minute
# ─────────────────────────────────────────────
# Step 1: Run a background timer/thread that fires every 60 seconds.
# Step 2: On each timer tick: clear the content dictionary entirely.
# Step 3: Also overwrite the shared content dictionary text file with empty/reset state.

import socket
import json
import time
import threading
PORT = 6000

# dictionaries to be used by task3,4,and 5
ip_to_user = {}
content_dict = {}
user_to_ip = {}

dict_lock = threading.Lock()     # Thread güvenliği için kilit mekanizması

# helper function to save a dictionary into a shared text file
def save(d, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(d, indent=2))


def wipe_content_worker():
    global content_dict
    while True:
        time.sleep(60)  # 60 saniye boyunca arka planda bekler
        with dict_lock:  # Ana döngü ile dosya çakışmasını engellemek için kilitler
            content_dict.clear()
            save(content_dict, "content_dict.txt")
            print("Content dictionary wiped")

# Arka plan thread'ini daemon modunda başlatıyoruz
wipe_thread = threading.Thread(target=wipe_content_worker, daemon=True)
wipe_thread.start()

# task1 
cD = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cD.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
cD.bind(("", PORT))

print("Content Discovery is listening on port 6000")

while True:
    try:
        msg, address = cD.recvfrom(4096)
        ip = address[0]                                 # task2 Step 3
        msg = msg.decode("utf-8")                       # task2 Step 1
        data = json.loads(msg)                          # task2 Step 2
        username = data["username"]               
        chunks = data["chunks"]                      

        # Paylaşılan kaynakları (Sözlükler ve Dosyalar) güncellerken kilidi aktif ediyoruz
        with dict_lock:
            ip_to_user[ip] = username                                # task3 
            save(ip_to_user, "ip_to_user.txt")

            for chunk in chunks:                                      # task4
                if chunk not in content_dict:
                    content_dict[chunk] = [username]
                else:
                    if username not in content_dict[chunk]:
                        content_dict[chunk].append(username)

            save(content_dict, "content_dict.txt")

            user_to_ip[username] = ip                         # task5
            save(user_to_ip, "user_to_ip.txt")

            print(username, ":", ", ".join(chunks))          # task6

    except json.JSONDecodeError:           # ignore messages that are not valid JSON
        pass
    except KeyError:                       # ignore JSON messages that do not have username or chunks
        pass
    except Exception as e:
        print(f"[Error] Unexpected exception in main loop: {e}")
