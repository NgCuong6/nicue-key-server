import os
import sys
import time
import threading
from itertools import cycle
import platform

class LoadingAnimation:
    def __init__(self):
        self.spinner = cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
        self.busy = False
        self.spinner_thread = None

    def spinner_task(self, text):
        while self.busy:
            sys.stdout.write(f'\r{next(self.spinner)} {text}')
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b' * (len(text) + 2))

    def __enter__(self):
        if platform.system() != 'Windows':
            self.busy = True
            self.spinner_thread = threading.Thread(target=self.spinner_task)
            self.spinner_thread.start()

    def __exit__(self, exception, value, tb):
        if platform.system() != 'Windows':
            self.busy = False
            if self.spinner_thread:
                self.spinner_thread.join()
        sys.stdout.write('\r')
        sys.stdout.flush()

def animate_text(text, color_code, delay=0.03):
    """Hiển thị text với hiệu ứng gõ chữ"""
    for char in text:
        sys.stdout.write(f'{color_code}{char}\033[0m')
        sys.stdout.flush()
        time.sleep(delay)
    print()

def clear_screen():
    """Xóa màn hình terminal"""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')