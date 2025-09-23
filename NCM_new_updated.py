#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import LoadingAnimation, animate_text, clear_screen
import os
import sys
import time
import random
import string
import json
import hashlib
import requests
import threading
import platform
import base64
import subprocess
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
SERVER_URL = "https://nicue-key-server.onrender.com"  # Your Render.com URL
LINK4M_API_KEY = "66e285b661103a61730450f9"  # API key Link4m
API_BASE_URL = f"{SERVER_URL}"  # Base URL for all API calls

# Danh sách các link shortener
SHORTENERS = {
    "Link4M": {
        "name": "Link4M",
        "api_url": "https://link4m.co/api-shorten/v2",
        "api_key": LINK4M_API_KEY
    },
    "BoostLink": {
        "name": "BoostLink",
        "api_url": "https://boostlink.tk/api/v1/shorten",
        "api_key": "your_boostlink_api_key"
    },
    "ShortLink": {
        "name": "ShortLink",
        "api_url": "https://shortlink.com/api/v1/shorten",
        "api_key": "your_shortlink_api_key"
    }
}

# Link shortener hiện tại
CURRENT_SHORTENER = "Link4M"

def change_shortener():
    """Thay đổi dịch vụ rút gọn link"""
    global CURRENT_SHORTENER
    
    print(f"\n{Colors.BLUE}╭{'═' * 50}╮{Colors.RESET}")
    print(f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🔄 CHỌN DỊCH VỤ RÚT GỌN LINK{Colors.RESET}".center(60) + f"{Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}├{'═' * 50}┤{Colors.RESET}")
    
    # Hiển thị danh sách các dịch vụ
    for i, (key, service) in enumerate(SHORTENERS.items(), 1):
        status = "✅ Đang sử dụng" if key == CURRENT_SHORTENER else ""
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}{i}.{Colors.RESET} {Colors.WHITE}{service['name']}{Colors.RESET} {Colors.GREEN}{status}{Colors.RESET}".ljust(58) + f"{Colors.BLUE}│{Colors.RESET}")
    
    print(f"{Colors.BLUE}│{Colors.RESET} {Colors.RED}0.{Colors.RESET} {Colors.WHITE}Quay lại{Colors.RESET}".ljust(58) + f"{Colors.BLUE}│{Colors.RESET}")
    print(f"{Colors.BLUE}╰{'═' * 50}╯{Colors.RESET}")
    
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}👉 Nhập lựa chọn của bạn: {Colors.RESET}").strip()
            
            if choice == "0":
                return False
                
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(SHORTENERS):
                    new_shortener = list(SHORTENERS.keys())[idx-1]
                    if new_shortener == CURRENT_SHORTENER:
                        print(f"{Colors.YELLOW}⚠️ Bạn đang sử dụng dịch vụ này!{Colors.RESET}")
                    else:
                        CURRENT_SHORTENER = new_shortener
                        print(f"{Colors.GREEN}✅ Đã đổi sang {SHORTENERS[new_shortener]['name']}!{Colors.RESET}")
                    return True
            
            print(f"{Colors.RED}❌ Lựa chọn không hợp lệ!{Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Lỗi: {str(e)}{Colors.RESET}")
            return False

