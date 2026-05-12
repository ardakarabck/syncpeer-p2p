"""
PeerShare — P2P File Sharing Dashboard UI
==========================================
Covers all four modules:
  • ChunkAnnouncer  — startup, chunk creation, broadcast status
  • ContentDiscovery — live peer/chunk network map
  • ChunkDownloader  — view content, download (secure/insecure), history
  • ChunkUploader    — upload log, connection monitor (ready for your impl.)

Run:  python p2p_ui.py
Reads shared state files written by your backend modules:
  content_dict.txt, user_to_ip.txt, ip_to_user.txt,
  received_log.txt, download_log.txt, sent_log.txt (uploader)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json, os, time, threading, math, socket, datetime

# ── Ports (must match your backend) ──────────────────────────────
UDP_PORT      = 6000
TCP_PORT      = 6001
BROADCAST_IP  = "192.168.1.255"
CHUNK_COUNT   = 3
BROADCAST_SEC = 8
WIPE_SEC      = 60

# ── Colour palette ────────────────────────────────────────────────
BG       = "#0f1117"
PANEL    = "#181c27"
CARD     = "#1e2333"
BORDER   = "#2a3050"
ACCENT   = "#1db97a"        # teal-green (online / success)
ACCENT2  = "#4e7cff"        # blue (secure)
WARN     = "#e8a020"        # amber (in-progress)
DANGER   = "#e84040"        # red (error / offline)
TEXT     = "#e8eaf0"
MUTED    = "#6b748f"
MONO     = "Courier"

# ── Shared state ─────────────────────────────────────────────────
_state = {
    "username":       "",
    "hosted_chunks":  [],
    "announcing":     False,
    "last_broadcast": None,
    "content_dict":   {},
    "user_to_ip":     {},
    "ip_to_user":     {},
}

# ── Helpers ───────────────────────────────────────────────────────
def read_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

def styled_btn(parent, text, cmd, color=ACCENT, width=18, **kw):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=BG, relief="flat", cursor="hand2",
                  font=("Helvetica", 10, "bold"), padx=10, pady=6,
                  activebackground=color, activeforeground=BG,
                  width=width, **kw)
    return b

def card_frame(parent, title="", **kw):
    outer = tk.Frame(parent, bg=CARD, bd=0, highlightbackground=BORDER,
                     highlightthickness=1)
    if title:
        tk.Label(outer, text=title, bg=CARD, fg=MUTED,
                 font=("Helvetica", 9, "bold"), anchor="w",
                 padx=12, pady=6).pack(fill="x")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x")
    inner = tk.Frame(outer, bg=CARD, padx=12, pady=10)
    inner.pack(fill="both", expand=True)
    return outer, inner

# ═════════════════════════════════════════════════════════════════
# TAB 1 — Announcer
# ═════════════════════════════════════════════════════════════════
class AnnouncerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(hdr, text="Chunk Announcer", bg=BG, fg=TEXT,
                 font=("Helvetica", 16, "bold")).pack(side="left")
        self.status_dot = tk.Label(hdr, text="●", bg=BG, fg=DANGER,
                                   font=("Helvetica", 14))
        self.status_dot.pack(side="left", padx=(12, 4))
        self.status_lbl = tk.Label(hdr, text="Offline", bg=BG, fg=MUTED,
                                   font=("Helvetica", 10))
        self.status_lbl.pack(side="left")

        # ── Setup card ───────────────────────────────────────────
        outer, inner = card_frame(self, "SETUP")
        outer.pack(fill="x", padx=20, pady=6)

        row = lambda lbl: self._lbl_entry(inner, lbl)
        self.e_user = row("Username")
        self.e_file = row("File path")

        browse_row = tk.Frame(inner, bg=CARD)
        browse_row.pack(fill="x", pady=(0, 6))
        styled_btn(browse_row, "Browse…", self._browse, color=ACCENT2,
                   width=10).pack(side="right")

        styled_btn(inner, "Split & Start Announcing", self._start,
                   width=26).pack(pady=(4, 0))

        # ── Chunk status card ────────────────────────────────────
        outer2, inner2 = card_frame(self, "HOSTED CHUNKS")
        outer2.pack(fill="x", padx=20, pady=6)
        self.chunk_frame = inner2

        # ── Broadcast log card ───────────────────────────────────
        outer3, inner3 = card_frame(self, "BROADCAST LOG")
        outer3.pack(fill="both", expand=True, padx=20, pady=6)
        self.log = scrolledtext.ScrolledText(inner3, bg=PANEL, fg=ACCENT,
                                             font=(MONO, 9), relief="flat",
                                             insertbackground=ACCENT, height=8)
        self.log.pack(fill="both", expand=True)
        self.log.config(state="disabled")

    def _lbl_entry(self, parent, label):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, bg=CARD, fg=MUTED,
                 font=("Helvetica", 9), width=10, anchor="w").pack(side="left")
        e = tk.Entry(row, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                     relief="flat", font=("Helvetica", 10), bd=4)
        e.pack(side="left", fill="x", expand=True)
        return e

    def _browse(self):
        path = filedialog.askopenfilename()
        if path:
            self.e_file.delete(0, "end")
            self.e_file.insert(0, path)

    def _start(self):
        username = self.e_user.get().strip()
        file_path = self.e_file.get().strip()
        if not username or not file_path:
            messagebox.showerror("Missing input", "Enter username and file path.")
            return
        if not os.path.exists(file_path):
            messagebox.showerror("File not found", f"'{file_path}' does not exist.")
            return

        _state["username"] = username
        _state["hosted_chunks"] = self._split(file_path)

        # persist username
        with open("user_info.txt", "w") as f:
            f.write(username)

        self._refresh_chunks()
        _state["announcing"] = True
        self.status_dot.config(fg=ACCENT)
        self.status_lbl.config(fg=ACCENT, text="Announcing")
        threading.Thread(target=self._broadcast_loop, daemon=True).start()
        self._log(f"[{ts()}] Started. User: {username}  Chunks: {len(_state['hosted_chunks'])}")

    def _split(self, path):
        size = os.path.getsize(path)
        chunk_size = math.ceil(size / CHUNK_COUNT)
        base = os.path.basename(path).split('.')[0]
        chunks = []
        with open(path, 'rb') as f:
            for i in range(1, CHUNK_COUNT + 1):
                data = f.read(chunk_size)
                name = f"{base}_{i}"
                with open(name, 'wb') as cf:
                    cf.write(data)
                chunks.append(name)
        return chunks

    def _refresh_chunks(self):
        for w in self.chunk_frame.winfo_children():
            w.destroy()
        cols = tk.Frame(self.chunk_frame, bg=CARD)
        cols.pack(fill="x")
        for i, name in enumerate(_state["hosted_chunks"]):
            c = tk.Frame(cols, bg=PANEL, bd=0,
                         highlightbackground=ACCENT, highlightthickness=1)
            c.pack(side="left", padx=(0, 8), pady=4, ipadx=10, ipady=6)
            tk.Label(c, text=f"chunk {i+1}", bg=PANEL, fg=MUTED,
                     font=("Helvetica", 8)).pack()
            tk.Label(c, text=name, bg=PANEL, fg=ACCENT,
                     font=(MONO, 9, "bold")).pack()
            sz = os.path.getsize(name) if os.path.exists(name) else 0
            tk.Label(c, text=f"{sz:,} B", bg=PANEL, fg=MUTED,
                     font=("Helvetica", 8)).pack()

    def _broadcast_loop(self):
        import json as _json
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception as e:
            self._log(f"[{ts()}] Socket error: {e}")
            return
        while _state["announcing"]:
            chunks = [f for f in os.listdir(".") if "_" in f and "." not in f]
            payload = {"username": _state["username"], "chunks": chunks}
            msg = _json.dumps(payload).encode()
            try:
                s.sendto(msg, (BROADCAST_IP, UDP_PORT))
                _state["last_broadcast"] = ts()
                self._log(f"[{ts()}] Broadcast → {payload}")
            except Exception as e:
                self._log(f"[{ts()}] Error: {e}")
            time.sleep(BROADCAST_SEC)

    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")


# ═════════════════════════════════════════════════════════════════
# TAB 2 — Content Discovery
# ═════════════════════════════════════════════════════════════════
class DiscoveryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()
        self._auto_refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(hdr, text="Content Discovery", bg=BG, fg=TEXT,
                 font=("Helvetica", 16, "bold")).pack(side="left")
        self.wipe_lbl = tk.Label(hdr, text="Next wipe: --", bg=BG, fg=MUTED,
                                 font=("Helvetica", 9))
        self.wipe_lbl.pack(side="right")
        styled_btn(hdr, "Refresh", self._refresh, color=ACCENT2,
                   width=8).pack(side="right", padx=8)

        # ── Peers card ───────────────────────────────────────────
        outer, inner = card_frame(self, "ONLINE PEERS")
        outer.pack(fill="x", padx=20, pady=6)

        cols = ["Username", "IP Address", "Chunks Hosted"]
        self.peer_tree = self._make_tree(inner, cols, height=5)
        self.peer_tree.pack(fill="x")

        # ── Content dict card ────────────────────────────────────
        outer2, inner2 = card_frame(self, "CHUNK → PEER MAP  (resets every 60s)")
        outer2.pack(fill="both", expand=True, padx=20, pady=6)

        cols2 = ["Chunk Name", "Held By"]
        self.chunk_tree = self._make_tree(inner2, cols2, height=10)
        self.chunk_tree.pack(fill="both", expand=True)

    def _make_tree(self, parent, cols, height=6):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("P2P.Treeview",
                        background=PANEL, foreground=TEXT,
                        fieldbackground=PANEL, rowheight=26,
                        font=("Helvetica", 9))
        style.configure("P2P.Treeview.Heading",
                        background=CARD, foreground=MUTED,
                        font=("Helvetica", 9, "bold"), relief="flat")
        style.map("P2P.Treeview", background=[("selected", BORDER)])

        tree = ttk.Treeview(parent, columns=cols, show="headings",
                             style="P2P.Treeview", height=height)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="w", width=160)
        return tree

    def _refresh(self):
        cd   = read_json_file("content_dict.txt")
        u2ip = read_json_file("user_to_ip.txt")
        ip2u = read_json_file("ip_to_user.txt")
        _state["content_dict"] = cd
        _state["user_to_ip"]   = u2ip
        _state["ip_to_user"]   = ip2u

        # peers
        for row in self.peer_tree.get_children():
            self.peer_tree.delete(row)
        for user, ip in u2ip.items():
            chunk_count = sum(1 for v in cd.values() if user in v)
            self.peer_tree.insert("", "end", values=(user, ip, chunk_count))

        # chunk map
        for row in self.chunk_tree.get_children():
            self.chunk_tree.delete(row)
        for chunk, owners in cd.items():
            self.chunk_tree.insert("", "end",
                                   values=(chunk, ", ".join(owners)))

    def _auto_refresh(self):
        self._refresh()
        self.after(5000, self._auto_refresh)   # refresh every 5 s


# ═════════════════════════════════════════════════════════════════
# TAB 3 — Downloader
# ═════════════════════════════════════════════════════════════════
class DownloaderTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(hdr, text="Chunk Downloader", bg=BG, fg=TEXT,
                 font=("Helvetica", 16, "bold")).pack(side="left")

        # ── Available content card ────────────────────────────────
        outer, inner = card_frame(self, "AVAILABLE CONTENT")
        outer.pack(fill="x", padx=20, pady=6)

        btn_row = tk.Frame(inner, bg=CARD)
        btn_row.pack(fill="x", pady=(0, 6))
        styled_btn(btn_row, "Refresh list", self._refresh_content,
                   color=ACCENT2, width=14).pack(side="left")

        self.content_lb = tk.Listbox(inner, bg=PANEL, fg=TEXT, selectbackground=BORDER,
                                     font=(MONO, 10), relief="flat", height=5,
                                     activestyle="none")
        self.content_lb.pack(fill="x")
        self._refresh_content()

        # ── Download form card ───────────────────────────────────
        outer2, inner2 = card_frame(self, "DOWNLOAD")
        outer2.pack(fill="x", padx=20, pady=6)

        row1 = tk.Frame(inner2, bg=CARD)
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="Filename", bg=CARD, fg=MUTED,
                 font=("Helvetica", 9), width=10, anchor="w").pack(side="left")
        self.e_fname = tk.Entry(row1, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                                relief="flat", font=("Helvetica", 10), bd=4)
        self.e_fname.pack(side="left", fill="x", expand=True)
        styled_btn(row1, "Use selected", self._use_selected,
                   color=BORDER, width=12).pack(side="left", padx=(6, 0))

        row2 = tk.Frame(inner2, bg=CARD)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="Mode", bg=CARD, fg=MUTED,
                 font=("Helvetica", 9), width=10, anchor="w").pack(side="left")
        self.mode_var = tk.StringVar(value="unsecure")
        for val, lbl, col in [("unsecure", "Unsecure (plain)", WARN),
                               ("secure",   "Secure (DH + DES)", ACCENT2)]:
            tk.Radiobutton(row2, text=lbl, variable=self.mode_var, value=val,
                           bg=CARD, fg=col, selectcolor=PANEL,
                           activebackground=CARD, activeforeground=col,
                           font=("Helvetica", 9)).pack(side="left", padx=8)

        styled_btn(inner2, "Download", self._download, width=14).pack(pady=(6, 0))

        # ── Transfer progress ────────────────────────────────────
        outer3, inner3 = card_frame(self, "TRANSFER LOG")
        outer3.pack(fill="both", expand=True, padx=20, pady=6)
        self.xfer_log = scrolledtext.ScrolledText(inner3, bg=PANEL, fg=TEXT,
                                                  font=(MONO, 9), relief="flat",
                                                  insertbackground=TEXT, height=7)
        self.xfer_log.pack(fill="both", expand=True)
        self.xfer_log.config(state="disabled")

    def _refresh_content(self):
        cd = read_json_file("content_dict.txt")
        unique = list({k.rsplit("_", 1)[0] for k in cd})
        self.content_lb.delete(0, "end")
        for name in sorted(unique):
            self.content_lb.insert("end", f"  {name}.png")

    def _use_selected(self):
        sel = self.content_lb.curselection()
        if not sel:
            return
        val = self.content_lb.get(sel[0]).strip()
        self.e_fname.delete(0, "end")
        self.e_fname.insert(0, val)

    def _download(self):
        fname = self.e_fname.get().strip()
        if not fname:
            messagebox.showerror("Missing input", "Enter a filename to download.")
            return
        mode = self.mode_var.get()
        self._log(f"[{ts()}] Starting {'🔒 secure' if mode=='secure' else '🔓 plain'} "
                  f"download of '{fname}'")
        threading.Thread(target=self._do_download,
                         args=(fname, mode), daemon=True).start()

    def _do_download(self, fname, mode):
        base = fname.split('.')[0]
        chunks = [f"{base}_{i}.png" for i in range(1, CHUNK_COUNT + 1)]
        cd    = read_json_file("content_dict.txt")
        u2ip  = read_json_file("user_to_ip.txt")

        all_ok = True
        for chunk in chunks:
            owners = cd.get(chunk, [])
            if not owners:
                self._log(f"  ✗  CHUNK {chunk} — no peers available")
                all_ok = False
                continue

            downloaded = False
            for user in owners:
                ip = u2ip.get(user)
                if not ip:
                    continue
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((ip, TCP_PORT))
                    self._log(f"  → [{ts()}] Requesting '{chunk}' from '{user}' ({ip})")

                    if mode == "secure":
                        import random, pyDes, base64
                        X = random.randint(2, 905)
                        pub = pow(7, X, 907)
                        s.send(json.dumps({"key": str(pub)}).encode())
                        Y = int(json.loads(s.recv(1024).decode())["key"])
                        secret = pow(Y, X, 907)
                        key = str(secret).zfill(8)[:8].encode()
                        s.send(json.dumps({"requested secured content": chunk}).encode())
                        data = json.loads(s.recv(65536).decode())
                        enc = base64.b64decode(data["encrypted chunk"])
                        chunk_bytes = pyDes.des(key, pyDes.ECB, pad=None,
                                                padmode=pyDes.PAD_PKCS5).decrypt(enc)
                    else:
                        s.send(json.dumps({"requested content": chunk}).encode())
                        data = s.recv(65536)
                        import base64 as _b64
                        payload = json.loads(data.decode())
                        chunk_bytes = _b64.b64decode(payload.get("data", ""))

                    with open(chunk, "wb") as f:
                        f.write(chunk_bytes)

                    # log
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open("received_log.txt", "a") as f:
                        f.write(f"{now} | {chunk} | {user} | RECEIVED\n")
                    with open("download_log.txt", "a") as f:
                        f.write(f"{now} | {chunk} | {ip}\n")

                    self._log(f"  ✓  '{chunk}' downloaded from '{user}'")
                    s.close()
                    downloaded = True
                    break
                except Exception as e:
                    self._log(f"  ✗  '{chunk}' failed from '{user}': {e}")
                    try: s.close()
                    except: pass

            if not downloaded:
                self._log(f"  ✗  CHUNK {chunk} CANNOT BE DOWNLOADED FROM ONLINE PEERS.")
                all_ok = False

        if all_ok:
            # merge
            with open(fname, "wb") as out:
                for c in chunks:
                    with open(c, "rb") as f:
                        out.write(f.read())
            self._log(f"[{ts()}] ✓ '{fname}' merged and saved successfully!")

    def _log(self, msg):
        def _do():
            self.xfer_log.config(state="normal")
            self.xfer_log.insert("end", msg + "\n")
            self.xfer_log.see("end")
            self.xfer_log.config(state="disabled")
        self.after(0, _do)


# ═════════════════════════════════════════════════════════════════
# TAB 4 — Uploader
# ═════════════════════════════════════════════════════════════════
class UploaderTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()
        self._auto_refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(hdr, text="Chunk Uploader", bg=BG, fg=TEXT,
                 font=("Helvetica", 16, "bold")).pack(side="left")
        self.listen_dot = tk.Label(hdr, text="●", bg=BG, fg=MUTED,
                                   font=("Helvetica", 14))
        self.listen_dot.pack(side="left", padx=(10, 4))
        self.listen_lbl = tk.Label(hdr, text="Not listening", bg=BG, fg=MUTED,
                                   font=("Helvetica", 9))
        self.listen_lbl.pack(side="left")

        note = tk.Frame(self, bg=PANEL, bd=0,
                        highlightbackground=WARN, highlightthickness=1)
        note.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(note, bg=PANEL, fg=WARN, padx=14, pady=8,
                 font=("Helvetica", 9),
                 text="⚠  ChunkUploader backend not yet implemented.\n"
                      "   Start chunk_uploader.py in a separate terminal on port 6001.\n"
                      "   This panel shows live connection logs from sent_log.txt.").pack(anchor="w")

        # ── Connection log ───────────────────────────────────────
        outer, inner = card_frame(self, "UPLOAD LOG  (sent_log.txt)")
        outer.pack(fill="both", expand=True, padx=20, pady=6)
        self.upload_log = scrolledtext.ScrolledText(inner, bg=PANEL, fg=ACCENT2,
                                                    font=(MONO, 9), relief="flat",
                                                    insertbackground=ACCENT2, height=14)
        self.upload_log.pack(fill="both", expand=True)
        self.upload_log.config(state="disabled")

        # ── Stats row ────────────────────────────────────────────
        outer2, inner2 = card_frame(self, "STATS")
        outer2.pack(fill="x", padx=20, pady=6)
        self.stats_frame = inner2
        self._build_stats(inner2)

    def _build_stats(self, parent):
        for i, (lbl, key) in enumerate([
            ("Chunks Sent",     "sent"),
            ("Secure Uploads",  "secure"),
            ("Plain Uploads",   "plain"),
            ("Unique Receivers","receivers"),
        ]):
            f = tk.Frame(parent, bg=PANEL, bd=0,
                         highlightbackground=BORDER, highlightthickness=1)
            f.grid(row=0, column=i, padx=(0, 10), pady=4, ipadx=14, ipady=8, sticky="ew")
            parent.columnconfigure(i, weight=1)
            tk.Label(f, text=lbl, bg=PANEL, fg=MUTED,
                     font=("Helvetica", 8)).pack()
            lv = tk.Label(f, text="0", bg=PANEL, fg=TEXT,
                          font=("Helvetica", 18, "bold"))
            lv.pack()
            setattr(self, f"stat_{key}", lv)

    def _auto_refresh(self):
        self._refresh_log()
        self.after(3000, self._auto_refresh)

    def _refresh_log(self):
        try:
            with open("sent_log.txt", "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        self.upload_log.config(state="normal")
        self.upload_log.delete("1.0", "end")
        for line in lines[-100:]:
            self.upload_log.insert("end", line)
        self.upload_log.see("end")
        self.upload_log.config(state="disabled")

        # stats
        sent = len(lines)
        secure = sum(1 for l in lines if "SECURE" in l.upper())
        plain  = sent - secure
        receivers = len({l.split("|")[2].strip() for l in lines if "|" in l})
        self.stat_sent.config(text=str(sent))
        self.stat_secure.config(text=str(secure))
        self.stat_plain.config(text=str(plain))
        self.stat_receivers.config(text=str(receivers))

        # status dot — green if log updated in last 30 s
        if lines:
            try:
                last_ts = lines[-1].split("|")[0].strip()
                last_dt = datetime.datetime.strptime(last_ts, "%Y-%m-%d %H:%M:%S")
                age = (datetime.datetime.now() - last_dt).seconds
                if age < 30:
                    self.listen_dot.config(fg=ACCENT)
                    self.listen_lbl.config(fg=ACCENT, text="Active (recent upload)")
                    return
            except Exception:
                pass
        self.listen_dot.config(fg=MUTED)
        self.listen_lbl.config(fg=MUTED, text="No recent activity")


# ═════════════════════════════════════════════════════════════════
# TAB 5 — History
# ═════════════════════════════════════════════════════════════════
class HistoryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()
        self._refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(hdr, text="History & Logs", bg=BG, fg=TEXT,
                 font=("Helvetica", 16, "bold")).pack(side="left")
        styled_btn(hdr, "Refresh", self._refresh, color=ACCENT2,
                   width=8).pack(side="right")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=20, pady=6)

        style = ttk.Style()
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD, foreground=MUTED,
                        padding=[10, 5], font=("Helvetica", 9))
        style.map("TNotebook.Tab", background=[("selected", PANEL)],
                  foreground=[("selected", TEXT)])

        self.recv_txt  = self._tab(nb, "Received log")
        self.dl_txt    = self._tab(nb, "Download log")
        self.sent_txt  = self._tab(nb, "Upload log")

    def _tab(self, nb, title):
        frame = tk.Frame(nb, bg=PANEL)
        nb.add(frame, text=title)
        txt = scrolledtext.ScrolledText(frame, bg=PANEL, fg=TEXT,
                                        font=(MONO, 9), relief="flat",
                                        insertbackground=TEXT)
        txt.pack(fill="both", expand=True, padx=4, pady=4)
        return txt

    def _refresh(self):
        for path, widget, color in [
            ("received_log.txt", self.recv_txt,  ACCENT),
            ("download_log.txt", self.dl_txt,    ACCENT2),
            ("sent_log.txt",     self.sent_txt,  WARN),
        ]:
            widget.config(fg=color, state="normal")
            widget.delete("1.0", "end")
            try:
                with open(path) as f:
                    widget.insert("end", f.read())
            except FileNotFoundError:
                widget.insert("end", f"(no {path} found yet)\n")
            widget.config(state="disabled")


# ═════════════════════════════════════════════════════════════════
# Main window
# ═════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PeerShare — P2P File Sharing")
        self.geometry("920x680")
        self.configure(bg=BG)
        self.minsize(800, 600)
        self._build_sidebar()

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=PANEL, width=170)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(sidebar, bg=PANEL)
        logo.pack(fill="x", pady=(20, 16), padx=16)
        tk.Label(logo, text="⇅", bg=PANEL, fg=ACCENT,
                 font=("Helvetica", 22)).pack(side="left")
        tk.Label(logo, text="PeerShare", bg=PANEL, fg=TEXT,
                 font=("Helvetica", 12, "bold")).pack(side="left", padx=6)

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=12)

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        tabs = [
            ("📡  Announcer",    AnnouncerTab),
            ("🔍  Discovery",    DiscoveryTab),
            ("⬇  Downloader",   DownloaderTab),
            ("⬆  Uploader",     UploaderTab),
            ("📋  History",      HistoryTab),
        ]

        self._tabs = {}
        self._active_btn = None
        self._active_tab = None

        for label, cls in tabs:
            tab = cls(self.content)
            self._tabs[label] = tab
            btn = tk.Button(sidebar, text=label, anchor="w",
                            bg=PANEL, fg=MUTED, relief="flat",
                            font=("Helvetica", 10), padx=16, pady=9,
                            cursor="hand2", activebackground=CARD,
                            activeforeground=TEXT,
                            command=lambda l=label: self._show(l))
            btn.pack(fill="x")
            self._tabs[label + "_btn"] = btn

        # show first tab
        self._show("📡  Announcer")

    def _show(self, label):
        if self._active_tab:
            self._active_tab.pack_forget()
        if self._active_btn:
            self._active_btn.config(bg=PANEL, fg=MUTED)

        tab = self._tabs[label]
        tab.pack(fill="both", expand=True)
        self._active_tab = tab

        btn = self._tabs[label + "_btn"]
        btn.config(bg=CARD, fg=TEXT)
        self._active_btn = btn


if __name__ == "__main__":
    app = App()
    app.mainloop()