STYLES = """
QMainWindow {
    background-color: #1e1e2e;
}

QWidget {
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QTextEdit {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
    selection-background-color: #585b70;
}

QTextEdit#chat_display {
    background-color: #313244;
    border: 2px solid #45475a;
}

QTextEdit#input_box {
    background-color: #313244;
    border: 2px solid #45475a;
    max-height: 100px;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #b4befe;
}

QPushButton:pressed {
    background-color: #cba6f7;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

#voice_button, #tts_button {
    background-color: #f5c2e7;
}

#voice_button:hover, #tts_button:hover {
    background-color: #f2cdcd;
}

MessageWidget {
    background-color: transparent;
    border-radius: 10px;
    margin: 5px;
    padding: 10px;
}
"""
