# ============================================================
# Chunk_Downloader Tasks
# ============================================================

# ─────────────────────────────────────────────────────────────────
# TASK 1 — Req 2.3.0-A: Startup Menu
# ─────────────────────────────────────────────────────────────────
# Step 1: On launch, prompt user to choose one of three options:
#         "View Contents" | "Download Content" | "History"
# Step 2: Route to the correct task based on user choice.
# Step 3: After completing an action, return to the menu (do not terminate).

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

