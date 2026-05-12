# Multi-Protocol Network Toolkit

A professional, modular, and asynchronous desktop application for local network operations. Built with Python and CustomTkinter, this toolkit provides a centralized dashboard for discovering devices, sending messages, transferring files, and running network diagnostics.

---

## 🌟 Features

*   **🔍 UDP Device Discovery**
    *   Finds other active instances of the application on the local network.
    *   Displays discovered devices in a clean, interactive GUI table.
    *   Automatically identifies Usernames, IP Addresses, Ports, OS, and Status.
*   **💬 Real-Time Messaging**
    *   P2P UDP-based messaging between discovered devices.
    *   Clean chat interface with history.
*   **📁 TCP File Transfer**
    *   Reliable point-to-point file sharing using TCP.
    *   Supports large files with automatic directory generation (`received_files`).
*   **🛠️ Network Diagnostics**
    *   **Ping Tool:** Test ICMP reachability to any IP address.
    *   **Port Scanner:** Scan common ports (21, 22, 80, 443, 8080) on target devices to check their states (OPEN/CLOSED).
*   **📝 System Logs**
    *   Real-time event logging (Discovery, Errors, Messages, File Transfers).
    *   Dedicated UI tab with search/filter capabilities to easily navigate logs.

---

## 📋 Requirements

*   Python 3.8+
*   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern UI Library)

---

## 🚀 Installation & Usage

1.  **Install dependencies:**
    Open your terminal or command prompt and run:
    ```bash
    pip install customtkinter
    ```

2.  **Run the application:**
    Navigate to the project directory and execute the main script:
    ```bash
    python main.py
    ```

3.  **Getting Started:**
    *   Upon launching, enter a **Username** to join the network.
    *   Navigate to the **Discovery** tab and click `Discover Devices` to broadcast your presence and find others.
    *   Use the sidebar to navigate between Messaging, File Transfers, and System Logs.

---

## 🏗️ Architecture

The project is cleanly divided into two main components to prevent UI freezing and ensure thread safety:

*   `main.py`: Handles the graphical user interface (GUI) using CustomTkinter, managing views, user inputs, and table rendering.
*   `network_core.py`: Manages all backend asynchronous networking. It handles UDP sockets for broadcasting and messaging, TCP server/client for file transfers, and threading for port scanning/pinging.

---

## 🛡️ Firewall Configuration

> **Note:** For the UDP Discovery and File Transfer features to work perfectly across different physical computers, please ensure that Python is allowed through your **Windows Defender Firewall** (or any active firewall/antivirus) on both private and public networks.
