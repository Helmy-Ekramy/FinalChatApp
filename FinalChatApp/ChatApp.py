from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from signalrcore.hub_connection_builder import HubConnectionBuilder
import sys
import time

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helmy Chat ✨")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QWidget {background-color: #1e1e1e; color: white; font-size: 16px;}
            QLineEdit {padding: 10px; border-radius: 10px; background: #2e2e2e;}
            QPushButton {background-color: #0078ff; padding: 10px; border-radius: 8px; color: white; font-weight: bold;}
            QTextEdit {background: #111; padding: 10px; border-radius: 10px;}
        """)

        layout = QVBoxLayout(self)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username…")
        layout.addWidget(self.username_input)

        self.partner_input = QLineEdit()
        self.partner_input.setPlaceholderText("Person you want to chat with…")
        layout.addWidget(self.partner_input)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_btn)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        send_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message…")
        send_layout.addWidget(self.message_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        send_layout.addWidget(self.send_btn)
        layout.addLayout(send_layout)

        self.connection = None
        self.connected = False

    def connect_to_server(self):
        username = self.username_input.text().strip()
        if username == "":
            QMessageBox.warning(self, "Error", "Username required!")
            return

        self.connection = HubConnectionBuilder() \
            .with_url("http://localhost:5283/chatHub") \
            .build()


        self.connection.on("ReceiveMessage", self.receive_message)

        self.connection.start()
        time.sleep(0.5) 
        self.connection.send("RegisterUser", [username])
        self.connected = True
        self.chat_area.append(f"Connected as {username}\n")

    def send_message(self):
        if not self.connection or not self.connected:
            QMessageBox.warning(self, "Error", "You are not connected!")
            return

        message = self.message_input.text().strip()
        to_user = self.partner_input.text().strip()
        from_user = self.username_input.text().strip()

        if message == "" or to_user == "":
            return

        try:
            self.connection.send("SendPrivateMessage", [to_user, from_user, message])
            self.chat_area.append(f"You: {message} : to {to_user}")
            self.message_input.clear()
        except Exception as e:
            self.chat_area.append(f"Error sending message: {e}")

    def receive_message(self, args):
        from_user, msg = args
        self.chat_area.append(f"{from_user}: {msg}")

app = QApplication(sys.argv)

# أول نافذة
window1 = ChatWindow()
window1.show()

# نسخة ثانية
window2 = ChatWindow()
window2.show()

sys.exit(app.exec())
