# ============================================================
# Chunk_Announcer - Task List
# ============================================================

# --- Req. 2.1.0-A ---
# TODO: Ask the user to specify their username and store it locally.
# TODO: Ask the user to specify the file it will initially host.
# TODO: Divide the specified file into N-byte chunks and store them
#       as separate files with indexed naming (code will be provided).
#       Note: chunks will NOT have a .png suffix.
#       Assume each file always has 3 chunks.
# TODO: Display a message on terminal informing the user about:
#       - The number of chunks
#       - That it is starting to announce these files

# --- Req. 2.1.0-B ---
# TODO: After preparing chunks, periodically send broadcast UDP messages
#       to announce the node's presence.
#       - Period: every 8 seconds
#       - Broadcast IP address: 192.168.1.255

# --- Req. 2.1.0-C ---
# TODO: Read the names of the files under a specified directory.
# TODO: Insert those file names into the broadcast message as a JSON array.

# --- Req. 2.1.0-D ---
# TODO: Ensure each periodic broadcast message contains a valid JSON with:
#       - Key "username"  (all lowercase, no underscore) -> the user-specified username
#       - Key "chunks"    (all lowercase)                -> JSON array of hosted file names
#       Example:
#       {
#           "username": "Ece",
#           "chunks": ["forest_1", "forest_2", "forest_3",
#                      "flower_2", "bee_1", "city_1", "city_2"]
#       }
