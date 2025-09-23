import requests
import json
import os
from datetime import datetime, timedelta

class NicueKeyManager:
    def __init__(self):
        self.key_file = "nicue_key.json"
        self.server_url = "https://nicue-key-server.onrender.com"
        self.key_data = self.load_saved_key()

    def load_saved_key(self):
        """Đọc key đã lưu từ file"""
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_key(self, key_data):
        """Lưu key vào file"""
        with open(self.key_file, 'w') as f:
            json.dump(key_data, f)

    def check_key(self, key):
        """Kiểm tra key với server"""
        try:
            response = requests.post(
                f"{self.server_url}/verify",
                json={"key": key},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "NicueTool/1.0"
                }
            )
            return response.json()
        except Exception as e:
            print(f"Lỗi kết nối: {str(e)}")
            return None

    def verify_and_save_key(self, key):
        """Xác thực và lưu key"""
        result = self.check_key(key)
        if result and result.get("status") == "ok":
            # Lưu key và thời gian hết hạn
            key_data = {
                "key": key,
                "expires_at": (datetime.now() + timedelta(seconds=result["expires_in"])).isoformat()
            }
            self.save_key(key_data)
            return True
        return False

    def is_key_valid(self):
        """Kiểm tra xem key hiện tại còn hạn không"""
        if not self.key_data:
            return False
        
        expires_at = datetime.fromisoformat(self.key_data["expires_at"])
        if datetime.now() > expires_at:
            return False
            
        # Kiểm tra với server
        result = self.check_key(self.key_data["key"])
        return result and result.get("status") == "ok"

def main():
    key_manager = NicueKeyManager()
    
    # Kiểm tra key đã lưu
    if key_manager.key_data and key_manager.is_key_valid():
        print("Key đã lưu còn hiệu lực!")
        expires_at = datetime.fromisoformat(key_manager.key_data["expires_at"])
        remaining = (expires_at - datetime.now()).total_seconds()
        print(f"Thời gian còn lại: {int(remaining/60)} phút {int(remaining%60)} giây")
        
        # Tiếp tục với chương trình chính
        print("\n=== NICUE TOOL ===")
        print("1. Tính năng 1")
        print("2. Tính năng 2")
        print("3. Thoát")
        
    else:
        # Yêu cầu nhập key mới
        while True:
            key = input("\nNhập key của bạn: ")
            if key_manager.verify_and_save_key(key):
                print("✓ Key hợp lệ! Đã lưu key.")
                main()  # Chạy lại để hiển thị menu
                break
            else:
                print("✗ Key không hợp lệ hoặc đã hết hạn!")
                retry = input("Thử lại? (y/n): ")
                if retry.lower() != 'y':
                    break

if __name__ == "__main__":
    main()