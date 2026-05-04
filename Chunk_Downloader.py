# ============================================================
# Chunk_Downloader Tasks
# ============================================================

# ─────────────────────────────────────────────────────────────────
# TASK 1 — Req 2.3.0-A: Startup Menu
# ─────────────────────────────────────────────────────────────────
# Step 1: On launch, prompt user to choose one of three options:
#         "View Contents" | "Download Content" | "History"
# Step 2: Route to the correct task based on user choice.
# Step 3: After completing an action, return to the menu (do not terminate)

# ─────────────────────────────────────────────────────────────────
# TASK 2 — Req 2.3.0-B: View Contents
# ─────────────────────────────────────────────────────────────────
# Step 1: Read the shared content dictionary (from Content Discovery).
# Step 2: Extract unique content/file names from chunk names:
#         "forest 1", "forest 2", "forest 3" → display only "forest.png"
#         Strip the trailing index number and add back the .png extension.
# Step 3: Deduplicate the resulting content names.
# Step 4: A content name is included if at least ONE of its chunks appears
#         in any node in the network — all 3 chunks being present is NOT required.
# Step 5: Print the deduplicated content name list to console.
    
# ─────────────────────────────────────────────────────────────────
# TASK 3 — Req 2.3.0-C: Initiate Download
# ─────────────────────────────────────────────────────────────────
# Step 1: Prompt user to enter the content name to download (e.g., "forest.png").
# Step 2: Ask user: "secure" or "unsecure" download — store this choice.
# Step 3: Derive the 3 chunk names from the entered filename:
#         e.g., "forest.png" → "forest 1", "forest 2", "forest 3"
# Step 4: Sequentially initiate download procedure for each of the 3 chunks
#         (Tasks 4–8 below), in order: chunk 1, then 2, then 3.

# ─────────────────────────────────────────────────────────────────
# TASK 4 — Req 2.3.0-D: Look Up Chunk Owners
# ─────────────────────────────────────────────────────────────────
# Step 1: For each chunk name (e.g., "forest 1"), look up the shared content
#         dictionary with the chunk name as key.
# Step 2: Retrieve the list of usernames who have that chunk.
# Step 3: Use the username-to-IP dict to resolve the first username to an IP address.
# Step 4: That IP is the first download attempt target.
    
# ─────────────────────────────────────────────────────────────────
# TASK 5 — Req 2.3.0-E: Open TCP Session & Display UI Message
# ─────────────────────────────────────────────────────────────────
# Step 1: Open a TCP socket and connect to the target IP on port 6001.
# Step 2: Before sending, print to console:
#         which chunk is being requested, from which user, at what timestamp.
# Step 3: Send the appropriate JSON request (see Task 6 or Task 7).

# ─────────────────────────────────────────────────────────────────
# TASK 6 — Req 2.3.0-F: Secure Download — Diffie-Hellman Key Exchange
# ─────────────────────────────────────────────────────────────────
# Step 1: Use fixed DH parameters: p = 907, g = 7.
# Step 2: Generate own random number X using: random.randint(2, p-2).
#         X must not be 1 or p-1 (trivial secrets).
# Step 3: Send JSON: {"key": "<X>"} to the remote Chunk Uploader over the TCP session.
# Step 4: Receive the remote's JSON reply containing their random number Y.
# Step 5: Parse Y from the JSON.
# Step 6: Compute shared secret using Diffie-Hellman:
#         shared_int = (g^X mod p combined with Y) — standard DH formula.
# Step 7: Convert shared_int to bytes suitable for pyDes (DES requires a byte-array key).
# Step 8: Store the derived key for decrypting the chunk received in this TCP session.
# Step 9: Send chunk request JSON: {"requested secured content": "<chunk_name>"}
# CRITICAL: JSON key must be exactly "requested secured content".

