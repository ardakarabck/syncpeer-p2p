# ============================================================
# Chunk_Uploader Tasks
# ============================================================

# ─────────────────────────────────────────────────────────────────
# TASK 1 — Req 2.4.0-A: Listen for TCP Connections on Port 6001
# ─────────────────────────────────────────────────────────────────
# Step 1: Create a TCP socket.
# Step 2: Bind socket to port 6001 (listen on all interfaces).
# Step 3: Call listen() to put socket in server (listening) mode.
# Step 4: Enter a continuous accept() loop.

# ─────────────────────────────────────────────────────────────────
# TASK 2 — Req 2.4.0-B: Accept Incoming TCP Connection
# ─────────────────────────────────────────────────────────────────
# Step 1: Call accept() to accept the incoming connection before it times out.
# Step 2: Retrieve the remote IP from the accepted connection.
# Step 3: Look up remote IP in the shared IP-to-username dict (from Content Discovery)
#         to resolve requester's username for display and logging.

# ─────────────────────────────────────────────────────────────────
# TASK 3 — Req 2.4.0-C: Parse Incoming JSON & Route by Message Type
# ─────────────────────────────────────────────────────────────────
# Step 1: Receive the message bytes from the TCP connection.
# Step 2: Decode bytes and parse as JSON using json.loads().
# Step 3: Inspect parsed JSON keys to determine message type:

#   CASE (i) — Key "key" present → DH Key Exchange (Task 4)
#   CASE (ii) — Key "requested secured content" present → Encrypted Send (Task 5)
#   CASE (iii) — Key "requested content" present → Unencrypted Send (Task 6)

# CRITICAL: JSON key matching must be exact — "key", "requested secured content",
#           "requested content" — case-sensitive, no deviations.

# ─────────────────────────────────────────────────────────────────
# TASK 4 — Req 2.4.0-C (i): Handle Diffie-Hellman Key Exchange
# ─────────────────────────────────────────────────────────────────
# Step 1: Extract the remote's random number X from the JSON field "key".
# Step 2: Generate own random number Y using: random.randint(2, p-2)
#         where p = 907, g = 7. Y must not be 1 or p-1.
# Step 3: Send JSON reply over the same TCP connection: {"key": "<Y>"}
# Step 4: Compute the shared secret using Diffie-Hellman with the received X and own Y.
# Step 5: Convert the resulting shared integer to a byte array suitable for pyDes
#         (DES does not accept integers directly — must be bytes).
# Step 6: Store the derived DES key for use when encrypting the chunk in this session.
# NOTE: After key exchange, Chunk Uploader waits for the next message (chunk request)
#       on the same TCP connection.

# ─────────────────────────────────────────────────────────────────
# TASK 5 — Req 2.4.0-C (ii): Send Encrypted Chunk (Secure)
# ─────────────────────────────────────────────────────────────────
# Step 1: Extract chunk name from JSON field "requested secured content".
# Step 2: Print to console: requester's username and the requested chunk name.
# Step 3: Read the raw binary bytes of the requested chunk file from disk.
# Step 4: Encrypt using pyDes:
#         pyDas.des(des_key_bytes, pyDas.ECB, pad=None, padmode=pyDas.PAD_PKCS5)
#         .encrypt(raw_image_chunk_bytes)
# Step 5: Base64-encode the encrypted bytes:
#         base64.b64encode(encrypted_bytes).decode('utf-8') → encoded_chunk_string
# Step 6: Build JSON response:
#         {"chunk name": "<chunk_name>", "encrypted chunk": "<encoded_chunk_string>"}
# Step 7: Serialize to JSON string, encode to bytes, send over TCP connection.

# ─────────────────────────────────────────────────────────────────
# TASK 6 — Req 2.4.0-C (iii): Send Unencrypted Chunk (Unsecure)
# ─────────────────────────────────────────────────────────────────
# Step 1: Extract chunk name from JSON field "requested content".
# Step 2: Print to console: requester's username and the requested chunk name.
# Step 3: Read the raw binary bytes of the requested chunk file from disk.
# Step 4: Base64-encode the raw bytes (no encryption):
#         base64.b64encode(raw_image_chunk_bytes).decode('utf-8') → json_safe_string
# Step 5: Build JSON response:
#         {"chunk name": "<chunk_name>", "data": "<json_safe_string>"}
# Step 6: Serialize to JSON string, encode to bytes, send over TCP connection.

# ─────────────────────────────────────────────────────────────────
# TASK 7 — Req 2.4.0-D: Log Sent Chunk
# ─────────────────────────────────────────────────────────────────
# Step 1: After sending the chunk, append an entry to a log text file
#         in the same directory.
# Step 2: Each log entry must contain:
#         timestamp | chunk name | recipient's username | "SENT"

# ─────────────────────────────────────────────────────────────────
# TASK 8 — Req 2.4.0-E: Persist After TCP Session Closes
# ─────────────────────────────────────────────────────────────────
# Step 1: After TCP session ends (chunk sent, session closed), do NOT terminate.
# Step 2: Return to the accept() loop (Task 1) and continue listening on port 6001.

