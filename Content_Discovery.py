# ============================================================
# Content Discovery - Task List (Section 2.2)
# ============================================================

# TODO 2.2.0-A: Listen for UDP broadcast messages on port 6000.

# TODO 2.2.0-B: Upon receiving a broadcast message:
#   (i)  Parse the message contents using a JSON parser in Python.
#   (ii) Get the UDP broadcast sender's IP address using the recvfrom() method.

# TODO 2.2.0-C: Maintain a dictionary to map IP addresses -> usernames.
#   - Keys   : IP address (retrieved from recvfrom())
#   - Values : username (parsed from the JSON message)
#   - Share this dictionary with Chunk_Uploader and Chunk_Downloader processes
#     (e.g., store it in a local text/file shared between processes).
#   - Use this dictionary to display usernames instead of raw IP addresses
#     whenever printing "from whom" content is being requested.

# TODO 2.2.0-D: Maintain a separate "content dictionary" mapping chunk names -> user list.
#   - Keys   : content chunk name (e.g., "forest_1")
#   - Values : list of usernames that have that chunk
#   - Share this dictionary with the Chunk_Downloader process
#     (e.g., store it in a local text/file shared between processes).

# TODO 2.2.0-E: Maintain a third dictionary mapping usernames -> IP addresses.
#   - This will be used by Chunk_Downloader to initiate TCP sessions:
#     look up which users have a chunk, then look up their IP address.

# TODO 2.2.0-F: Upon every insertion into the content dictionary, display on the console
#   the detected username and their hosted content.
#   Example output: "Ece : vid_1, vid_2, vid_3"

# TODO 2.2.0-G: Wipe the content dictionary every ~60 seconds so that only
#   recently discovered content is shown to the end user.
