import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import threading
import os
from network_core import NetworkCore

# Setup Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Multi-Protocol Network Toolkit - Team 8")
        self.geometry("1000x650")
        self.minsize(800, 500)

        self.network_core = None
        self.username = None
        
        # State variables
        self.discovered_devices = {} # ip -> username

        self._show_login()

    def _show_login(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.login_label = ctk.CTkLabel(self.login_frame, text="Network Toolkit", font=ctk.CTkFont(size=28, weight="bold"))
        self.login_label.pack(pady=(30, 10), padx=50)
        
        self.subtitle_label = ctk.CTkLabel(self.login_frame, text="Please enter a username to continue", font=ctk.CTkFont(size=14))
        self.subtitle_label.pack(pady=(0, 20), padx=50)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username...", width=250, height=40)
        self.username_entry.pack(pady=10, padx=50)
        self.username_entry.bind("<Return>", lambda e: self._do_login())

        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", command=self._do_login, width=250, height=40)
        self.login_btn.pack(pady=(10, 30), padx=50)

    def _do_login(self):
        user = self.username_entry.get().strip()
        if not user:
            messagebox.showerror("Error", "Username is required")
            return
        
        self.username = user
        self.login_frame.destroy()
        self._init_network_core()
        self._show_main_dashboard()

    def _init_network_core(self):
        try:
            self.network_core = NetworkCore(self.username)
            self.network_core.on_device_discovered = self.handle_device_discovered
            self.network_core.on_message_received = self.handle_message_received
            self.network_core.on_file_progress = self.handle_file_progress
            self.network_core.on_file_received = self.handle_file_received
        except Exception as e:
            messagebox.showerror("Network Error", f"Failed to initialize network sockets.\nCheck your firewall settings.\nError: {e}")
            self.destroy()

    def _show_main_dashboard(self):
        # Configure Grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------------- Sidebar ----------------
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Toolkit", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.user_label = ctk.CTkLabel(self.sidebar_frame, text=f"User: {self.username}", font=ctk.CTkFont(size=14, slant="italic"))
        self.user_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.btn_discovery = ctk.CTkButton(self.sidebar_frame, text="Discovery", command=lambda: self.select_frame("discovery"))
        self.btn_discovery.grid(row=2, column=0, padx=20, pady=10)

        self.btn_messaging = ctk.CTkButton(self.sidebar_frame, text="Messaging", command=lambda: self.select_frame("messaging"))
        self.btn_messaging.grid(row=3, column=0, padx=20, pady=10)

        self.btn_file = ctk.CTkButton(self.sidebar_frame, text="File Transfer", command=lambda: self.select_frame("file"))
        self.btn_file.grid(row=4, column=0, padx=20, pady=10)

        self.btn_tools = ctk.CTkButton(self.sidebar_frame, text="Network Tools", command=lambda: self.select_frame("tools"))
        self.btn_tools.grid(row=5, column=0, padx=20, pady=10)

        self.btn_logs = ctk.CTkButton(self.sidebar_frame, text="Logs", command=lambda: self.select_frame("logs"))
        self.btn_logs.grid(row=6, column=0, padx=20, pady=10)

        self.btn_about = ctk.CTkButton(self.sidebar_frame, text="About", command=lambda: self.select_frame("about"))
        self.btn_about.grid(row=7, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # ---------------- Main Frames ----------------
        self.frames = {}
        
        # Discovery Frame
        self.frames["discovery"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["discovery"].grid_columnconfigure(0, weight=1)
        self.frames["discovery"].grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self.frames["discovery"], text="Device Discovery (UDP Broadcast)", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.discovery_btn = ctk.CTkButton(self.frames["discovery"], text="Discover Devices", command=self.do_discovery)
        self.discovery_btn.grid(row=0, column=0, padx=20, pady=20, sticky="e")
        
        # Treeview Style for Dark Theme
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2b2b2b",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", 
                        background="#565b5e",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading", background=[('active', '#343638')])
        
        self.discovery_table = ttk.Treeview(self.frames["discovery"], columns=("IP", "Port", "Username", "OS", "Status"), show="headings")
        self.discovery_table.heading("IP", text="IP Address")
        self.discovery_table.heading("Port", text="Port")
        self.discovery_table.heading("Username", text="Username")
        self.discovery_table.heading("OS", text="OS")
        self.discovery_table.heading("Status", text="Status")
        
        self.discovery_table.column("IP", width=150, anchor="center")
        self.discovery_table.column("Port", width=80, anchor="center")
        self.discovery_table.column("Username", width=150, anchor="center")
        self.discovery_table.column("OS", width=100, anchor="center")
        self.discovery_table.column("Status", width=100, anchor="center")
        
        self.discovery_table.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Messaging Frame
        self.frames["messaging"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["messaging"].grid_columnconfigure(0, weight=1)
        self.frames["messaging"].grid_rowconfigure(1, weight=1)
        
        msg_top = ctk.CTkFrame(self.frames["messaging"], fg_color="transparent")
        msg_top.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        msg_top.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(msg_top, text="Chat with IP:").grid(row=0, column=0, padx=(0,10))
        self.msg_ip_entry = ctk.CTkEntry(msg_top, placeholder_text="Enter IP address...")
        self.msg_ip_entry.grid(row=0, column=1, sticky="ew")
        
        self.chat_history = ctk.CTkTextbox(self.frames["messaging"])
        self.chat_history.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.chat_history.configure(state="disabled")
        
        msg_bottom = ctk.CTkFrame(self.frames["messaging"], fg_color="transparent")
        msg_bottom.grid(row=2, column=0, padx=20, pady=(0,20), sticky="ew")
        msg_bottom.grid_columnconfigure(0, weight=1)
        
        self.msg_entry = ctk.CTkEntry(msg_bottom, placeholder_text="Type a message...")
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0,10))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())
        
        ctk.CTkButton(msg_bottom, text="Send", width=80, command=self.send_message).grid(row=0, column=1)

        # File Transfer Frame
        self.frames["file"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["file"].grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.frames["file"], text="TCP File Transfer", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        file_input_frame = ctk.CTkFrame(self.frames["file"])
        file_input_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        file_input_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(file_input_frame, text="Target IP:").grid(row=0, column=0, padx=10, pady=10)
        self.file_ip_entry = ctk.CTkEntry(file_input_frame, placeholder_text="Enter IP address...")
        self.file_ip_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(file_input_frame, text="File:").grid(row=1, column=0, padx=10, pady=10)
        self.filepath_entry = ctk.CTkEntry(file_input_frame, placeholder_text="No file selected...", state="disabled")
        self.filepath_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(file_input_frame, text="Browse", width=80, command=self.browse_file).grid(row=1, column=2, padx=10, pady=10)
        
        self.send_file_btn = ctk.CTkButton(self.frames["file"], text="Send File", command=self.send_file)
        self.send_file_btn.grid(row=2, column=0, padx=20, pady=20)
        
        self.file_status_label = ctk.CTkLabel(self.frames["file"], text="")
        self.file_status_label.grid(row=3, column=0, padx=20, pady=10)

        # Network Tools Frame
        self.frames["tools"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["tools"].grid_columnconfigure(0, weight=1)
        self.frames["tools"].grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self.frames["tools"], text="Network Tools", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        tools_input_frame = ctk.CTkFrame(self.frames["tools"])
        tools_input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        tools_input_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(tools_input_frame, text="Target IP:").grid(row=0, column=0, padx=10, pady=10)
        self.tools_ip_entry = ctk.CTkEntry(tools_input_frame, placeholder_text="Enter IP to scan/ping...")
        self.tools_ip_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(tools_input_frame, text="Ping", width=80, command=self.run_ping).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkButton(tools_input_frame, text="Scan Ports", width=100, command=self.run_scan).grid(row=0, column=3, padx=10, pady=10)
        
        self.tools_output = ctk.CTkTextbox(self.frames["tools"])
        self.tools_output.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.tools_output.configure(state="disabled")

        # Logs Frame
        self.frames["logs"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["logs"].grid_columnconfigure(0, weight=1)
        self.frames["logs"].grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self.frames["logs"], text="System Logs", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        logs_top = ctk.CTkFrame(self.frames["logs"], fg_color="transparent")
        logs_top.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        logs_top.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(logs_top, text="Search Filter:").grid(row=0, column=0, padx=(0, 10))
        self.logs_search = ctk.CTkEntry(logs_top, placeholder_text="Type to filter logs...")
        self.logs_search.grid(row=0, column=1, sticky="ew")
        self.logs_search.bind("<KeyRelease>", self.filter_logs)
        
        ctk.CTkButton(logs_top, text="Refresh", width=80, command=self.load_logs).grid(row=0, column=2, padx=10)
        ctk.CTkButton(logs_top, text="Clear Logs", width=80, fg_color="#a83232", hover_color="#7a2121", command=self.clear_logs).grid(row=0, column=3)
        
        self.logs_textbox = ctk.CTkTextbox(self.frames["logs"], font=("Consolas", 12))
        self.logs_textbox.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.logs_textbox.configure(state="disabled")

        # About Frame
        self.frames["about"] = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["about"].grid_columnconfigure(0, weight=1)

        title_font = ctk.CTkFont(size=26, weight="bold")
        heading_font = ctk.CTkFont(size=18, weight="bold")
        normal_font = ctk.CTkFont(size=14)

        ctk.CTkLabel(self.frames["about"], text="TEAM 8", font=title_font, text_color="#3b8ed0").pack(pady=(20, 5))
        ctk.CTkLabel(self.frames["about"], text="Project: Multi-Protocol Network Toolkit", font=heading_font, text_color="#3b8ed0").pack(pady=(0, 20))

        # Project Goal
        ctk.CTkLabel(self.frames["about"], text="Project Goal:", font=heading_font, text_color="#3b8ed0", anchor="w").pack(fill="x", padx=20, pady=(10, 5))
        idea_text = "A Python GUI application that provides multiple network tools such as device discovery,\nUDP messaging, TCP file transfer, connectivity testing, port checking, and logging."
        ctk.CTkLabel(self.frames["about"], text=idea_text, font=normal_font, justify="left").pack(fill="x", padx=30)

        # Port Definitions
        ctk.CTkLabel(self.frames["about"], text="Port Definitions:", font=heading_font, text_color="#3b8ed0", anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        ports_text = (
            "• Port 50000 (UDP) : Broadcasting discovery packets and P2P messaging.\n"
            "• Port 50001 (TCP) : Establishing reliable connections for file transfers.\n"
            "• Port 21 (TCP)    : Standard File Transfer Protocol (FTP) port.\n"
            "• Port 22 (TCP)    : Secure Shell (SSH) port for remote access.\n"
            "• Port 80 (TCP)    : Unencrypted web traffic (HTTP).\n"
            "• Port 443 (TCP)   : Encrypted web traffic (HTTPS).\n"
            "• Port 8080 (TCP)  : Common alternative HTTP port or Proxy."
        )
        ctk.CTkLabel(self.frames["about"], text=ports_text, font=normal_font, justify="left").pack(fill="x", padx=30)

        # Team Members
        ctk.CTkLabel(self.frames["about"], text="Team Members:", font=heading_font, text_color="#3b8ed0", anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        team_text = "Mohamed Ahmed Saeed Toaiman\nAli Soliman Mohamed\nMubarak Ali Ali Saeed\nMohamed Ayman Mohamed Ibrahim\nMahmoud Reda Mahmoud\nIslam ElSaeed Ragab Abdullah"
        ctk.CTkLabel(self.frames["about"], text=team_text, font=normal_font, justify="left").pack(fill="x", padx=30)

        # Copyright
        ctk.CTkLabel(self.frames["about"], text="Copyright @ Islam Ragab", font=heading_font, text_color="#7a7a7a").pack(pady=(30, 30))

        # Select default frame
        self.select_frame("discovery")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def select_frame(self, name):
        # Update button colors
        self.btn_discovery.configure(fg_color=("gray75", "gray25") if name == "discovery" else "transparent")
        self.btn_messaging.configure(fg_color=("gray75", "gray25") if name == "messaging" else "transparent")
        self.btn_file.configure(fg_color=("gray75", "gray25") if name == "file" else "transparent")
        self.btn_tools.configure(fg_color=("gray75", "gray25") if name == "tools" else "transparent")
        self.btn_logs.configure(fg_color=("gray75", "gray25") if name == "logs" else "transparent")
        self.btn_about.configure(fg_color=("gray75", "gray25") if name == "about" else "transparent")

        if name == "logs":
            self.load_logs()

        # Show selected frame
        for frame_name, frame in self.frames.items():
            if frame_name == name:
                frame.grid(row=0, column=1, sticky="nsew")
            else:
                frame.grid_forget()

    # --- Callbacks from Network Core ---
    def handle_device_discovered(self, ip, port, username, os_info, status):
        # Prevent duplicates if the same username broadcasts from both LAN IP and 127.0.0.1
        if username in self.discovered_devices.values():
            return
            
        if ip not in self.discovered_devices:
            self.discovered_devices[ip] = username
            self.after(0, self._append_discovery, (ip, port, username, os_info, status))
            # Also auto-fill IPs in other tabs to be helpful if they are empty
            self.after(0, self._autofill_ips, ip)

    def _append_discovery(self, data):
        self.discovery_table.insert("", "end", values=data)

    def _autofill_ips(self, ip):
        if not self.msg_ip_entry.get():
            self.msg_ip_entry.insert(0, ip)
        if not self.file_ip_entry.get():
            self.file_ip_entry.insert(0, ip)
        if not self.tools_ip_entry.get():
            self.tools_ip_entry.insert(0, ip)

    def handle_message_received(self, ip, username, content):
        msg = f"[{username}@{ip}]: {content}"
        self.after(0, self._append_chat, msg)

    def _append_chat(self, msg):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", msg + "\n")
        self.chat_history.see("end")
        self.chat_history.configure(state="disabled")

    def handle_file_progress(self, filename, current, total):
        pass # Optional: update a progress bar. Simplified for now.

    def handle_file_received(self, username, filename):
        self.after(0, messagebox.showinfo, "File Received", f"Received file '{filename}' from {username}.\nSaved in 'received_files' folder.")

    # --- UI Actions ---
    def do_discovery(self):
        # Clear existing items in the treeview
        for item in self.discovery_table.get_children():
            self.discovery_table.delete(item)
            
        self.discovered_devices.clear()
        self.network_core.discover_devices()

    def send_message(self):
        ip = self.msg_ip_entry.get().strip()
        msg = self.msg_entry.get()
        if not ip or not msg:
            return
        
        self.network_core.send_message(ip, msg)
        self._append_chat(f"[You -> {ip}]: {msg}")
        self.msg_entry.delete(0, "end")

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.filepath_entry.configure(state="normal")
            self.filepath_entry.delete(0, "end")
            self.filepath_entry.insert(0, filename)
            self.filepath_entry.configure(state="disabled")

    def send_file(self):
        ip = self.file_ip_entry.get().strip()
        filepath = self.filepath_entry.get().strip()
        
        if not ip or not filepath:
            messagebox.showwarning("Warning", "IP address and file must be selected.")
            return
            
        self.file_status_label.configure(text=f"Sending {os.path.basename(filepath)}...")
        # Send in a background thread using network_core
        self.network_core.send_file(ip, filepath)
        self.file_status_label.configure(text=f"Transfer initiated to {ip}")

    def run_ping(self):
        ip = self.tools_ip_entry.get().strip()
        if not ip:
            return
        
        self.tools_output.configure(state="normal")
        self.tools_output.insert("end", f"Pinging {ip}...\n")
        self.tools_output.configure(state="disabled")
        
        def ping_thread():
            success, out = self.network_core.check_connectivity(ip)
            self.after(0, self._append_tools_output, out)
            
        threading.Thread(target=ping_thread, daemon=True).start()

    def run_scan(self):
        ip = self.tools_ip_entry.get().strip()
        if not ip:
            return
            
        self.tools_output.configure(state="normal")
        self.tools_output.insert("end", f"Scanning common ports on {ip}...\n")
        self.tools_output.configure(state="disabled")
        
        def scan_thread():
            results = self.network_core.scan_ports(ip)
            out = f"Port Scan Results for {ip}:\n"
            for port, is_open in results.items():
                status = "OPEN" if is_open else "CLOSED"
                out += f"Port {port}: {status}\n"
            out += "-"*20 + "\n"
            self.after(0, self._append_tools_output, out)
            
        threading.Thread(target=scan_thread, daemon=True).start()

    def _append_tools_output(self, text):
        self.tools_output.configure(state="normal")
        self.tools_output.insert("end", text + "\n")
        self.tools_output.see("end")
        self.tools_output.configure(state="disabled")

    def load_logs(self):
        self.logs_textbox.configure(state="normal")
        self.logs_textbox.delete("0.0", "end")
        try:
            if os.path.exists("network_toolkit_log.txt"):
                with open("network_toolkit_log.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                self.full_logs = content
                self.logs_textbox.insert("end", content)
                self.logs_textbox.see("end")
            else:
                self.full_logs = "No logs found."
                self.logs_textbox.insert("end", "No logs found.")
        except Exception as e:
            self.logs_textbox.insert("end", f"Error loading logs: {e}")
            self.full_logs = ""
        self.logs_textbox.configure(state="disabled")
        self.filter_logs() # Apply any existing filter

    def filter_logs(self, event=None):
        query = self.logs_search.get().lower()
        self.logs_textbox.configure(state="normal")
        self.logs_textbox.delete("0.0", "end")
        if not query:
            self.logs_textbox.insert("end", getattr(self, "full_logs", ""))
        else:
            lines = getattr(self, "full_logs", "").split("\n")
            filtered = [line for line in lines if query in line.lower()]
            self.logs_textbox.insert("end", "\n".join(filtered))
        self.logs_textbox.see("end")
        self.logs_textbox.configure(state="disabled")

    def clear_logs(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all logs?"):
            try:
                open("network_toolkit_log.txt", "w").close()
                self.load_logs()
            except Exception as e:
                messagebox.showerror("Error", f"Could not clear logs: {e}")

    def destroy(self):
        if self.network_core:
            self.network_core.stop()
        super().destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
