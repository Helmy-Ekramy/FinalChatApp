from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from signalrcore.hub_connection_builder import HubConnectionBuilder
import sys
import json

class ChatWindow(QWidget):
    update_users_signal = pyqtSignal(list)
    update_groups_signal = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helmy Chat ✨")
        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QWidget {background-color: #1e1e1e; color: white; font-size: 14px;}
            QLineEdit {padding: 10px; border-radius: 10px; background: #2e2e2e;}
            QPushButton {background-color: #0078ff; padding: 10px; border-radius: 8px; color: white; font-weight: bold;}
            QPushButton:hover {background-color: #0056b3;}
            QTextEdit {background: #111; padding: 10px; border-radius: 10px;}
            QComboBox {padding: 8px; border-radius: 8px; background: #2e2e2e;}
            QListWidget {background: #2e2e2e; padding: 5px; border-radius: 8px;}
            QTabWidget::pane {border: 1px solid #444; border-radius: 8px;}
            QTabBar::tab {background: #2e2e2e; padding: 8px 20px; margin-right: 2px; border-radius: 5px;}
            QTabBar::tab:selected {background: #0078ff;}
        """)

        layout = QVBoxLayout(self)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username…")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_btn)

        # Tab widget for Private Chat and Groups
        self.tabs = QTabWidget()
        
        # Private Chat Tab
        private_tab = QWidget()
        private_layout = QVBoxLayout(private_tab)
        
        private_layout.addWidget(QLabel("Select user to chat with:"))
        self.users_combo = QComboBox()
        self.users_combo.currentTextChanged.connect(self.on_user_selected)
        private_layout.addWidget(self.users_combo)
        
        self.refresh_users_btn = QPushButton("🔄 Refresh Users")
        self.refresh_users_btn.clicked.connect(self.request_online_users)
        private_layout.addWidget(self.refresh_users_btn)
        
        self.private_chat_area = QTextEdit()
        self.private_chat_area.setReadOnly(True)
        private_layout.addWidget(self.private_chat_area)
        
        private_send_layout = QHBoxLayout()
        self.private_message_input = QLineEdit()
        self.private_message_input.setPlaceholderText("Type a message…")
        self.private_message_input.returnPressed.connect(self.send_private_message)
        private_send_layout.addWidget(self.private_message_input)
        
        self.private_send_btn = QPushButton("Send")
        self.private_send_btn.clicked.connect(self.send_private_message)
        private_send_layout.addWidget(self.private_send_btn)
        private_layout.addLayout(private_send_layout)
        
        self.tabs.addTab(private_tab, "Private Chat")
        
        # Groups Tab
        groups_tab = QWidget()
        groups_layout = QVBoxLayout(groups_tab)
        
        # Create Group Section
        create_group_box = QGroupBox("Create New Group")
        create_group_layout = QVBoxLayout()
        
        group_name_layout = QHBoxLayout()
        group_name_layout.addWidget(QLabel("Group Name:"))
        self.group_name_input = QLineEdit()
        self.group_name_input.setPlaceholderText("Enter group name…")
        group_name_layout.addWidget(self.group_name_input)
        create_group_layout.addLayout(group_name_layout)
        
        create_group_layout.addWidget(QLabel("Select members:"))
        self.members_list = QListWidget()
        self.members_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.members_list.setMaximumHeight(100)
        create_group_layout.addWidget(self.members_list)
        
        self.create_group_btn = QPushButton("Create Group")
        self.create_group_btn.clicked.connect(self.create_group)
        create_group_layout.addWidget(self.create_group_btn)
        
        create_group_box.setLayout(create_group_layout)
        groups_layout.addWidget(create_group_box)
        
        # Group Chat Section
        groups_layout.addWidget(QLabel("Select group to chat:"))
        self.groups_combo = QComboBox()
        self.groups_combo.currentTextChanged.connect(self.on_group_selected)
        groups_layout.addWidget(self.groups_combo)
        
        self.refresh_groups_btn = QPushButton("🔄 Refresh Groups")
        self.refresh_groups_btn.clicked.connect(self.request_groups)
        groups_layout.addWidget(self.refresh_groups_btn)
        
        self.group_chat_area = QTextEdit()
        self.group_chat_area.setReadOnly(True)
        groups_layout.addWidget(self.group_chat_area)
        
        group_send_layout = QHBoxLayout()
        self.group_message_input = QLineEdit()
        self.group_message_input.setPlaceholderText("Type a message…")
        self.group_message_input.returnPressed.connect(self.send_group_message)
        group_send_layout.addWidget(self.group_message_input)
        
        self.group_send_btn = QPushButton("Send")
        self.group_send_btn.clicked.connect(self.send_group_message)
        group_send_layout.addWidget(self.group_send_btn)
        groups_layout.addLayout(group_send_layout)
        
        self.tabs.addTab(groups_tab, "Groups")
        
        layout.addWidget(self.tabs)

        self.connection = None
        self.connected = False
        self.current_username = ""
        self.selected_user = ""
        self.selected_group = ""
        
        # Connect signals
        self.update_users_signal.connect(self.update_users_list)
        self.update_groups_signal.connect(self.update_groups_list)
        
        # Disable UI until connected
        self.set_ui_enabled(False)

    def set_ui_enabled(self, enabled):
        self.tabs.setEnabled(enabled)
        self.refresh_users_btn.setEnabled(enabled)
        self.refresh_groups_btn.setEnabled(enabled)

    def connect_to_server(self):
        username = self.username_input.text().strip()
        if username == "":
            QMessageBox.warning(self, "Error", "Username required!")
            return

        try:
            self.connection = HubConnectionBuilder() \
                .with_url("https://linguistical-vacatable-candelaria.ngrok-free.dev/chatHub") \
                .with_automatic_reconnect({
                    "type": "interval",
                    "intervals": [0, 2000, 5000, 10000]
                }).build()

            self.connection.on("ReceiveMessage", self.receive_private_message)
            self.connection.on("ReceiveGroupMessage", self.receive_group_message)
            self.connection.on("UpdateOnlineUsers", self.handle_users_update)
            self.connection.on("UpdateGroups", self.handle_groups_update)

            self.connection.start()
            import time
            time.sleep(0.8)
            
            self.connection.send("RegisterUser", [username])
            self.connected = True
            self.current_username = username
            self.username_input.setEnabled(False)
            self.connect_btn.setEnabled(False)
            self.set_ui_enabled(True)
            
            self.private_chat_area.append(f"✅ Connected as {username}\n")
            
            # Request initial data
            self.request_online_users()
            self.request_groups()
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")

    def request_online_users(self):
        if self.connection and self.connected:
            try:
                self.connection.send("GetOnlineUsers", [])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to get users: {str(e)}")

    def request_groups(self):
        if self.connection and self.connected:
            try:
                self.connection.send("GetGroups", [])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to get groups: {str(e)}")

    def handle_users_update(self, args):
        users = args[0] if args else []
        self.update_users_signal.emit(users)

    def handle_groups_update(self, args):
        groups = args[0] if args else []
        self.update_groups_signal.emit(groups)

    def update_users_list(self, users):
        current = self.users_combo.currentText()
        self.users_combo.clear()
        self.members_list.clear()
        
        filtered_users = [u for u in users if u != self.current_username]
        self.users_combo.addItems(filtered_users)
        self.members_list.addItems(filtered_users)
        
        if current in filtered_users:
            self.users_combo.setCurrentText(current)

    def update_groups_list(self, groups):
        current = self.groups_combo.currentText()
        self.groups_combo.clear()
        self.groups_combo.addItems(groups)
        
        if current in groups:
            self.groups_combo.setCurrentText(current)

    def on_user_selected(self, username):
        self.selected_user = username
        if username:
            self.private_chat_area.append(f"\n--- Chat with {username} ---\n")

    def on_group_selected(self, group_name):
        self.selected_group = group_name
        if group_name:
            self.group_chat_area.append(f"\n--- Group: {group_name} ---\n")

    def send_private_message(self):
        if not self.connection or not self.connected:
            QMessageBox.warning(self, "Error", "You are not connected!")
            return

        message = self.private_message_input.text().strip()
        to_user = self.users_combo.currentText()

        if message == "" or to_user == "":
            return

        try:
            self.connection.send("SendPrivateMessage", [to_user, self.current_username, message])
            self.private_chat_area.append(f"<b>You → {to_user}:</b> {message}")
            self.private_message_input.clear()
        except Exception as e:
            self.private_chat_area.append(f"❌ Error: {str(e)}")

    def receive_private_message(self, args):
        from_user, msg = args
        self.private_chat_area.append(f"<b>{from_user}:</b> {msg}")

    def create_group(self):
        if not self.connection or not self.connected:
            QMessageBox.warning(self, "Error", "You are not connected!")
            return

        group_name = self.group_name_input.text().strip()
        selected_items = self.members_list.selectedItems()
        
        if not group_name:
            QMessageBox.warning(self, "Error", "Please enter a group name!")
            return
        
        if len(selected_items) < 1:
            QMessageBox.warning(self, "Error", "Please select at least one member!")
            return

        members = [item.text() for item in selected_items]
        members.append(self.current_username)  # Add creator

        try:
            self.connection.send("CreateGroup", [group_name, members])
            self.group_name_input.clear()
            self.members_list.clearSelection()
            QMessageBox.information(self, "Success", f"Group '{group_name}' created!")
            self.request_groups()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create group: {str(e)}")

    def send_group_message(self):
        if not self.connection or not self.connected:
            QMessageBox.warning(self, "Error", "You are not connected!")
            return

        message = self.group_message_input.text().strip()
        group_name = self.groups_combo.currentText()

        if message == "" or group_name == "":
            return

        try:
            self.connection.send("SendGroupMessage", [group_name, self.current_username, message])
            self.group_chat_area.append(f"<b>You:</b> {message}")
            self.group_message_input.clear()
        except Exception as e:
            self.group_chat_area.append(f"❌ Error: {str(e)}")

    def receive_group_message(self, args):
        group_name, from_user, msg = args
        if group_name == self.selected_group:
            self.group_chat_area.append(f"<b>{from_user}:</b> {msg}")

    def closeEvent(self, event):
        if self.connection and self.connected:
            try:
                self.connection.stop()
            except:
                pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # First window
    window1 = ChatWindow()
    window1.show()
    
    # Second window for testing
    window2 = ChatWindow()
    window2.move(window1.x() + window1.width() + 20, window1.y())
    window2.show()
    
    sys.exit(app.exec())