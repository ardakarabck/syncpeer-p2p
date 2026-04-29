# P2P File Sharing Application

![Project Status](https://img.shields.io/badge/status-in%20development-yellow)

## Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Team](#team)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)

---

## About the Project

A peer-to-peer (P2P) file sharing application that allows users to share files directly between devices without a central server. Built as a collaborative project by a team of 3 developers.

---

## Features

- Direct peer-to-peer file transfer
- File browsing and selection
- Transfer progress tracking
- Multiple peer connections

---

## Tech Stack 

- **Language:** Python
- **Framework:** Standard Library only (uses socket, threading, json, base64)
- **Protocol:** TCP Sockets (port 6001 for transfers) / UDP Broadcast (port 6000 for announcements)
- **UI:** CLI(Command Line Interface)
---

## Team 

(Fetchleyip kendi github profilinizi eklersiniz)

| Name | Role | GitHub |
|------|------|--------|
| [Ömer Bayık] | [e.g. Backend / P2P Logic] | [@username](https://github.com/username) |
| [Meryem Mahmut] | [e.g. Frontend / UI] | [@MXRI3](https://github.com/MXRI3) |
| [Arda Karaböcek] | [e.g. Networking / Testing] | [@ardakarabck](https://github.com/ardakarabck) |

---

## Getting Started

### Prerequisites 

- Python 3.10+
- Git
- pyDes library (pip install pyDes)

### Installation 

1. Clone the repository

   git clone https://github.com/ardakarabck/syncpeer-p2p.git

2. Navigate to the project directory

   cd syncpeer-p2p/ 

3. Install dependencies

   pip install pyDes

---

## Project Structure  
(Burayı da düzenleyeceğiz - Ece hoca farklı dosyalar verdi)

syncpeer-p2p
├── Chunk_Announcer.py
├── Chunk_Downloader.py
├── Chunk_Uploader.py
├── Content_Discovery.py
├── LICENSE
└── README.md

---

                                                                                                                                                                                               100,1         Bot
