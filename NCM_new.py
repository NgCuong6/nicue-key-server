#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import string
import json
import hashlib
import requests
import threading
from datetime import datetime, timedelta
from PIL import Image
try:
    import UnityPy
except ImportError:
    print("Installing UnityPy...")
    os.system("pip install UnityPy")
    import UnityPy

try:
    import pyperclip
except ImportError:
    print("Installing pyperclip...")
    os.system("pip install pyperclip")
    import pyperclip

# ================= KEY VERIFY & LINK4M ==================
SERVER_URL = "http://127.0.0.1:5000"  # Update to your server URL if different
LINK4M_API_KEY = "66e285b661103a61730450f9"  # API key Link4m
REDIRECT_URL = "https://link4m.com/k1WLJVwB?kktool=true"  # URL Link4m có sẵn để redirect

def create_redirect_link() -> str:
    """Tạo link redirect qua Link4m"""
    return REDIRECT_URL
class LinkStatus:
    PENDING = "pending"      # Chưa vượt link
    COMPLETED = "completed"  # Đã vượt link
    EXPIRED = "expired"      # Link hết hạn

def create_link4m_shortlink(original_url: str) -> str:
    """Tạo link rút gọn Link4m với API chính thức"""
    try:
        api_url = "https://link4m.co/api"
        # Tạo token ngẫu nhiên để xác thực
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # Thêm token vào URL gốc
        url_with_token = f"{original_url}?token={token}"
        
        payload = {
            'api': LINK4M_API_KEY,
            'url': url_with_token,
            'alias': ''
        }
        
        # Gửi request
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl", original_url)
                else:
                    print(f"{Colors.YELLOW}⚠️ Link4m API trả về lỗi: {data.get('message', 'Unknown error')}{Colors.RESET}")
            except ValueError:
                print(f"{Colors.YELLOW}⚠️ Không thể parse JSON response{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️ API request failed with status code: {response.status_code}{Colors.RESET}")
            
        return original_url
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ Lỗi khi tạo link rút gọn: {str(e)}{Colors.RESET}")
        return original_url
    """Tạo link rút gọn Link4m với token xác thực"""
    try:
        api_url = "https://link4m.co/api"
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        url_with_token = f"{original_url}?link4m_token={token}"
        
        payload = {
            'api': LINK4M_API_KEY,
            'url': url_with_token,
            'alias': '',
            'format': 'json'
        }
        
        response = requests.post(api_url, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('shortenedUrl', url_with_token)
        return url_with_token
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ Không tạo được link rút gọn: {e}{Colors.RESET}")
        return url_with_token

def get_key_link():
    """Tạo và hiển thị link lấy key với giao diện đẹp"""
    print(f"\n{Colors.CYAN}╔{'═' * 70}╗{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🔑 HỆ THỐNG QUẢN LÝ KEY NICUE MOD 🔑{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Thời hạn key: {Colors.GREEN}20 phút{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Bảo mật: {Colors.YELLOW}Link4M Verification{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Anti-Abuse: {Colors.RED}Enabled{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.MAGENTA}⚡ ĐANG TẠO LINK BẢO MẬT...{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    
    # Lấy link redirect qua Link4m
    redirect_link = create_redirect_link()
    
    # Tạo link rút gọn với bảo mật
    short_link = create_link4m_shortlink(original_link)
    
    print(f"\n{Colors.GREEN}╔{'═' * 70}╗{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}✅ LINK BẢO MẬT ĐÃ SẴN SÀNG!{Colors.RESET}".center(80) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}🔗 Link Xác Thực:{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.CYAN}{short_link}{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}📋 Hướng Dẫn Lấy Key:{Colors.RESET}".center(80) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}1. Copy link xác thực phía trên{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}2. Vượt link Link4M để nhận key bảo mật{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}3. Key sẽ tự động hiển thị sau khi vượt link{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.RED}⚠️ Lưu ý:{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Key chỉ có hiệu lực trong 20 phút{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Mỗi IP chỉ được lấy 1 key trong 20 phút{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Không reset/bypass để lấy key mới{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.MAGENTA}💬 Liên hệ hỗ trợ: ZALO 0349667922 - YOUTUBE: NiCue Mod{Colors.RESET}".center(80) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╚{'═' * 70}╝{Colors.RESET}")
    
    return short_link

def check_key(key: str) -> bool:
    try:
        resp = requests.get(f"{SERVER_URL}/verify/{key}", timeout=5)
        data = resp.json()
        
        if data.get("code") == "LINK4M_REQUIRED":
            print(f"\n{Colors.YELLOW}⚠️ Vui lòng vượt link Link4M trước khi lấy key!{Colors.RESET}")
            return False
            
        if data.get("status") == "error":
            print(f"\n{Colors.RED}❌ Lỗi: {data.get('message', 'Unknown error')}{Colors.RESET}")
            return False
            
        return data.get("status") == "ok"
    except Exception as e:
        print(f"\n{Colors.RED}❌ Không kết nối được server: {e}{Colors.RESET}")
        return False

def get_image_path(self, texture_name):
    """Lấy đường dẫn ảnh với giao diện đẹp"""
    print(f"\n{Colors.BLUE}╭─{'─' * 50}─╮{Colors.RESET}")
    print(f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎨 CHỌN ẢNH CHO: {texture_name}{Colors.RESET}".ljust(65) + f"{Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}├─{'─' * 50}─┤{Colors.RESET}")
    print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}• Kéo thả ảnh vào đây{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}• Hoặc nhập đường dẫn đầy đủ{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
    
    # Hiển thị ảnh trong thư mục images nếu có
    images = [f for f in os.listdir('images') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    if images:
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}• Hoặc chọn từ thư mục /images/:{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}├─{'─' * 50}─┤{Colors.RESET}")
        
        for i, img_name in enumerate(images, 1):
            if len(img_name) > 35:
                img_name = img_name[:32] + "..."
            print(f"{Colors.BLUE}│{Colors.RESET} {Colors.YELLOW}{i:>2}.{Colors.RESET} {Colors.WHITE}{img_name}{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
    
    print(f"{Colors.BLUE}╰─{'─' * 50}─╯{Colors.RESET}")
    
    while True:
        path = input(f"\n{Colors.YELLOW}👉 Đường dẫn hoặc số thứ tự: {Colors.RESET}").strip().strip('"\'')
        
        # Kiểm tra nếu là số thứ tự
        if path.isdigit() and images:
            try:
                index = int(path) - 1
                if 0 <= index < len(images):
                    selected_path = os.path.join('images', images[index])
                    print(f"{Colors.GREEN}✅ Đã chọn: {images[index]}{Colors.RESET}")
                    return selected_path
                else:
                    print(f"{Colors.RED}❌ Số thứ tự không hợp lệ! Chọn từ 1-{len(images)}{Colors.RESET}")
                    continue
            except ValueError:
                pass
        
        # Kiểm tra đường dẫn file
        if not path:
            print(f"{Colors.RED}❌ Vui lòng chọn ảnh!{Colors.RESET}")
            continue
            
        if not os.path.exists(path):
            print(f"{Colors.RED}❌ File không tồn tại!{Colors.RESET}")
            continue
            
        if not path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            print(f"{Colors.RED}❌ Chỉ hỗ trợ: PNG, JPG, JPEG, BMP{Colors.RESET}")
            continue
            
        print(f"{Colors.GREEN}✅ Đã chọn: {os.path.basename(path)}{Colors.RESET}")
        return path

def optimize_image(self, image_path, target_size):
    """Tối ưu ảnh"""
    try:
        with Image.open(image_path) as img:
            # Convert sang RGBA
            if img.mode != 'RGBA':
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    img = background
                img = img.convert('RGBA')
            
            # Resize nếu kích thước khác
            if img.size != target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            return img
    except Exception as e:
        print(f"{Colors.RED}❌ Lỗi xử lý ảnh: {e}{Colors.RESET}")
        return None

# ================== MÀU SẮC ===================
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

# ================== TOOL MOD ==================
class NiCueModTool:
    def __init__(self):
        # Cấu hình tất cả file với tên mới và texture
        self.file_configs = {
            "optionalab_weapon_068.taWKWMEe462YVhaYmP6~2Fq07NIV8~3D": {
                "name": "File Truyện Tranh & Côn Trùng",
                "textures": [
                    "IceWall_Bunker_New_Rank44_D",
                    "IceWall_Bunker_New_CSRank30_D"
                ],
                "max_name": "optionalab_weapon_068.wK6Wcwor2D8pjjzCkSIAPIldo7c~3D"
            },
            "optionalab_weapon_038.xn3C2MskfGbGot82Dz2fJQ54M4g~3D": {
                "name": "Keo Tanjiro",
                "textures": ["IceWall_Bunker_New_DS_green_D"],
                "max_name": "optionalab_weapon_038.dYO4hfQMcF~2BGYHqQxLGGsRnIGys~3D"
            },
            "optionalab_weapon_058.lFsWlMele5d4X5aw6RBLchSdjgo~3D": {
                "name": "Keo Booya",
                "textures": ["IceWall_Bunker_New_Booyahday24_Team_D"],
                "max_name": "optionalab_weapon_058.hxAcEvqNDnVv0ahYZtQ7rBQhPgc~3D"
            },
            "optionalab_weapon_054.PZEaSpjxrnFlozy~2Bs9hos3qj6xo~3D": {
                "name": "Keo 7 Tuổi",
                "textures": ["IceWall_Bunker_New_Spirit24_D"],
                "max_name": "optionalab_weapon_054.RTLN0jSaLvRttCJ2g8DS8uPx7NQ~3D"
            },
            "optionalab_weapon_060.k18kfeCBi8x8CHn~2B5l9tBrYEcRM~3D": {
                "name": "Keo Hà Mã",
                "textures": ["IceWall_Bunker_New_Hippo_D"],
                "max_name": "optionalab_weapon_060.MmoGsHpdq5URHWzr4AL3F~2F9hBmY~3D"
            }
        }
        
        # Đường dẫn game
        self.game_paths = {
            "TH": "com.dts.freefireth\\com.dts.freefireth\\files\\contentcache\\Optional\\android\\gameassetbundles",
            "MAX": "com.dts.freefiremax\\files\\contentcache\\Optional\\android\\gameassetbundles"
        }
        
        # Quét file có sẵn
        self.available_files = [f for f in self.file_configs if os.path.exists(f)]
        
        # Tạo thư mục images nếu chưa có
        if not os.path.exists('images'):
            os.makedirs('images')

    def print_header(self):
        """In header tool với giao diện đẹp"""
        print(Colors.CYAN + "╔" + "═" * 58 + "╗" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.YELLOW + Colors.BOLD + 
              "🔥 NICUE MOD TOOL - FREE FIRE MODDING 🔥".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.WHITE + 
              "Công cụ mod Free Fire chuyên nghiệp".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "╠" + "═" * 58 + "╣" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.GREEN + Colors.BOLD +
              "👤 Author: Nguyễn Trung Cường".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.BLUE + 
              "📱 Zalo: 0349667922".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.RED + 
              "📺 Youtube: NiCue Mod".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.MAGENTA + 
              "© 2024 NiCue Mod - All Rights Reserved".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "╚" + "═" * 58 + "╝" + Colors.RESET)

    def process_mod(self, asset_file, version):
        """Xử lý mod với giao diện đẹp"""
        config = self.file_configs[asset_file]
        
        print(f"\n{Colors.CYAN}╔{'═' * 50}╗{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🔄 ĐANG XỬ LÝ: {config['name']}{Colors.RESET}".ljust(60) + f"{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}╚{'═' * 50}╝{Colors.RESET}")
        
        try:
            # Load bundle
            print(f"{Colors.YELLOW}⏳ Đang tải asset bundle...{Colors.RESET}")
            bundle = UnityPy.load(asset_file)
            
            # Xử lý từng texture
            for texture_name in config['textures']:
                print(f"\n{Colors.BLUE}📍 Texture: {Colors.BOLD}{texture_name}{Colors.RESET}")
                
                # Lấy ảnh thay thế
                image_path = self.get_image_path(texture_name)
                
                # Tìm và thay thế texture
                texture_found = False
                for obj in bundle.objects:
                    if obj.type.name == "Texture2D":
                        data = obj.read()
                        if data.name == texture_name:
                            print(f"{Colors.YELLOW}⚡ Đang tối ưu ảnh...{Colors.RESET}")
                            
                            # Tối ưu ảnh
                            new_img = self.optimize_image(image_path, (data.m_Width, data.m_Height))
                            
                            # Thay thế
                            data.image = new_img
                            data.save()
                            texture_found = True
                            print(f"{Colors.GREEN}✅ Thay thế {texture_name} thành công!{Colors.RESET}")
                            break
                
                if not texture_found:
                    print(f"{Colors.RED}❌ Không tìm thấy texture: {texture_name}{Colors.RESET}")
                    return False
            
            # Tạo tên file output
            if version == "TH":
                output_name = asset_file
            else:  # MAX
                output_name = config['max_name']
            
            output_file = f"{output_name}.mod"
            
            print(f"\n{Colors.YELLOW}💾 Đang lưu file mod...{Colors.RESET}")
            with open(output_file, "wb") as f:
                f.write(bundle.file.save())
            
            # Hiển thị kết quả thành công
            self.show_success_result(config['name'], output_file, version)
            return True
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ Lỗi trong quá trình mod: {str(e)}{Colors.RESET}")
            return False

    def check_files(self):
        """Kiểm tra file có sẵn"""
        if not self.available_files:
            print("\n" + Colors.RED + "❌ KHÔNG TÌM THẤY FILE NÀO!" + Colors.RESET)
            print(Colors.YELLOW + "📁 Hãy đặt file asset vào cùng thư mục với tool!" + Colors.RESET)
            print(Colors.DIM + "\nDanh sách file cần có:" + Colors.RESET)
            for filename, config in self.file_configs.items():
                print(f"  • {Colors.CYAN}{config['name']}{Colors.RESET}: {Colors.DIM}{filename}{Colors.RESET}")
            input(Colors.WHITE + "\nNhấn Enter để thoát..." + Colors.RESET)
            sys.exit(1)
            
        print(f"\n{Colors.GREEN}✅ Tìm thấy {len(self.available_files)} file có thể mod!{Colors.RESET}")

    def show_file_menu(self):
        """Hiển thị menu chọn file với giao diện đẹp"""
        print("\n" + Colors.BLUE + "╭─" + "─" * 40 + "─╮" + Colors.RESET)
        print(Colors.BLUE + "│" + Colors.BOLD + Colors.YELLOW + 
              "📋 CHỌN FILE MUỐN MOD".center(42) + 
              Colors.RESET + Colors.BLUE + "│" + Colors.RESET)
        print(Colors.BLUE + "├─" + "─" * 40 + "─┤" + Colors.RESET)
        
        for i, filename in enumerate(self.available_files, 1):
            config = self.file_configs[filename]
            texture_count = len(config['textures'])
            
            print(Colors.BLUE + "│" + 
                  f"{Colors.CYAN}{i:>2}.{Colors.RESET} " +
                  f"{Colors.WHITE}{config['name']:<25}{Colors.RESET} " +
                  f"{Colors.DIM}({texture_count} texture){Colors.RESET}".ljust(15) +
                  Colors.BLUE + "│" + Colors.RESET)
        
        print(Colors.BLUE + "│" + 
              f"{Colors.RED}{0:>2}.{Colors.RESET} " +
              f"{Colors.WHITE}{'Thoát':<35}{Colors.RESET}" +
              Colors.BLUE + "│" + Colors.RESET)
        print(Colors.BLUE + "╰─" + "─" * 40 + "─╯" + Colors.RESET)
        
        while True:
            choice = input(f"\n{Colors.YELLOW}👉 Lựa chọn của bạn: {Colors.RESET}").strip()
            
            if choice == "0":
                print(f"{Colors.YELLOW}👋 Cảm ơn bạn đã sử dụng NiCue Mod Tool!{Colors.RESET}")
                sys.exit(0)
                
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.available_files):
                    return self.available_files[choice_num - 1]
                else:
                    print(f"{Colors.RED}❌ Vui lòng chọn từ 0 đến {len(self.available_files)}!{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}❌ Vui lòng nhập số!{Colors.RESET}")

    def choose_version(self):
        """Chọn phiên bản Free Fire"""
        print("\n" + Colors.MAGENTA + "╭─" + "─" * 35 + "─╮" + Colors.RESET)
        print(Colors.MAGENTA + "│" + Colors.BOLD + Colors.YELLOW + 
              "📱 CHỌN PHIÊN BẢN GAME".center(37) + 
              Colors.RESET + Colors.MAGENTA + "│" + Colors.RESET)
        print(Colors.MAGENTA + "├─" + "─" * 35 + "─┤" + Colors.RESET)
        print(Colors.MAGENTA + "│" + 
              f"{Colors.CYAN}1.{Colors.RESET} {Colors.GREEN}Free Fire TH{Colors.RESET}" +
              f"{Colors.DIM} (Tên file gốc){Colors.RESET}".ljust(15) +
              Colors.MAGENTA + "│" + Colors.RESET)
        print(Colors.MAGENTA + "│" + 
              f"{Colors.CYAN}2.{Colors.RESET} {Colors.BLUE}Free Fire MAX{Colors.RESET}" +
              f"{Colors.DIM} (Đổi tên file){Colors.RESET}".ljust(14) +
              Colors.MAGENTA + "│" + Colors.RESET)
        print(Colors.MAGENTA + "╰─" + "─" * 35 + "─╯" + Colors.RESET)
        
        while True:
            choice = input(f"\n{Colors.YELLOW}👉 Chọn phiên bản: {Colors.RESET}").strip()
            if choice == "1":
                print(f"{Colors.GREEN}✅ Đã chọn: Free Fire TH{Colors.RESET}")
                return "TH"
            elif choice == "2":
                print(f"{Colors.BLUE}✅ Đã chọn: Free Fire MAX{Colors.RESET}")
                return "MAX"
            else:
                print(f"{Colors.RED}❌ Vui lòng chọn 1 hoặc 2!{Colors.RESET}")

    def run(self):
        """Chạy tool chính"""
        self.print_header()
        self.check_files()
        
        while True:
            # Chọn file
            selected_file = self.show_file_menu()
            
            # Chọn phiên bản
            version = self.choose_version()
            
            # Xử lý mod
            if self.process_mod(selected_file, version):
                print(f"\n{Colors.BLUE}{'=' * 40}{Colors.RESET}")
                continue_choice = input(f"{Colors.YELLOW}🔄 Bạn có muốn mod file khác không? (y/n): {Colors.RESET}").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    break
            else:
                print(f"{Colors.RED}❌ Mod thất bại!{Colors.RESET}")
                input(f"{Colors.WHITE}Nhấn Enter để thử lại...{Colors.RESET}")

# ================= MAIN ======================
def main():
    print(Colors.CYAN + "🔥 NiCue Mod Tool 🔥" + Colors.RESET)
    print("=================================")
    
    # Menu chính
    while True:
        print(f"\n{Colors.BLUE}╭─{'─' * 35}─╮{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎯 MENU CHÍNH{Colors.RESET}".center(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}├─{'─' * 35}─┤{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}1.{Colors.RESET} {Colors.WHITE}Tạo link lấy key{Colors.RESET}".ljust(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}2.{Colors.RESET} {Colors.WHITE}Nhập key và vào tool{Colors.RESET}".ljust(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.RED}0.{Colors.RESET} {Colors.WHITE}Thoát{Colors.RESET}".ljust(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}╰─{'─' * 35}─╯{Colors.RESET}")
        
        choice = input(f"\n{Colors.YELLOW}👉 Lựa chọn của bạn: {Colors.RESET}").strip()
        
        if choice == "1":
            # Tạo link lấy key
            link = get_key_link()
            print(f"\n{Colors.MAGENTA}📋 Link đã được copy sẵn (nếu hỗ trợ){Colors.RESET}")
            
            # Thử copy vào clipboard nếu có thể
            try:
                import pyperclip
                pyperclip.copy(link)
                print(f"{Colors.GREEN}✅ Link đã copy vào clipboard!{Colors.RESET}")
            except ImportError:
                print(f"{Colors.YELLOW}💡 Cài đặt 'pip install pyperclip' để tự copy link{Colors.RESET}")
            
            input(f"\n{Colors.WHITE}Nhấn Enter để tiếp tục...{Colors.RESET}")
            
        elif choice == "2":
            # Nhập key và vào tool
            print(f"\n{Colors.CYAN}╔{'═' * 40}╗{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🔑 NHẬP KEY{Colors.RESET}".center(50) + f"{Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}╚{'═' * 40}╝{Colors.RESET}")
            
            key = input(f"{Colors.YELLOW}🔑 Nhập key (đã lấy từ link): {Colors.RESET}").strip()

            if not key:
                print(f"{Colors.RED}❌ Vui lòng nhập key!{Colors.RESET}")
                continue
            
            print(f"{Colors.YELLOW}⏳ Đang xác thực key...{Colors.RESET}")
            
            if not check_key(key):
                print(f"\n{Colors.RED}╔{'═' * 45}╗{Colors.RESET}")
                print(f"{Colors.RED}║{Colors.RESET} {Colors.BOLD}{Colors.WHITE}❌ KEY KHÔNG HỢP LỆ!{Colors.RESET}".center(55) + f"{Colors.RED}║{Colors.RESET}")
                print(f"{Colors.RED}╠{'═' * 45}╣{Colors.RESET}")
                print(f"{Colors.RED}║{Colors.RESET} {Colors.WHITE}• Key có thể đã hết hạn{Colors.RESET}".ljust(55) + f"{Colors.RED}║{Colors.RESET}")
                print(f"{Colors.RED}║{Colors.RESET} {Colors.WHITE}• Key không đúng định dạng{Colors.RESET}".ljust(55) + f"{Colors.RED}║{Colors.RESET}")
                print(f"{Colors.RED}║{Colors.RESET} {Colors.WHITE}• Server không hoạt động{Colors.RESET}".ljust(55) + f"{Colors.RED}║{Colors.RESET}")
                print(f"{Colors.RED}╚{'═' * 45}╝{Colors.RESET}")
                
                input(f"\n{Colors.WHITE}Nhấn Enter để thử lại...{Colors.RESET}")
                continue

            print(f"\n{Colors.GREEN}╔{'═' * 35}╗{Colors.RESET}")
            print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}✅ KEY HỢP LỆ!{Colors.RESET}".center(45) + f"{Colors.GREEN}║{Colors.RESET}")
            print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}Đang khởi động tool...{Colors.RESET}".center(45) + f"{Colors.GREEN}║{Colors.RESET}")
            print(f"{Colors.GREEN}╚{'═' * 35}╝{Colors.RESET}")
            
            # Vào tool chính
            try:
                tool = NiCueModTool()
                tool.run()
                break
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}👋 Cảm ơn bạn đã sử dụng NiCue Mod Tool!{Colors.RESET}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}❌ Lỗi không mong muốn: {str(e)}{Colors.RESET}")
                input(f"{Colors.WHITE}Nhấn Enter để quay lại menu...{Colors.RESET}")
                continue
                
        elif choice == "0":
            print(f"\n{Colors.YELLOW}👋 Cảm ơn bạn đã sử dụng NiCue Mod Tool!{Colors.RESET}")
            break
            
        else:
            print(f"{Colors.RED}❌ Lựa chọn không hợp lệ! Vui lòng chọn 0, 1 hoặc 2{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Thoát tool.")