# ─────────────────────────────────────────────────────────────────
# TASK 7 — Req 2.3.0-G: Unsecure Download
# ─────────────────────────────────────────────────────────────────
# Step 1: Skip key exchange entirely.
# Step 2: Send JSON directly: {"requested content": "<chunk_name>"}
# CRITICAL: JSON key must be exactly "requested content".

# ─────────────────────────────────────────────────────────────────
# TASK 8 — Req 2.3.0-H: Handle Download Success / Failure & Fallback
# ─────────────────────────────────────────────────────────────────
# Step 1: If chunk received successfully → proceed to next chunk (Task 4 for next index).
# Step 2: If download fails from current peer → print:
#         "Chunk [chunk name] cannot be downloaded from [username]"
# Step 3: Try the next IP in the content dictionary array for that chunk.
# Step 4: If ALL peers for that chunk have been tried and failed → print warning:
#         "CHUNK <chunk_name> CANNOT BE DOWNLOADED FROM ONLINE PEERS."

# ─────────────────────────────────────────────────────────────────
# TASK 9 — Req 2.3.0-I: Merge Chunks After All 3 Downloaded
# ─────────────────────────────────────────────────────────────────
# Step 1: After chunk 3 is successfully downloaded, call the provided merge function
#         to combine the 3 chunk files into a single file.
# Step 2: Print terminal message informing user the file has been successfully downloaded.
# Step 3: Do NOT delete the individual chunk files after merging.

# ─────────────────────────────────────────────────────────────────
# TASK 10 — Req 2.3.0-J: Close TCP Session Per Chunk
# ─────────────────────────────────────────────────────────────────
# Step 1: After receiving the chunk (success or failure), close the TCP socket.
# Step 2: A new TCP session must be opened for the next chunk (sessions are not reused).

# ─────────────────────────────────────────────────────────────────
# TASK 11 — Req 2.3.0-K & 2.3.0-L: Logging
# ─────────────────────────────────────────────────────────────────
# Step 1 (Req K): On each chunk received, log to a text file in the same directory:
#         timestamp | chunk name | received from (username) | "RECEIVED"
# Step 2 (Req L): Also maintain a download log text file in the same directory.
#         Each entry: timestamp | chunk name | downloaded from IP address.

# ─────────────────────────────────────────────────────────────────
# TASK 12 — Req 2.3.0-M: Persist After TCP Session Closes
# ─────────────────────────────────────────────────────────────────
# Step 1: After each TCP session closes, do NOT terminate the process.
# Step 2: Return to the main menu (Task 1) to await the next user action.

# ─────────────────────────────────────────────────────────────────
# TASK 13 — Secure Chunk Decryption (Sec. 1.1, referenced by 2.3.0-F)
# ─────────────────────────────────────────────────────────────────
# Step 1: Receive JSON from Chunk Uploader containing key "encrypted chunk".
# Step 2: Extract the Base64 string value.
# Step 3: Base64-decode it back to encrypted bytes.
# Step 4: Decrypt using pyDes: pyDes.des(des_key_bytes, pyDes.ECB, pad=None,
#         padmode=pyDas.PAD_PKCS5).decrypt(encrypted_bytes)
# Step 5: Result is the raw image chunk bytes — write to a chunk file.
# NOTE: des_key_bytes must be a byte array derived from the DH shared integer, not int.

import json
from socket import *
import datetime
import base64
import pyDes
import random
## Global variables ##

Global_Chunk_Num = 3 # flower_(1,2,3).png
TCP_PORT = 6001

# Diffie-Hellman Key Exchange Parameters #
DH_p = 907
DH_g = 7

