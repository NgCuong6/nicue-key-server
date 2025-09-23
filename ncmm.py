#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
from PIL import Image
import UnityPy

# ================= KEY VERIFY ==================
SERVER_URL = "http://127.0.0.1:5000"

def check_key(key: str) -> bool:
    try:
        resp = requests.get(f"{SERVER_URL}/verify/{key}", timeout=5)
        data = resp.json()
        return data.get("status") == "ok"
    except Exception as e:
        print("❌ Không kết nối được server:", e)
        return False

# ================== MÀU SẮC ===================
class Colors:
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"
    WHITE = "\033[97m"; RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"

# ================== TOOL MOD ==================
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PIL import Image
import UnityPy

# Màu sắc cho terminal
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
        
    def print_header(self):
        """In header tool với giao diện đẹp"""
        print(Colors.CYAN + "╔" + "═" * 58 + "╗" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.YELLOW + Colors.BOLD + 
              "🔥 NICUE MOD TOOL - FREE FIRE MODDING 🔥".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.WHITE + 
              "Công cụ mod Free Fire chuyên nghiệp".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "║" + Colors.MAGENTA + 
              "© 2024 NiCue Mod - All Rights Reserved".center(58) + 
              Colors.RESET + Colors.CYAN + "║" + Colors.RESET)
        print(Colors.CYAN + "╚" + "═" * 58 + "╝" + Colors.RESET)
        
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

    def list_images_in_folder(self):
        """Liệt kê ảnh trong thư mục images"""
        img_dir = "images"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            print(f"{Colors.YELLOW}📁 Đã tạo thư mục 'images' để bạn có thể bỏ ảnh vào{Colors.RESET}")
            
        image_files = []
        for file in os.listdir(img_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_files.append(os.path.join(img_dir, file))
        
        return image_files

    def get_image_path(self, texture_name):
        """Lấy đường dẫn ảnh với giao diện đẹp"""
        print(f"\n{Colors.BLUE}╭─{'─' * 50}─╮{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎨 CHỌN ẢNH CHO: {texture_name}{Colors.RESET}".ljust(65) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}├─{'─' * 50}─┤{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}• Kéo thả ảnh vào đây{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}• Hoặc nhập đường dẫn đầy đủ{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
        
        # Hiển thị ảnh trong thư mục images nếu có
        images = self.list_images_in_folder()
        if images:
            print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}• Hoặc chọn từ thư mục /images/:{Colors.RESET}".ljust(60) + f"{Colors.BLUE}│{Colors.RESET}")
            print(f"{Colors.BLUE}├─{'─' * 50}─┤{Colors.RESET}")
            
            for i, img_path in enumerate(images, 1):
                img_name = os.path.basename(img_path)
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
                        selected_path = images[index]
                        print(f"{Colors.GREEN}✅ Đã chọn: {os.path.basename(selected_path)}{Colors.RESET}")
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
                
            if not path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                print(f"{Colors.RED}❌ Chỉ hỗ trợ: PNG, JPG, JPEG, BMP, GIF{Colors.RESET}")
                continue
                
            print(f"{Colors.GREEN}✅ Đã chọn: {os.path.basename(path)}{Colors.RESET}")
            return path

    def optimize_image(self, image_path, target_size):
        """Tối ưu ảnh siêu nhanh"""
        with Image.open(image_path) as img:
            # Convert sang RGBA
            if img.mode != 'RGBA':
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    img = background
                img = img.convert('RGBA')
            
            # Resize siêu nhanh
            if img.size != target_size:
                method = Image.Resampling.NEAREST if img.size[0] < target_size[0] else Image.Resampling.BOX
                img = img.resize(target_size, method)
            
            return img

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
            for i, texture_name in enumerate(config['textures'], 1):
                print(f"\n{Colors.BLUE}📍 Texture {i}/{len(config['textures'])}: {Colors.BOLD}{texture_name}{Colors.RESET}")
                
                # Lấy ảnh thay thế
                image_path = self.get_image_path(texture_name)
                
                # Tìm và thay thế texture
                texture_found = False
                for obj in bundle.objects:
                    if obj.type.name == "Texture2D":
                        data = obj.read()
                        name = getattr(data, "name", None) or getattr(data, "m_Name", None)
                        
                        if name == texture_name:
                            print(f"{Colors.YELLOW}⚡ Đang tối ưu ảnh...{Colors.RESET}")
                            
                            # Tối ưu ảnh
                            orig_size = (data.m_Width, data.m_Height)
                            new_img = self.optimize_image(image_path, orig_size)
                            
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

    def show_success_result(self, item_name, output_file, version):
        """Hiển thị kết quả thành công với giao diện đẹp"""
        print(f"\n{Colors.GREEN}╔{'═' * 60}╗{Colors.RESET}")
        print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎉 MOD HOÀN TẤT THÀNH CÔNG! 🎉{Colors.RESET}".center(70) + f"{Colors.GREEN}║{Colors.RESET}")
        print(f"{Colors.GREEN}╠{'═' * 60}╣{Colors.RESET}")
        print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}📁 Item:{Colors.RESET} {Colors.WHITE}{item_name}{Colors.RESET}".ljust(70) + f"{Colors.GREEN}║{Colors.RESET}")
        print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}📱 Version:{Colors.RESET} {Colors.CYAN}Free Fire {version}{Colors.RESET}".ljust(70) + f"{Colors.GREEN}║{Colors.RESET}")
        print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}💾 File:{Colors.RESET} {Colors.YELLOW}{os.path.basename(output_file)}{Colors.RESET}".ljust(70) + f"{Colors.GREEN}║{Colors.RESET}")
        print(f"{Colors.GREEN}╠{'═' * 60}╣{Colors.RESET}")
        print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}📂 Đường dẫn game:{Colors.RESET}".ljust(70) + f"{Colors.GREEN}║{Colors.RESET}")
        print(f"{Colors.GREEN}║{Colors.RESET} {Colors.CYAN}{self.game_paths[version]}{Colors.RESET}".ljust(70) + f"{Colors.GREEN}║{Colors.RESET}")
        print(f"{Colors.GREEN}╠{'═' * 60}╣{Colors.RESET}")
        print(f"{Colors.GREEN}║{Colors.RESET} {Colors.BOLD}{Colors.MAGENTA}© 2024 NiCue Mod - All Rights Reserved{Colors.RESET}".center(70) + f"{Colors.GREEN}║{Colors.RESET}")
        print(f"{Colors.GREEN}╚{'═' * 60}╝{Colors.RESET}")

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

def main():
    """Main function"""
    try:
        tool = NiCueModTool()
        tool.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Cảm ơn bạn đã sử dụng NiCue Mod Tool!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Lỗi không mong muốn: {str(e)}{Colors.RESET}")
        input(f"{Colors.WHITE}Nhấn Enter để thoát...{Colors.RESET}")

if __name__ == "__main__":
    main()

    # 👉 giữ nguyên tất cả function bạn đã viết: print_header, check_files, show_file_menu, choose_version, list_images_in_folder, get_image_path, optimize_image, process_mod, show_success_result, run

# ================= MAIN ======================
def main():
    print(Colors.CYAN + "🔥 NiCue Mod Tool 🔥" + Colors.RESET)
    print("=================================")
    key = input("🔑 Nhập key free (lấy tại server): ").strip()

    if not check_key(key):
        print(Colors.RED + "❌ Key không hợp lệ hoặc hết hạn!" + Colors.RESET)
        sys.exit(1)

    print(Colors.GREEN + "✅ Key hợp lệ! Vào tool..." + Colors.RESET)
    tool = NiCueModTool()
    tool.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Thoát tool.")
