# ============================================================
# Chunk_Uploader Tasks
# ============================================================

# --- Req. 2.4.0-A ---
# TODO: Listen for incoming TCP connections on port 6001.

# --- Req. 2.4.0-B ---
# TODO: Accept TCP connection requests before they time out.

# --- Req. 2.4.0-C ---
# TODO: Upon receiving a message, parse the JSON to determine what is being requested.
#       Handle three cases:

#       (i)  If the JSON contains a "key" field:
#            - This is a key exchange request (secure download).
#            - Receive the remote peer's key (random number Y from downloader).
#            - Generate your own random number (use random.randint(2, p-2), must be < p, not 1 or p-1).
#            - Send your random number back over the same TCP connection in a JSON:
#              {"key": "XXX"}  (XXX replaced by your random number)
#            - Compute the shared secret key using the Diffie-Hellman key exchange mechanism.
#            - Store the shared key for use when encrypting the chunk to be sent.

#       (ii) If the JSON contains a "requested_secured_content" field:
#            - This is a request for an encrypted chunk.
#            - Read the requested chunk file from disk.
#            - Encrypt and encode the chunk data as described in Sec. 1.1.
#            - Send the encrypted chunk over the TCP connection in a JSON:
#              {"chunk_name": "forest_1", "encrypted_chunk": "YYY"}
#              (YYY replaced by the encrypted + encoded text)

#       (iii) If the JSON contains a "requested_content" field:
#             - This is a request for an unencrypted chunk.
#             - Read the requested chunk file from disk.
#             - Encode the chunk as a JSON-safe string as described in Sec. 1.1.
#             - Send the chunk over the TCP connection in a JSON:
#               {"chunk_name": "forest_1", "data": "YYY"}
#               (YYY replaced by the JSON-safe encoded string)

# --- Req. 2.4.0-D ---
# TODO: After sending a chunk, log the event to a text file in the same directory.
#       Each log entry shall include:
#         - Timestamp
#         - Chunk name
#         - Recipient's username/name
#         - Marked as "SENT"

# --- Req. 2.4.0-E ---
# TODO: After a TCP session is closed, do NOT terminate the service.
#       Continue listening on port 6001 for new incoming TCP connections (persistent loop).