# Return a dictionary from JSON syntax'd file with error handling
def JSON_to_dict(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading file: {e}")
        return {}

# ─────────────────────────────────────────────────────────────────
# TASK 11 — Logging helpers
# ─────────────────────────────────────────────────────────────────
def logChunk(chunk_name, username, ip):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Req K: timestamp | chunk name | username | RECEIVED
    with open("received_log.txt", "a") as f:
        f.write(f"{timestamp} | {chunk_name} | {username} | RECEIVED\n")
    # Req L: timestamp | chunk name | IP address
    with open("download_log.txt", "a") as f:
        f.write(f"{timestamp} | {chunk_name} | {ip}\n")

# ─────────────────────────────────────────────────────────────────
# TASK 11 — Req 2.3.0-K & L: fetchHistory
# ─────────────────────────────────────────────────────────────────
def fetchHistory():
    print("\n--- Received Log ---")
    try:
        with open("received_log.txt", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("No received log found.")

    print("\n--- Download Log ---")
    try:
        with open("download_log.txt", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("No download log found.")
# ─────────────────────────────────────────────────────────────────
# TASK 2 — Req 2.3.0-B: View Contents
# ─────────────────────────────────────────────────────────────────
def viewContent():
    Chunk_Dict = JSON_to_dict("content_dict.txt")   # re-read fresh from disk
    uniqueContent = []                               # fix: was {}, must be a list
    for chunk_key in Chunk_Dict:
        specificChunk = chunk_key.split('_')[0]      # forest_1.png -> forest
        if specificChunk not in uniqueContent:
            uniqueContent.append(specificChunk)
    print("Here is the list of available content:\n")
    for j in range(len(uniqueContent)):
        print(f"  {j+1}) {uniqueContent[j]}.png")
    print()

# ─────────────────────────────────────────────────────────────────
# TASK 6 — Req 2.3.0-F: Diffie-Hellman Key Exchange
# ─────────────────────────────────────────────────────────────────
def create_DH_key(s):
    # Step 2: generate own private random X
    X = random.randint(2, DH_p - 2)

    # Step 3: send our public value to uploader
    public_val = pow(DH_g, X, DH_p)             # g^X mod p
    s.send(json.dumps({"key": str(public_val)}).encode())

    # Step 4 & 5: receive uploader's public value Y
    response = s.recv(1024).decode()
    Y = int(json.loads(response)["key"])         # their g^Y mod p

    # Step 6: compute shared secret = Y^X mod p  (standard DH)
    shared_secret_int = pow(Y, X, DH_p)

    # Step 7: convert shared_int to 8-byte key for DES
    des_key_string = str(shared_secret_int).zfill(8)[:8]   # e.g. 456 → "00000456" → "00000456"
    des_key_bytes = des_key_string.encode('utf-8')          # → b"00000456" (exactly 8 bytes)

    # Step 8: return derived key
    return shared_bytes

# ─────────────────────────────────────────────────────────────────
# TASK 3, 4, 5, 6, 7, 8, 9, 10, 13 — downloadContent
# ─────────────────────────────────────────────────────────────────
def downloadContent():
    # TASK 3 — get filename and build chunk list
    chunk_name = input("Choose a content to download (e.g., forest.png): \n")
    chunk_pure = chunk_name.split('.')[0]                    # forest.png -> forest
    chunks_in_need = []
    for i in range(1, Global_Chunk_Num + 1):
        chunks_in_need.append(f"{chunk_pure}_{i}.png")      # ["forest_1.png", "forest_2.png", "forest_3.png"]

    sec_val = input("Which type of download: unsecure(0) or secure(1) (type only 0/1): ")

    # Re-read dictionaries fresh from disk (TASK 4)
    Chunk_Dict = JSON_to_dict("content_dict.txt")
    user_to_ip = JSON_to_dict("user_to_ip.txt")

    all_success = True  # track if all 3 chunks downloaded (for TASK 9)

    for chunk in chunks_in_need:
        # TASK 4 — look up owners of this chunk
        owners = Chunk_Dict.get(chunk, [])          # e.g. ["alex", "bob"]

        if not owners:
            print(f"CHUNK {chunk} CANNOT BE DOWNLOADED FROM ONLINE PEERS.")
            all_success = False
            continue

        # TASK 8 — try each owner, fallback to next on failure
        downloaded = False
        for username in owners:
            ip = user_to_ip.get(username)
            if not ip:
                continue

            try:
                # TASK 5 — open TCP session
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, TCP_PORT))

                # TASK 5 — UI message before sending
                print(f"[{datetime.datetime.now()}] Requesting '{chunk}' from '{username}' ({ip})")

                if sec_val == '1':
                    # TASK 6 — DH key exchange
                    des_key = create_DH_key(s)
                    # TASK 6 Step 9 — send secure request
                    request = json.dumps({"requested secured content": chunk})
                    s.send(request.encode())

                    # TASK 13 — receive and decrypt
                    data = s.recv(65536)
                    if not data:
                        raise Exception("Empty response")
                    payload = json.loads(data.decode('utf-8'))
                    encrypted_bytes = base64.b64decode(payload["encrypted chunk"])
                    # Decrypt using pyDes with the exact 8-byte key
                    chunk_bytes = pyDes.des(
                        des_key_bytes,
                        pyDes.ECB,
                        pad=None,
                        padmode=pyDes.PAD_PKCS5
                    ).decrypt(encrypted_bytes)

                else:
                    # TASK 7 — unsecure request
                    request = json.dumps({"requested content": chunk})
                    s.send(request.encode())

                    # receive raw bytes
                    data = s.recv(65536)
                    if not data:
                        raise Exception("Empty response")
                    chunk_bytes = data

                # Save chunk to file
                with open(chunk, "wb") as f:
                    f.write(chunk_bytes)

                print(f"  ✓ '{chunk}' downloaded successfully from '{username}'")

                # TASK 11 — log success
                logChunk(chunk, username, ip)

                s.close()               # TASK 10 — close socket after each chunk
                downloaded = True
                break                   # TASK 8 — success, stop trying other peers

            except Exception as e:
                # TASK 8 — this peer failed, try next
                print(f"Chunk {chunk} cannot be downloaded from {username}")
                try:
                    s.close()           # TASK 10 — always close even on failure
                except:
                    pass

        if not downloaded:
            # TASK 8 — all peers exhausted for this chunk
            print(f"CHUNK {chunk} CANNOT BE DOWNLOADED FROM ONLINE PEERS.")
            all_success = False

    # TASK 9 — merge if all 3 chunks downloaded successfully
    if all_success:
        merge(chunks_in_need, chunk_name)
        print(f"✓ '{chunk_name}' has been downloaded and merged successfully!")

# ─────────────────────────────────────────────────────────────────
# TASK 9 — Merge helper (provided externally, placeholder here)
# ─────────────────────────────────────────────────────────────────
def merge(chunk_files, output_name):
    with open(output_name, "wb") as out:
        for chunk_file in chunk_files:
            with open(chunk_file, "rb") as f:
                out.write(f.read())

# ─────────────────────────────────────────────────────────────────
# TASK 1 — Req 2.3.0-A: Startup Menu
# ─────────────────────────────────────────────────────────────────
def selectChoice(self): # TASK 1 (we can create a main function as well)
    print("Choose an option:\n 1.View Contents\n 2.Download Content \n 3.History\n Enter 'quit' to stop: ")
    while True:
        option = input("> ")
        if option == 'quit':
            print("Goodbye!")
            break

        if option not in ('1', '2', '3'):
            print("Invalid input (1, 2 or 3)\n")
            continue   # go back to menu immediately

        if option == '1':
            print("Viewing contents...\n")
            viewContent()
        elif option == '2':
            print("Downloading contents...\n")
            downloadContent()
        elif option == '3':
            print("Fetching your history...\n")
            fetchHistory()
        # TASK 12 — return to menu after each action
        print("\nChoose an option:\n 1. View Contents\n 2. Download Content\n 3. History\n Enter 'quit' to stop: ")   

# ─────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    selectChoice()