def create_shortlink() -> str:
    """Tạo link rút gọn qua API của dịch vụ hiện tại"""
    try:
        # URL gốc của endpoint generate 
        destination_url = f"{API_BASE_URL}/generate"
        
        # URL encode the destination URL
        from urllib.parse import quote
        encoded_url = quote(destination_url)
        
        # Lấy thông tin shortener hiện tại
        shortener = SHORTENERS[CURRENT_SHORTENER]
        
        # Tạo API request theo định dạng của từng dịch vụ
        if CURRENT_SHORTENER == "Link4M":
            api_url = f"{shortener['api_url']}?api={shortener['api_key']}&url={encoded_url}"
            print(f"{Colors.YELLOW}⏳ Đang tạo link rút gọn qua {shortener['name']}...{Colors.RESET}")
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # In ra response để debug
                print(f"{Colors.YELLOW}📝 API Response: {data}{Colors.RESET}")
                if 'status' in data and data['status'] == 'success':
                    short_url = data.get('shortenedUrl') or data.get('shorturl') or data.get('url')
                    if short_url:
                        print(f"{Colors.GREEN}✅ Tạo link rút gọn thành công!{Colors.RESET}")
                        print(f"{Colors.CYAN}🔗 Link: {short_url}{Colors.RESET}")
                        return short_url
                else:
                    print(f"{Colors.YELLOW}⚠️ API trả về lỗi: {data.get('message', 'Unknown error')}{Colors.RESET}")
                    
        elif CURRENT_SHORTENER == "BoostLink":
            data = {
                "api": shortener['api_key'],
                "url": destination_url
            }
            print(f"{Colors.YELLOW}⏳ Đang tạo link rút gọn qua {shortener['name']}...{Colors.RESET}")
            response = requests.post(shortener['api_url'], json=data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    short_url = data.get('short_url')
                    print(f"{Colors.GREEN}✅ Tạo link rút gọn thành công!{Colors.RESET}")
                    print(f"{Colors.CYAN}🔗 Link: {short_url}{Colors.RESET}")
                    return short_url
                else:
                    print(f"{Colors.YELLOW}⚠️ API trả về lỗi: {data.get('message', 'Unknown error')}{Colors.RESET}")
                    
        elif CURRENT_SHORTENER == "ShortLink":
            headers = {
                "Authorization": f"Bearer {shortener['api_key']}"
            }
            data = {
                "url": destination_url
            }
            print(f"{Colors.YELLOW}⏳ Đang tạo link rút gọn qua {shortener['name']}...{Colors.RESET}")
            response = requests.post(shortener['api_url'], headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    short_url = data.get('short_url')
                    print(f"{Colors.GREEN}✅ Tạo link rút gọn thành công!{Colors.RESET}")
                    print(f"{Colors.CYAN}🔗 Link: {short_url}{Colors.RESET}")
                    return short_url
                else:
                    print(f"{Colors.YELLOW}⚠️ API trả về lỗi: {data.get('message', 'Unknown error')}{Colors.RESET}")
        
        # Nếu có lỗi hoặc dịch vụ không hỗ trợ, trả về URL gốc
        print(f"{Colors.YELLOW}⚠️ Không thể tạo link rút gọn, sử dụng URL gốc{Colors.RESET}")
        print(f"{Colors.CYAN}🔗 Link gốc: {destination_url}{Colors.RESET}")
        return destination_url
        
    except Exception as e:
        print(f"{Colors.RED}❌ Lỗi khi gọi API: {str(e)}{Colors.RESET}")
        return destination_url
    try:
        # URL gốc của endpoint generate
        destination_url = f"{API_BASE_URL}/generate"
        
        # URL encode the destination URL
        from urllib.parse import quote
        encoded_url = quote(destination_url)
        
        # URL API Link4M
        api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API_KEY}&url={encoded_url}"
        
        # Gọi API Link4m
        print(f"{Colors.YELLOW}⏳ Đang tạo link rút gọn...{Colors.RESET}")
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'success' and data.get('shortenedUrl'):
                    short_url = data.get('shortenedUrl')
                    print(f"{Colors.GREEN}✅ Tạo link rút gọn thành công!{Colors.RESET}")
                    print(f"{Colors.CYAN}🔗 Link: {short_url}{Colors.RESET}")
                    return short_url
                else:
                    error_msg = data.get('message', 'Unknown error')
                    print(f"{Colors.YELLOW}⚠️ API trả về lỗi: {error_msg}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️ Lỗi khi xử lý response: {str(e)}{Colors.RESET}")
                print(f"{Colors.YELLOW}📝 Response: {response.text}{Colors.RESET}")
        
        print(f"{Colors.YELLOW}⚠️ Không thể tạo link rút gọn, sử dụng URL gốc{Colors.RESET}")
        print(f"{Colors.CYAN}🔗 Link gốc: {destination_url}{Colors.RESET}")
        return destination_url
        
    except Exception as e:
        print(f"{Colors.RED}❌ Lỗi khi gọi API: {str(e)}{Colors.RESET}")
        return destination_url

def get_key_link():
    """Tạo và hiển thị link lấy key với giao diện đẹp"""
    print(f"\n{Colors.CYAN}╔{'═' * 70}╗{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🔑 NICUE MOD - HỆ THỐNG KEY 🔑{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Show key information
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}⏳ Thời hạn key: {Colors.GREEN}20 phút{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}💰 Giá key: {Colors.YELLOW}FREE{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}🔒 Bảo mật: {Colors.RED}Link4M Verification{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}🛡️ Chống: {Colors.RED}Reset/Bypass/Crack{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Show tool information
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🛠️ THÔNG TIN TOOL{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Tên: NICUE MOD TOOL{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Phiên bản: 2.0{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Tác giả: Nguyễn Trung Cường{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Bản quyền © 2025 NiCue Mod{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")

    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎮 TÍNH NĂNG{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Mod keo Free Fire MAX & TH{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Hỗ trợ nhiều loại keo khác nhau{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Tự động tối ưu chất lượng ảnh{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}⚡ ĐANG TẠO LINK BẢO MẬT...{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    
    # Tạo link rút gọn với dịch vụ hiện tại
    short_link = create_shortlink()
    
    print(f"\n{Colors.GREEN}╔{'═' * 70}╗{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}✅ LINK BẢO MẬT ĐÃ SẴN SÀNG!{Colors.RESET}".center(80) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}🔗 Link Lấy Key:{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.CYAN}{short_link}{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Instructions
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}📋 HƯỚNG DẪN:{Colors.RESET}".center(80) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}1. Copy link lấy key ở trên{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}2. Vượt link Link4M để lấy key{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}3. Key sẽ hiện sau khi vượt link thành công{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Warnings
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.RED}⚠️ LƯU Ý QUAN TRỌNG:{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Key chỉ có hiệu lực trong 20 phút{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Mỗi IP chỉ được lấy 1 key trong 20 phút{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Không reset/bypass để lấy key mới{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Quá thời hạn key sẽ tự động hết hiệu lực{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Contact info
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.MAGENTA}💬 LIÊN HỆ HỖ TRỢ:{Colors.RESET}".center(80) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Zalo: 0349667922{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Youtube: NiCue Mod{Colors.RESET}".ljust(79) + f"{Colors.GREEN}║{Colors.RESET}")
    print(f"{Colors.GREEN}╚{'═' * 70}╝{Colors.RESET}")
    
    # Try to copy link to clipboard
    try:
        pyperclip.copy(short_link)
        print(f"\n{Colors.GREEN}✅ Đã copy link vào clipboard!{Colors.RESET}")
    except:
        print(f"\n{Colors.YELLOW}💡 Tip: Cài pyperclip để tự động copy link{Colors.RESET}")
    
    return short_link
    
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.GREEN}✅ LINK LẤY KEY ĐÃ SẴN SÀNG!{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}🔗 Link Lấy Key:{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.CYAN}{redirect_url}{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Instructions
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}📋 HƯỚNG DẪN:{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}1. Copy link lấy key ở trên{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}2. Mở link và vượt Link4M để lấy key{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}3. Key sẽ hiện sau khi vượt link thành công{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Warnings
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.RED}⚠️ LƯU Ý:{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Key chỉ có hiệu lực trong 12 giờ{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Không reset/bypass để lấy key mới{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Tool tự động kiểm tra key hợp lệ{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * 70}╣{Colors.RESET}")
    
    # Contact info
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.MAGENTA}💬 LIÊN HỆ HỖ TRỢ:{Colors.RESET}".center(80) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Zalo: 0349667922{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Youtube: NiCue Mod{Colors.RESET}".ljust(79) + f"{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╚{'═' * 70}╝{Colors.RESET}")
    
    # Try to copy link to clipboard
    try:
        pyperclip.copy(redirect_url)
        print(f"\n{Colors.GREEN}✅ Đã copy link vào clipboard!{Colors.RESET}")
    except:
        print(f"\n{Colors.YELLOW}💡 Tip: Cài pyperclip để tự động copy link{Colors.RESET}")
    
    return redirect_url

def check_key(key: str) -> bool:
    """Kiểm tra key có hợp lệ không"""
    try:
        # First verify locally
        if not key or len(key) < 20:  # Updated key length check
            print(f"\n{Colors.RED}❌ Key không hợp lệ!{Colors.RESET}")
            return False

        # Get hardware ID
        import uuid
        hw_id = str(uuid.getnode())
            
        # Verify with server
        headers = {
            'Content-Type': 'application/json',
            'X-Hardware-ID': hw_id
        }
        
        verify_url = f"{API_BASE_URL}/verify"
        response = requests.post(
            verify_url, 
            json={'key': key},
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            error_data = response.json()
            print(f"\n{Colors.RED}❌ {error_data.get('message', 'Key không hợp lệ!')}{Colors.RESET}")
            return False
            
        data = response.json()
        if data.get('status') == 'ok':
            remaining = data.get('expires_in', 0)
            remaining_minutes = int(remaining / 60)
            print(f"\n{Colors.GREEN}✅ Key hợp lệ!{Colors.RESET}")
            print(f"{Colors.YELLOW}⏳ Thời gian còn lại: {remaining_minutes} phút{Colors.RESET}")
            
            # Store tool config if provided
            tool_config = data.get('tool_config', {})
            if tool_config:
                print(f"\n{Colors.CYAN}🔄 Đang cập nhật cấu hình tool...{Colors.RESET}")
                # You can save tool_config here for later use
                
            return True
        
        print(f"\n{Colors.RED}❌ Key không hợp lệ hoặc đã hết hạn!{Colors.RESET}")
        return False
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Lỗi khi kiểm tra key: {str(e)}{Colors.RESET}")
        return False
            
        # Then verify with server
        resp = requests.get(f"{SERVER_URL}/verify/{key}", timeout=5)
        data = resp.json()
        
        if data.get("status") == "error":
            error_msg = data.get('message', 'Unknown error')
            print(f"\n{Colors.RED}╔{'═' * 45}╗{Colors.RESET}")
            print(f"{Colors.RED}║{Colors.RESET} {Colors.BOLD}{Colors.WHITE}❌ LỖI XÁC THỰC KEY!{Colors.RESET}".center(55) + f"{Colors.RED}║{Colors.RESET}")
            print(f"{Colors.RED}╠{'═' * 45}╣{Colors.RESET}")
            print(f"{Colors.RED}║{Colors.RESET} {Colors.WHITE}{error_msg}{Colors.RESET}".ljust(55) + f"{Colors.RED}║{Colors.RESET}")
            
            if "expired" in error_msg.lower():
                print(f"{Colors.RED}║{Colors.RESET} {Colors.WHITE}Vui lòng lấy key mới để tiếp tục{Colors.RESET}".ljust(55) + f"{Colors.RED}║{Colors.RESET}")
            elif "not found" in error_msg.lower():
                print(f"{Colors.RED}║{Colors.RESET} {Colors.WHITE}Key không tồn tại hoặc chưa vượt link{Colors.RESET}".ljust(55) + f"{Colors.RED}║{Colors.RESET}")
            
            print(f"{Colors.RED}╚{'═' * 45}╝{Colors.RESET}")
            return False
            
        if data.get("status") == "ok":
            expires_in = data.get("expires_in", 0)
            print(f"\n{Colors.GREEN}╔{'═' * 45}╗{Colors.RESET}")
            print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}✅ XÁC THỰC THÀNH CÔNG!{Colors.RESET}".center(55) + f"{Colors.GREEN}║{Colors.RESET}")
            print(f"{Colors.GREEN}╠{'═' * 45}╣{Colors.RESET}")
            print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• Key còn hiệu lực: {expires_in} phút{Colors.RESET}".ljust(55) + f"{Colors.GREEN}║{Colors.RESET}")
            print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}• IP của bạn đã được ghi nhận{Colors.RESET}".ljust(55) + f"{Colors.GREEN}║{Colors.RESET}")
            print(f"{Colors.GREEN}╚{'═' * 45}╝{Colors.RESET}")
            return True
            
        return False
    except Exception as e:
        print(f"\n{Colors.RED}❌ Không kết nối được server: {e}{Colors.RESET}")
        return False

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
        print(Colors.CYAN + "╚" + "═" * 58 + "╝" + Colors.RESET)

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
                print(f"{Colors.BLUE}│{Colors.RESET} {Colors.WHITE}{i}. {img_name}{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
    
        print(f"{Colors.BLUE}╰─{'─' * 50}─╯{Colors.RESET}")
        
        while True:
            path = input(f"\n{Colors.YELLOW}👉 Đường dẫn hoặc số thứ tự: {Colors.RESET}").strip().strip('"\'')
            
            # Kiểm tra nếu là số thứ tự
            if path.isdigit() and images:
                idx = int(path)
                if 1 <= idx <= len(images):
                    path = os.path.join('images', images[idx-1])
                else:
                    print(f"{Colors.RED}❌ Số thứ tự không hợp lệ!{Colors.RESET}")
                    continue
            
            # Kiểm tra đường dẫn file
            if not path:
                print(f"{Colors.RED}❌ Vui lòng nhập đường dẫn ảnh!{Colors.RESET}")
                continue
                
            if not os.path.exists(path):
                print(f"{Colors.RED}❌ Không tìm thấy file: {path}{Colors.RESET}")
                continue
                
            if not path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                print(f"{Colors.RED}❌ File không phải là ảnh!{Colors.RESET}")
                continue
                
            print(f"{Colors.GREEN}✅ Đã chọn: {os.path.basename(path)}{Colors.RESET}")
            return path

    def optimize_image(self, image_path, target_size):
        """Tối ưu ảnh"""
        try:
            with Image.open(image_path) as img:
                # Tối ưu kích thước ảnh
                img.thumbnail(target_size)
                return img
        except Exception as e:
            print(f"{Colors.RED}❌ Lỗi xử lý ảnh: {e}{Colors.RESET}")
            return None

    def process_mod(self, asset_file, version):
        """Xử lý mod file asset"""
        try:
            print(f"\n{Colors.CYAN}╔{'═' * 50}╗{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}⚙️ ĐANG XỬ LÝ MOD...{Colors.RESET}".center(60) + f"{Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}╠{'═' * 50}╣{Colors.RESET}")
            
            config = self.file_configs[asset_file]
            
            # Load file asset
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Đang đọc file asset...{Colors.RESET}".ljust(59) + f"{Colors.CYAN}║{Colors.RESET}")
            bundle = UnityPy.load(asset_file)
            
            # Xử lý từng texture
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Đang xử lý textures...{Colors.RESET}".ljust(59) + f"{Colors.CYAN}║{Colors.RESET}")
            
            for obj in bundle.objects:
                if obj.type.name == "Texture2D":
                    data = obj.read()
                    
                    # Kiểm tra nếu texture cần mod
                    if data.name in config['textures']:
                        print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}  - Xử lý {data.name}...{Colors.RESET}".ljust(59) + f"{Colors.CYAN}║{Colors.RESET}")
                        
                        # Lấy đường dẫn ảnh mới
                        img_path = self.get_image_path(data.name)
                        
                        # Tối ưu ảnh
                        new_img = self.optimize_image(img_path, (data.width, data.height))
                        if new_img is None:
                            continue
                            
                        # Cập nhật texture
                        data.image = new_img
                        data.save()
            
            # Lưu file đã mod
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}• Đang lưu file...{Colors.RESET}".ljust(59) + f"{Colors.CYAN}║{Colors.RESET}")
            
            # Tạo đường dẫn game
            game_path = os.path.join(os.getenv('EXTERNAL_STORAGE', ''), 'Android/data', self.game_paths[version])
            
            if not os.path.exists(game_path):
                os.makedirs(game_path)
                
            # Lưu file với tên mới
            output_path = os.path.join(game_path, config['max_name'])
            with open(output_path, 'wb') as f:
                f.write(bundle.file.save())
            
            print(f"{Colors.CYAN}╠{'═' * 50}╣{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.GREEN}✅ MOD THÀNH CÔNG!{Colors.RESET}".center(60) + f"{Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}╚{'═' * 50}╝{Colors.RESET}")
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Lỗi: {str(e)}{Colors.RESET}")
            return False

    def check_files(self):
        """Kiểm tra các file asset có sẵn"""
        if not self.available_files:
            print(f"\n{Colors.RED}❌ KHÔNG TÌM THẤY FILE ASSET!{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Vui lòng copy các file asset vào thư mục tool{Colors.RESET}")
            return False
        return True

    def show_file_menu(self):
        """Hiển thị menu chọn file để mod"""
        while True:
            print(f"\n{Colors.BLUE}╭─{'─' * 50}─╮{Colors.RESET}")
            print(f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}📂 CHỌN FILE MUỐN MOD{Colors.RESET}".center(65) + f"{Colors.BLUE}│{Colors.RESET}")
            print(f"{Colors.BLUE}├─{'─' * 50}─┤{Colors.RESET}")
            
            # Hiển thị danh sách file
            for i, file in enumerate(self.available_files, 1):
                config = self.file_configs[file]
                print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}{i}.{Colors.RESET} {Colors.WHITE}{config['name']}{Colors.RESET}".ljust(65) + f"{Colors.BLUE}│{Colors.RESET}")
            
            print(f"{Colors.BLUE}│{Colors.RESET} {Colors.RED}0.{Colors.RESET} {Colors.WHITE}Quay lại{Colors.RESET}".ljust(65) + f"{Colors.BLUE}│{Colors.RESET}")
            print(f"{Colors.BLUE}╰─{'─' * 50}─╯{Colors.RESET}")
            
            choice = input(f"\n{Colors.YELLOW}👉 Lựa chọn của bạn: {Colors.RESET}")
            
            if choice == "0":
                return None
                
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(self.available_files):
                    return self.available_files[idx-1]
            
            print(f"{Colors.RED}❌ Lựa chọn không hợp lệ!{Colors.RESET}")

    def choose_version(self):
        """Chọn phiên bản game để mod"""
        while True:
            print(f"\n{Colors.MAGENTA}╭─{'─' * 40}─╮{Colors.RESET}")
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎮 CHỌN PHIÊN BẢN GAME{Colors.RESET}".center(55) + f"{Colors.MAGENTA}│{Colors.RESET}")
            print(f"{Colors.MAGENTA}├─{'─' * 40}─┤{Colors.RESET}")
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.CYAN}1.{Colors.RESET} {Colors.WHITE}Free Fire MAX{Colors.RESET}".ljust(55) + f"{Colors.MAGENTA}│{Colors.RESET}")
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.CYAN}2.{Colors.RESET} {Colors.WHITE}Free Fire Thailand{Colors.RESET}".ljust(55) + f"{Colors.MAGENTA}│{Colors.RESET}")
            print(f"{Colors.MAGENTA}│{Colors.RESET} {Colors.RED}0.{Colors.RESET} {Colors.WHITE}Quay lại{Colors.RESET}".ljust(55) + f"{Colors.MAGENTA}│{Colors.RESET}")
            print(f"{Colors.MAGENTA}╰─{'─' * 40}─╯{Colors.RESET}")
            
            choice = input(f"\n{Colors.YELLOW}👉 Lựa chọn của bạn: {Colors.RESET}")
            
            if choice == "1":
                return "MAX"
            elif choice == "2":
                return "TH"
            elif choice == "0":
                return None
            else:
                print(f"{Colors.RED}❌ Lựa chọn không hợp lệ!{Colors.RESET}")

    def run(self):
        """Chạy tool mod"""
        self.print_header()
        
        if not self.check_files():
            return
            
        while True:
            # Chọn file để mod
            asset_file = self.show_file_menu()
            if asset_file is None:
                break
                
            # Chọn phiên bản game
            version = self.choose_version()
            if version is None:
                continue
                
            # Xử lý mod
            if self.process_mod(asset_file, version):
                input(f"\n{Colors.WHITE}Nhấn Enter để tiếp tục...{Colors.RESET}")

# ================== MAIN ======================
def main():
    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}🔥 NICUE MOD TOOL - FREE FIRE MODDING TOOL 🔥{Colors.RESET}".center(70))
    print(f"{Colors.WHITE}Version 2.0 - Developed by Nguyễn Trung Cường{Colors.RESET}".center(70))
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")
    
    # Kiểm tra kết nối server
    try:
        requests.get(f"{API_BASE_URL}/", timeout=5)
        print(f"{Colors.GREEN}✅ Đã kết nối tới server thành công!{Colors.RESET}")
    except:
        print(f"{Colors.RED}❌ Không thể kết nối tới server!{Colors.RESET}")
        input("Nhấn Enter để thoát...")
        return
    
    # Menu chính
    while True:
        print(f"\n{Colors.BLUE}╭{'═' * 50}╮{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎯 MENU CHÍNH{Colors.RESET}".center(60) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}├{'═' * 50}┤{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}1.{Colors.RESET} {Colors.WHITE}Lấy Key Tool (Thời hạn 20 phút){Colors.RESET}".ljust(58) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}2.{Colors.RESET} {Colors.WHITE}Nhập Key & Sử Dụng Tool{Colors.RESET}".ljust(58) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.RED}0.{Colors.RESET} {Colors.WHITE}Thoát Tool{Colors.RESET}".ljust(58) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}╰{'═' * 50}╯{Colors.RESET}")
        
        choice = input(f"\n{Colors.YELLOW}👉 Nhập lựa chọn của bạn: {Colors.RESET}").strip()
        
        if choice == "1":
            # Lấy key mới
            print(f"\n{Colors.CYAN}⏳ Đang tạo link lấy key...{Colors.RESET}")
            link = get_key_link()
            input(f"\n{Colors.GREEN}✅ Nhấn Enter để tiếp tục...{Colors.RESET}")
            
        elif choice == "2":
            # Nhập và verify key
            print(f"\n{Colors.YELLOW}🔑 Vui lòng nhập key để sử dụng tool:{Colors.RESET}")
            key = input(f"{Colors.CYAN}👉 Nhập key: {Colors.RESET}").strip()
            
            if check_key(key):
                tool = NiCueModTool()
                tool.run()
            else:
                input(f"\n{Colors.RED}❌ Nhấn Enter để thử lại...{Colors.RESET}")
                
        elif choice == "0":
            print(f"\n{Colors.GREEN}👋 Cảm ơn bạn đã sử dụng tool!{Colors.RESET}")
            break
            
        else:
            print(f"\n{Colors.RED}❌ Lựa chọn không hợp lệ!{Colors.RESET}")
        
        if choice == "1":
            # Tạo và hiển thị link lấy key
            get_key_link()
            input(f"\n{Colors.WHITE}Nhấn Enter để tiếp tục...{Colors.RESET}")
            
        elif choice == "2":
            # Nhập key và vào tool
            print(f"\n{Colors.CYAN}╔{'═' * 40}╗{Colors.RESET}")
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🔑 NHẬP KEY TOOL{Colors.RESET}".center(50) + f"{Colors.CYAN}║{Colors.RESET}")
            print(f"{Colors.CYAN}╚{'═' * 40}╝{Colors.RESET}")
            
            key = input(f"{Colors.YELLOW}🔑 Nhập key hoặc link đã vượt: {Colors.RESET}").strip()

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
                print(f"{Colors.RED}║{Colors.RESET} {Colors.WHITE}• Bạn chưa vượt link để lấy key{Colors.RESET}".ljust(55) + f"{Colors.RED}║{Colors.RESET}")
                print(f"{Colors.RED}╚{'═' * 45}╝{Colors.RESET}")
                
                input(f"\n{Colors.WHITE}Nhấn Enter để thử lại...{Colors.RESET}")
                continue

            print(f"\n{Colors.GREEN}╔{'═' * 35}╗{Colors.RESET}")
            print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}✅ XÁC THỰC THÀNH CÔNG!{Colors.RESET}".center(45) + f"{Colors.GREEN}║{Colors.RESET}")
            print(f"{Colors.GREEN}║{Colors.RESET} {Colors.WHITE}Đang khởi động tool...{Colors.RESET}".center(45) + f"{Colors.GREEN}║{Colors.RESET}")
            print(f"{Colors.GREEN}╚{'═' * 35}╝{Colors.RESET}")
            
            # Khởi động tool chính
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