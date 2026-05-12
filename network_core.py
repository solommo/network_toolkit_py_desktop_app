import socket
import threading
import json
import os
import subprocess
import platform
from logger import log_info, log_error, log_warning

UDP_PORT = 50000
TCP_PORT = 50001
BUFFER_SIZE = 4096

class NetworkCore:
    def __init__(self, username):
        self.username = username
        self.running = True
        self.udp_socket = None
        self.tcp_socket = None
        
        # Callbacks
        self.on_device_discovered = None
        self.on_message_received = None
        self.on_file_progress = None
        self.on_file_received = None

        self._init_udp()
        self._init_tcp()

    def _init_udp(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Enable broadcasting mode
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Allow multiple instances on the same machine to bind to the same port (useful for testing)
        if hasattr(socket, 'SO_REUSEPORT'):
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        else:
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
        self.udp_socket.bind(('', UDP_PORT))
        
        threading.Thread(target=self._udp_listener, daemon=True).start()

    def _init_tcp(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(('', TCP_PORT))
        self.tcp_socket.listen(5)
        
        threading.Thread(target=self._tcp_listener, daemon=True).start()

    def _udp_listener(self):
        log_info(f"UDP Listener started on port {UDP_PORT}")
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8')
                
                try:
                    msg_data = json.loads(message)
                    msg_type = msg_data.get("type")
                    
                    if msg_type == "discovery":
                        peer_user = msg_data.get("username", "Unknown")
                        peer_os = msg_data.get("os", "Unknown")
                        peer_status = msg_data.get("status", "Online")
                        
                        # Show ourselves as well
                        log_info(f"Discovered device: {addr[0]}:{addr[1]} - {peer_user}")
                        if self.on_device_discovered:
                            self.on_device_discovered(addr[0], addr[1], peer_user, peer_os, peer_status)
                            
                        # Reply to the sender so they know we exist too (but don't reply to ourselves)
                        if peer_user != self.username:
                            reply_msg = json.dumps({"type": "discovery_reply", "username": self.username, "os": platform.system(), "status": "Online"}).encode('utf-8')
                            self.udp_socket.sendto(reply_msg, addr)
                    
                    elif msg_type == "discovery_reply":
                        peer_user = msg_data.get("username", "Unknown")
                        peer_os = msg_data.get("os", "Unknown")
                        peer_status = msg_data.get("status", "Online")
                        log_info(f"Discovery reply from: {addr[0]}:{addr[1]} - {peer_user}")
                        if self.on_device_discovered:
                            self.on_device_discovered(addr[0], addr[1], peer_user, peer_os, peer_status)

                    elif msg_type == "message":
                        peer_user = msg_data.get("username")
                        content = msg_data.get("content")
                        log_info(f"Message received from {peer_user} ({addr[0]}): {content}")
                        if self.on_message_received:
                            self.on_message_received(addr[0], peer_user, content)

                except json.JSONDecodeError:
                    log_warning(f"Received malformed UDP packet from {addr[0]}")
            except Exception as e:
                if self.running:
                    log_error(f"UDP listener error: {e}")

    def _tcp_listener(self):
        log_info(f"TCP Listener started on port {TCP_PORT}")
        while self.running:
            try:
                conn, addr = self.tcp_socket.accept()
                threading.Thread(target=self._handle_tcp_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                if self.running:
                    log_error(f"TCP listener error: {e}")

    def _handle_tcp_client(self, conn, addr):
        try:
            # First receive metadata
            meta_data = conn.recv(BUFFER_SIZE).decode('utf-8')
            meta_json = json.loads(meta_data)
            
            filename = meta_json.get("filename")
            filesize = meta_json.get("filesize")
            sender_name = meta_json.get("username")
            
            log_info(f"Receiving file '{filename}' ({filesize} bytes) from {sender_name} ({addr[0]})")
            
            # Send ACK
            conn.send(b"ACK")
            
            os.makedirs("received_files", exist_ok=True)
            filepath = os.path.join("received_files", filename)
            
            received_bytes = 0
            with open(filepath, 'wb') as f:
                while received_bytes < filesize:
                    chunk = conn.recv(min(BUFFER_SIZE, filesize - received_bytes))
                    if not chunk:
                        break
                    f.write(chunk)
                    received_bytes += len(chunk)
                    if self.on_file_progress:
                        self.on_file_progress(filename, received_bytes, filesize)
            
            log_info(f"File '{filename}' received successfully.")
            if self.on_file_received:
                self.on_file_received(sender_name, filename)
                
        except Exception as e:
            log_error(f"Error receiving file from {addr[0]}: {e}")
        finally:
            conn.close()

    def discover_devices(self):
        msg = json.dumps({"type": "discovery", "username": self.username, "os": platform.system(), "status": "Online"}).encode('utf-8')
        try:
            self.udp_socket.sendto(msg, ('<broadcast>', UDP_PORT))
            self.udp_socket.sendto(msg, ('127.0.0.1', UDP_PORT)) # ensure localhost receives it
            log_info("Sent discovery broadcast")
        except Exception as e:
            log_error(f"Broadcast failed: {e}")

    def send_message(self, ip, message):
        msg = json.dumps({
            "type": "message",
            "username": self.username,
            "content": message
        }).encode('utf-8')
        try:
            self.udp_socket.sendto(msg, (ip, UDP_PORT))
            log_info(f"Sent message to {ip}")
        except Exception as e:
            log_error(f"Failed to send message to {ip}: {e}")

    def send_file(self, ip, filepath):
        threading.Thread(target=self._send_file_thread, args=(ip, filepath), daemon=True).start()

    def _send_file_thread(self, ip, filepath):
        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip, TCP_PORT))
            s.settimeout(None)
            
            meta = json.dumps({
                "filename": filename,
                "filesize": filesize,
                "username": self.username
            }).encode('utf-8')
            
            s.send(meta)
            
            ack = s.recv(BUFFER_SIZE)
            if ack != b"ACK":
                log_error("Did not receive ACK for file transfer")
                s.close()
                return
                
            log_info(f"Sending file '{filename}' to {ip}")
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    s.send(chunk)
            
            log_info(f"File '{filename}' sent successfully to {ip}")
            s.close()
        except Exception as e:
            log_error(f"Failed to send file to {ip}: {e}")

    def check_connectivity(self, ip):
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, '1', ip]
        try:
            output = subprocess.run(command, capture_output=True, text=True, timeout=5)
            success = output.returncode == 0
            log_info(f"Ping {ip} success: {success}")
            return success, output.stdout
        except Exception as e:
            log_error(f"Ping error for {ip}: {e}")
            return False, str(e)

    def scan_ports(self, ip, ports=[21, 22, 80, 443, 8080]):
        results = {}
        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                is_open = (result == 0)
                results[port] = is_open
                s.close()
            except Exception as e:
                results[port] = False
        log_info(f"Port scan results for {ip}: {results}")
        return results

    def stop(self):
        self.running = False
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except:
                pass
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except:
                pass
