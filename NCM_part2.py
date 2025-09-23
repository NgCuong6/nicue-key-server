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

# ================== MAIN ======================
def main():
    print(Colors.CYAN + "🔥 NiCue Mod Tool 🔥" + Colors.RESET)
    print("=================================")
    
    # Menu chính
    while True:
        print(f"\n{Colors.BLUE}╭─{'─' * 35}─╮{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}🎯 MENU CHÍNH{Colors.RESET}".center(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}├─{'─' * 35}─┤{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}1.{Colors.RESET} {Colors.WHITE}Lấy Key Tool{Colors.RESET}".ljust(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.CYAN}2.{Colors.RESET} {Colors.WHITE}Nhập Key & Sử Dụng Tool{Colors.RESET}".ljust(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {Colors.RED}0.{Colors.RESET} {Colors.WHITE}Thoát{Colors.RESET}".ljust(45) + f"{Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}╰─{'─' * 35}─╯{Colors.RESET}")
        
        choice = input(f"\n{Colors.YELLOW}👉 Lựa chọn của bạn: {Colors.RESET}").strip()
        
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