# ============================================================
# Chunk_Announcer Tasks
# ============================================================

from socket import*
serverPort = 12000
serverSocket = socket(AF_INET,
    SOCK_DGRAM ) 
serverSocket.bind(('',serverPort))
print "The server is ready to receive"
while 1 :
    message,clientAddress =  serverSocket.recvfrom(2048)
    modifiedMessage = message.upper()
    serverSocket.sendto(modifiedMessage,clientAddress)

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

# ─────────────────────────────────────────────
# TASK 2 — Req 2.1.0-B: Periodic UDP Broadcast
# ─────────────────────────────────────────────
# Step 1: Create a UDP socket.
# Step 2: Enable SO_BROADCAST socket option.
# Step 3: Target broadcast IP: 192.168.1.255.
# Step 4: Period: send once every 8 seconds.
# Step 5: Run a loop — build message, send, sleep 8 seconds, repeat.

# ─────────────────────────────────────────────
# TASK 3 — Req 2.1.0-C: Read Hosted Chunk Names from Directory
# ─────────────────────────────────────────────
# Step 1: Point to the directory where chunk files are stored.
# Step 2: Read all filenames in that directory.
# Step 3: Collect chunk names into a Python list.
# Step 4: This list feeds directly into the broadcast JSON payload (Task 4).

# ─────────────────────────────────────────────
# TASK 4 — Req 2.1.0-D: Construct & Send Broadcast JSON
# ─────────────────────────────────────────────
# Step 1: Build a dict with exactly two keys:
#           key "username" (all lowercase, no underscore) → username string
#           key "chunks"  (all lowercase)                 → list of chunk name strings
#         Example: {"username": "Ece", "chunks": ["forest 1", "forest 2", "forest 3"]}
# Step 2: Serialize dict to JSON string via json.dumps().
# Step 3: Encode JSON string to bytes (UTF-8).
# Step 4: Send encoded bytes via UDP broadcast socket to 192.168.1.255 on port 6000.
# Step 5: Repeat every 8 seconds (integrated into Task 2 loop).
# CRITICAL: Key names must be exactly "username" and "chunks".
#           JSON must be valid — malformed JSON causes peer parsing failures.

