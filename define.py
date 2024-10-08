from enum import Enum
from PyQt5.QtWidgets import QApplication, QMessageBox
import re, sys, traceback

expireDate = "2024-12-30"
MAX_POSTS = 100
MAX_POSTS_PER_DAY = 20

class Stop(Enum):
    RUN = 1
    NOW = 2
    USER = 3
constStr = "NO REVIEW"
NoThread = False #
NoWrite = False
NoGPT = False

platforms = ["baemin", "coupang"]

def show_error_message(message):
    app = QApplication([])
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.exec_()

        
def filter_non_bmp(text):
    # Regular expression to match non-BMP characters
    non_bmp_pattern = re.compile('[^\U00000000-\U0000FFFF]', flags=re.UNICODE)
    # Filter out non-BMP characters
    return non_bmp_pattern.sub('', text)