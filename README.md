# CMP2204 P2P File Sharing Application

![Status](https://img.shields.io/badge/status-demo--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Protocol](https://img.shields.io/badge/protocol-UDP%206000%20%2F%20TCP%206001-orange)

A peer-to-peer file sharing application built for **CMP2204 — Introduction to Computer Networks (Spring 2026)**. Peers discover each other on the Local Area Network using UDP announcements, then exchange file chunks directly over TCP. The application supports both unencrypted and encrypted chunk transfer. Secure transfer uses Diffie-Hellman key exchange with DES encryption through the `pyDes` library.

---

## Table of Contents

* [About the Project](#about-the-project)
* [Tech Stack](#tech-stack)
* [Team](#team)
* [Requirements](#requirements)
* [Folder Setup](#folder-setup)
* [How to Run](#how-to-run)
* [Wireshark Verification](#wireshark-verification)
* [Logs](#logs)
* [Project Structure](#project-structure)
* [Known Limitations](#known-limitations)

---

## About the Project

The system has four cooperating processes:

| Process                | Role                                                                                        | Port     |
| ---------------------- | ------------------------------------------------------------------------------------------- | -------- |
| `Chunk_Announcer.py`   | Splits the original file into 3 chunks and broadcasts the hosted chunk list every 8 seconds | UDP 6000 |
| `Content_Discovery.py` | Listens for UDP announcements and maintains the shared peer/content dictionaries            | UDP 6000 |
| `Chunk_Uploader.py`    | Acts as the TCP server and serves requested chunks in secure or unsecure mode               | TCP 6001 |
| `Chunk_Downloader.py`  | Provides the terminal menu for viewing content, downloading chunks, and viewing history     | TCP 6001 |

The program follows the required peer-to-peer structure:

1. A peer announces the chunks it owns.
2. Other peers discover the available chunks.
3. The downloader requests the needed chunks one by one.
4. The uploader sends the requested chunks over TCP.
5. The downloader saves the chunks and merges them into the final file.
6. Upload and download events are logged.

Secure transfers use **Diffie-Hellman** with:

```text
p = 907
g = 7
```

The generated shared secret is converted into an 8-byte DES key. The chunk is then encrypted using `pyDes`, encoded with Base64, and inserted into a JSON payload. Unsecure transfers skip encryption but still use Base64 so that raw image bytes can be safely transferred inside JSON.

---

## Tech Stack

* **Language:** Python 3.10+
* **Standard Library:** `socket`, `threading`, `json`, `base64`, `random`, `os`, `time`, `math`, `datetime`
* **External Library:** `pyDes`
* **Discovery Protocol:** UDP broadcast on port `6000`
* **Chunk Transfer Protocol:** TCP on port `6001`
* **Interface:** Command Line Interface / Terminal
* **Testing Tool:** Wireshark

---

## Team

| Name           | Role                               | GitHub                                         |
| -------------- | ---------------------------------- | ---------------------------------------------- |
| Meryem Mahmut  | Content Discovery + Chunk Uploader | [@MXRI3](https://github.com/MXRI3)             |
| Ömer Bayık     | Chunk Announcer                    | [@username](https://github.com/username)       |
| Arda Karaböcek | Chunk Downloader                   | [@ardakarabck](https://github.com/ardakarabck) |

A separate 1-page document is included with the submission. It describes the development platform, challenges faced, group members, and division of workload.

---

## Requirements

Install Python 3.10 or newer.

Install `pyDes` before running the secure mode:

```bash
python -m pip install pyDes
```

Wireshark is only needed for verification screenshots. It is not required for running the actual Python program.

---

## Folder Setup

Create a folder for the original image and chunks. The folder name can be anything, such as:

```text
pic
```

or:

```text
test_images
```

Example folder before running the announcer:

```text
pic/
└── view.png
```

When `Chunk_Announcer.py` runs, it splits the selected image into exactly 3 chunks:

```text
pic/
├── view.png
├── view_1.png
├── view_2.png
└── view_3.png
```

The same folder should be used when running the uploader so it can find and serve the chunk files.

---

## How to Run

Open four terminal windows in the project folder and run the processes in this order.

---

### 1. Start Content Discovery

```bash
python Content_Discovery.py
```

This process listens for UDP announcements on port `6000`.

It creates and updates these shared files:

```text
ip_to_user.txt
user_to_ip.txt
content_dict.txt
```

It also refreshes the content dictionary periodically so that old announcements do not stay forever.

---

### 2. Start Chunk Announcer

```bash
python Chunk_Announcer.py
```

The announcer asks for:

```text
Enter your username:
Enter the original file to host:
Enter the folder where chunks will be stored:
```

Example input:

```text
Username: mimi
Original file: pic\view.png
Chunk folder: pic
```

After splitting the file, it broadcasts a JSON message every 8 seconds:

```json
{
  "username": "mimi",
  "chunks": ["view_1.png", "view_2.png", "view_3.png"]
}
```

---

### 3. Start Chunk Uploader

```bash
python Chunk_Uploader.py
```

The uploader asks for the folder where the chunk files are stored.

Example:

```text
pic
```

It then listens on TCP port `6001`.

The uploader supports:

* unsecure chunk requests
* secure chunk requests
* Diffie-Hellman key exchange
* DES encryption
* Base64 encoding
* upload logging

---

### 4. Start Chunk Downloader

```bash
python Chunk_Downloader.py
```

The downloader shows this menu:

```text
1. View Contents
2. Download Content
3. History
```

#### Option 1 — View Contents

Displays available content files discovered from the network.

Example:

```text
view.png
```

#### Option 2 — Download Content

Prompts for the content name:

```text
view.png
```

Then asks whether to download securely or unsecurely:

```text
0 = unsecure download
1 = secure download
```

The downloader requests the three chunks sequentially:

```text
view_1.png
view_2.png
view_3.png
```

After all chunks are downloaded, it merges them into the final file.

#### Option 3 — History

Displays download/received history from the log files.

---

## Wireshark Verification

For same-device testing, select:

```text
Adapter for loopback traffic capture
```

Then apply this Wireshark filter:

```text
tcp.port == 6001
```

For two-device LAN testing, select the active Wi-Fi/Ethernet adapter instead.

---

### Unencrypted Exchange

In unencrypted mode, the TCP stream shows readable JSON and Base64 image data.

Example:

```json
{"requested content": "view_1.png"}
{"chunk name": "view_1.png", "data": "iVBORw0KGgo..."}
```

The Base64 string starting with:

```text
iVBORw0KGgo
```

corresponds to the PNG header, which confirms that the unencrypted image chunk data is visible in the packet capture.

---

### Encrypted Exchange

In secure mode, the downloader and uploader first exchange Diffie-Hellman values:

```json
{"key": "..."}
{"key": "..."}
```

Then the downloader requests the secured chunk:

```json
{"requested secured content": "view_1.png"}
```

The uploader responds with encrypted Base64 ciphertext:

```json
{"chunk name": "view_1.png", "encrypted chunk": "Base64CiphertextHere..."}
```

Unlike the unencrypted exchange, the encrypted payload does not reveal the PNG header directly because the chunk bytes are encrypted before Base64 encoding.

---

## Logs

The program creates log files during runtime.

### Upload Log

`upload_log.txt` stores sent chunks:

```text
timestamp | chunk name | recipient | SENT
```

Example:

```text
2026-06-07 05:33:21 | view_1.png | mimi | SENT
```

### Received Log

`received_log.txt` stores received chunks:

```text
timestamp | chunk name | sender | RECEIVED
```

Example:

```text
2026-06-07 05:33:21 | view_1.png | mimi | RECEIVED
```

### Download Log

`download_log.txt` stores downloaded chunks with sender IP information:

```text
timestamp | chunk name | sender IP
```

Example:

```text
2026-06-07 05:33:21 | view_1.png | 127.0.0.1
```

These files are generated automatically when the program is run.

---

## Project Structure

```text
[SyncPeer]_P2P/
├── Chunk_Announcer.py
├── Content_Discovery.py
├── Chunk_Uploader.py
├── Chunk_Downloader.py
├── README.md
├── Platform_Challenges_Workload.docx
├── Wireshark_Encrypted_Image_Chunk.png
├── Wireshark_Unencrypted_Image_Chunk.png
├── ip_to_user.txt        (generated at runtime)
├── user_to_ip.txt        (generated at runtime)
├── content_dict.txt      (generated at runtime)
├── upload_log.txt        (generated at runtime)
├── received_log.txt      (generated at runtime)
├── download_log.txt      (generated at runtime)
└── pic/
    ├── view.png
    ├── view_1.png
    ├── view_2.png
    └── view_3.png
```

---

## Known Limitations

* **LAN-scoped:** The application is designed for peers on the same Local Area Network. It does not support discovery across different networks or subnets.
* **Loopback testing:** For same-device testing, Wireshark shows traffic as `127.0.0.1 → 127.0.0.1`. For real two-device LAN testing, peers should use their LAN IP addresses and the correct LAN broadcast address.
* **Broadcast IP:** For local testing, `127.0.0.1` can be used. For a real LAN demo, the broadcast address may need to be changed to the local network broadcast address, such as `192.168.1.255`.
* **Exactly 3 chunks:** The application assumes each file is split into exactly 3 chunks, as required by the simplified project design.
* **Terminal-only interface:** The application runs through command-line prompts and does not include a graphical user interface.
* **DES encryption:** DES is used because it is required for the project. Modern real-world systems would normally use stronger encryption such as AES.
* **Folder paths matter:** The uploader can only serve chunks that exist in the folder entered by the user. If the wrong folder is entered, the requested chunk may not be found.
* **Generated files:** Dictionary and log files are created during runtime, so they may be empty or missing before the program is tested.

---

## Included Files

The submission includes:

```text
[SyncPeer] Chunk_Announcer.py
[SyncPeer] Content_Discovery.py
[SyncPeer] Chunk_Uploader.py
[SyncPeer] Chunk_Downloader.py
[SyncPeer] README.md
[SyncPeer] Report.docx
[SyncPeer] Wireshark encrypted.png
[SyncPeer] Wireshark unencrypted.png
```

The Wireshark screenshots show one encrypted and one unencrypted image chunk exchange, including IP addresses and packet contents.
