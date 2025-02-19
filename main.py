# main.py
import sys
import json
import requests
import pyttsx3
import speech_recognition as sr
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QTextEdit, QPushButton, QHBoxLayout, QScrollArea,
                           QLabel, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFontDatabase, QFont, QPalette, QColor
from styles import STYLES

class MessageWidget(QFrame):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Create header (You/Assistant label)
        header = QLabel("You:" if is_user else "Assistant:")
        header.setStyleSheet(f"color: {'#89b4fa' if is_user else '#f5c2e7'}; font-weight: bold;")
        layout.addWidget(header)
        
        # Create message content
        message = QLabel(text)
        message.setWordWrap(True)
        message.setStyleSheet("color: #cdd6f4; margin-left: 10px;")
        layout.addWidget(message)
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            MessageWidget {{
                background-color: {('#313244' if is_user else '#45475a')};
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }}
        """)

class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setMinimumWidth(400)

class ScrollableChatArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_widget = ChatWidget()
        
        self.setWidget(self.chat_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Style the scroll bar
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background-color: #313244;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #45475a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    def add_message(self, text, is_user=True):
        message_widget = MessageWidget(text, is_user)
        self.chat_widget.layout.addWidget(message_widget)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class VoiceThread(QThread):
    finished = pyqtSignal(str)
    
    def run(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            
        try:
            text = recognizer.recognize_google(audio)
            self.finished.emit(text)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.finished.emit("")

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chat Assistant")
        self.setGeometry(100, 100, 1000, 800)
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Chat area
        self.chat_area = ScrollableChatArea()
        layout.addWidget(self.chat_area)
        
        # Input area container
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(10)
        
        # Input box
        self.input_box = QTextEdit()
        self.input_box.setObjectName("input_box")
        self.input_box.setPlaceholderText("Type your message here...")
        input_layout.addWidget(self.input_box)
        
        # Buttons container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("send_button")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        # Voice input button
        self.voice_button = QPushButton("🎤 Voice")
        self.voice_button.setObjectName("voice_button")
        self.voice_button.clicked.connect(self.start_voice_input)
        button_layout.addWidget(self.voice_button)
        
        # TTS button
        self.tts_button = QPushButton("🔊 TTS: Off")
        self.tts_button.setObjectName("tts_button")
        self.tts_enabled = False
        self.tts_button.clicked.connect(self.toggle_tts)
        button_layout.addWidget(self.tts_button)
        
        input_layout.addWidget(button_container)
        layout.addWidget(input_container)
        
        # Set styles
        self.setStyleSheet(STYLES)
        
        # Initialize voice thread
        self.voice_thread = None
        
        # Add welcome message
        self.chat_area.add_message("Welcome! How can I help you today?", False)

    def send_message(self):
        user_message = self.input_box.toPlainText().strip()
        if not user_message:
            return
            
        # Display user message
        self.chat_area.add_message(user_message, True)
        self.input_box.clear()
        
        # Send request to local LLM (Ollama)
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "deepseek-r1:1.5b",  # Change this to your model name
                    "prompt": user_message
                },
                stream=True  # Stream the response
            )
            
            if response.status_code == 200:
                # Handle streaming response
                llm_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            llm_response += data.get('response', '')
                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error: {e}")
                            continue
                
                if llm_response:
                    self.chat_area.add_message(llm_response, False)
                    
                    # Text-to-speech for assistant's response
                    if self.tts_enabled:
                        self.engine.say(llm_response)
                        self.engine.runAndWait()
                else:
                    self.chat_area.add_message("Error: No valid response", False)
            else:
                self.chat_area.add_message("Error: Could not connect to LLM", False)
                
        except Exception as e:
            self.chat_area.add_message(f"Error: {str(e)}", False)

    def start_voice_input(self):
        self.voice_button.setEnabled(False)
        self.voice_thread = VoiceThread()
        self.voice_thread.finished.connect(self.handle_voice_input)
        self.voice_thread.start()

    def handle_voice_input(self, text):
        self.voice_button.setEnabled(True)
        if text:
            self.input_box.setText(text)
            self.send_message()

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled
        self.tts_button.setText("🔊 TTS: On" if self.tts_enabled else "🔊 TTS: Off")

if __name__ == "__main__":
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
