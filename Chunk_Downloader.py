
# ============================================================
# Chunk_Downloader Tasks (Requirements 2.3.0-A through 2.3.0-E)
# ============================================================

# --- Req 2.3.0-A: Launch Menu ---
# TODO: On launch, prompt the user to choose one of three options:
#       1. "View Contents"
#       2. "Download Content"
#       3. "History"
# TODO: Handle user input and route to the correct functionality based on choice.

# --- Req 2.3.0-B: View Contents ---
# TODO: When user selects "View Contents", display the list of content FILES
#       available in the network (e.g., "forest.png", "flower.png") — NOT chunks.
# TODO: Derive content names from chunk names by stripping the chunk index suffix
#       (e.g., "forest_1" → "forest.png").
# TODO: A content name shall be listed if AT LEAST ONE of its chunks is found
#       in the network (do not require all chunks to be present).
# TODO: Ensure content names are displayed without duplicates (use a set or
#       equivalent deduplication logic).

# --- Req 2.3.0-C: Download Content ---
# TODO: When user selects "Download Content", prompt the user to specify
#       which content they want to download (e.g., "forest.png" or "forest").
# TODO: Internally map the user input to the correct chunk names:
#       e.g., "forest" → "forest_1", "forest_2", "forest_3".
# TODO: Ask the user whether they prefer to download the content SECURELY or NOT.
# TODO: Remember the user's security preference for this download session.
# TODO: Initiate 3 sequential download procedures — one for each chunk of the file.

# --- Req 2.3.0-D: Chunk Lookup via Content Dictionary ---
# TODO: For each of the 3 chunks to download (e.g., "forest_1", "forest_2", "forest_3"):
#       - Look up the content dictionary (shared with Content_Discovery) using
#         the chunk name as the key.
#       - Retrieve the list of IP addresses (users) that have that chunk.
# TODO: Attempt to download the chunk from the FIRST IP address in the list
#       for that chunk key in the content dictionary.

# --- Req 2.3.0-E: TCP Download Session per Chunk ---
# TODO: For each chunk download, initiate a TCP session with the resolved IP address.
# TODO: Send a JSON message over TCP that includes:
#       - The chunk being requested.
#       - Whether the download is secure or unsecure (based on user's preference).
# TODO: Ensure the JSON format matches the agreed-upon format with peers
#       (confirm key names and structure with the project spec / peer agreement).
# TODO: Display a UI message on the console indicating:
#       - Which chunk is being requested.
#       - From which user (IP or username).
#       - The timestamp of the request.
#       (This aids debugging and improves UI feedback.)

# --- Req 2.3.0-F: Secure Download ---
# TODO: If the user chose "secure", initiate Diffie-Hellman key exchange:
#       1. Randomly generate a number (key) where 2 <= key < p-2
#          Use: random.randint(2, p-2)  — key must NOT be 1 or p-1.
#       2. Send the remote device a JSON message: {"key": key}
# TODO: Wait to receive the remote host's random number Y in a JSON response.
# TODO: Compute the shared_secret_key using the Diffie-Hellman mechanism
#       (g^(our_key * their_key) mod p).
# TODO: Store the shared secret key to use later for DECRYPTING the received chunk.
# TODO: After key exchange, send the chunk request as JSON:
#       {"requested_secured_content": "forest_1"}
#       (Ensure key name is EXACTLY "requested_secured_content".)

# --- Req 2.3.0-G: Unsecure Download ---
# TODO: If the user chose "unsecure", skip key generation entirely.
# TODO: Directly send the chunk request as JSON:
#       {"requested_content": "forest_1"}
#       (Ensure key name is EXACTLY "requested_content".)

# --- Req 2.3.0-H: Download Retry Logic ---
# TODO: If a chunk download from the first IP is successful, move on to the next chunk.
# TODO: If a chunk download fails:
#       - Display a console message: "Chunk [chunk_name] cannot be downloaded from [user name]."
#       - Try the next IP address in the content dictionary array for that chunk.
# TODO: If ALL IP addresses in the array have been tried and all failed:
#       - Display a warning: "CHUNK [chunk_name] CANNOT BE DOWNLOADED FROM ONLINE PEERS."

# --- Req 2.3.0-I: Merge Chunks into Final File ---
# TODO: After the 3rd chunk is successfully downloaded, combine the 3 chunks
#       into a single file using the provided merging code.
# TODO: Once the file is ready, inform the user via the terminal:
#       e.g., "File has been successfully downloaded."
# TODO: Do NOT delete or remove the individual chunk files after merging —
#       they must remain available (needed for the demo day).

# --- Req 2.3.0-J: Close TCP Session ---
# TODO: After receiving each requested chunk, close the TCP session.

# --- Req 2.3.0-K: Log Each Received Chunk ---
# TODO: Upon receiving each chunk, log the event with:
#       - Timestamp
#       - Chunk name
#       - Received from (IP/username)
#       - Mark entry as "RECEIVED"

# --- Req 2.3.0-L: Download Log File ---
# TODO: Dump all downloaded chunk filenames to a Download log (text file)
#       in the same directory.
# TODO: Each log entry shall include:
#       - Timestamp
#       - Chunk name
#       - Downloaded_from IP address

# --- Req 2.3.0-M: Persist After TCP Close ---
# TODO: After a TCP session is closed, Chunk_Downloader shall keep running.
# TODO: The service shall NOT terminate — loop back to the main menu or
#       continue listening for further user interaction.

