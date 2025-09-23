from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
import jwt
import hashlib
import uuid
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
CORS(app)

# Cấu hình bảo mật
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
MONGO_URI = os.environ.get('MONGODB_URI', 'your-mongodb-uri')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-jwt-secret')

# Kết nối MongoDB
client = MongoClient(MONGO_URI)
db = client.keydb
keys_collection = db.keys
blacklist_collection = db.blacklist

# Rate limiting để chống DDoS
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Middleware bảo mật
def security_check(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr
        
        # Kiểm tra IP có trong blacklist
        if blacklist_collection.find_one({"ip": ip}):
            return jsonify({"status": "error", "message": "IP đã bị chặn"}), 403
        
        # Kiểm tra User-Agent
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or 'python-requests' in user_agent.lower():
            blacklist_collection.insert_one({"ip": ip, "reason": "Invalid User-Agent"})
            return jsonify({"status": "error", "message": "Access denied"}), 403
            
        return f(*args, **kwargs)
    return decorated

# Trang chủ
@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>NiCue Mod Key System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #1a1a1a;
                color: #fff;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: #2d2d2d;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }
            h1 {
                color: #00ff00;
                text-align: center;
                margin-bottom: 30px;
            }
            .info {
                background: #3d3d3d;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
            }
            .warning {
                color: #ff3333;
                font-weight: bold;
            }
            .success {
                color: #00ff00;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 NiCue Mod Key System</h1>
            <div class="info">
                <h3>⚡ Trạng thái: <span class="success">Hoạt động</span></h3>
                <p>• Server key đang hoạt động bình thường</p>
                <p>• Thời hạn key: 20 phút</p>
                <p>• Chế độ bảo mật: Đang bật</p>
            </div>
            <div class="info warning">
                <h3>⚠️ Lưu ý:</h3>
                <p>• Vui lòng sử dụng tool chính thức để lấy key</p>
                <p>• Không chia sẻ hoặc bán lại key</p>
                <p>• Mỗi key chỉ sử dụng được trên 1 máy</p>
            </div>
            <div class="info">
                <h3>📞 Liên hệ hỗ trợ:</h3>
                <p>• Zalo: 0349667922</p>
                <p>• Youtube: NiCue Mod</p>
            </div>
        </div>
    </body>
    </html>
    """

# Trang hiển thị key
@app.route('/key/')
def show_key():
    key = request.args.get('key')
    if not key:
        return "Key không hợp lệ!", 400
        
    return f"""
    <html>
    <head>
        <title>Key NiCue Mod</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #1a1a1a;
                color: #fff;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: #2d2d2d;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }}
            h1 {{
                color: #00ff00;
                text-align: center;
                margin-bottom: 30px;
            }}
            .key-box {{
                background: #3d3d3d;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }}
            .key {{
                font-size: 18px;
                color: #00ff00;
                word-break: break-all;
                font-family: monospace;
            }}
            .timer {{
                font-size: 24px;
                color: #ff3333;
                margin: 20px 0;
            }}
            .info {{
                background: #3d3d3d;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
            }}
        </style>
        <script>
            function startTimer(duration, display) {{
                var timer = duration, minutes, seconds;
                setInterval(function () {{
                    minutes = parseInt(timer / 60, 10);
                    seconds = parseInt(timer % 60, 10);

                    minutes = minutes < 10 ? "0" + minutes : minutes;
                    seconds = seconds < 10 ? "0" + seconds : seconds;

                    display.textContent = minutes + ":" + seconds;

                    if (--timer < 0) {{
                        display.textContent = "HẾT HẠN!";
                    }}
                }}, 1000);
            }}

            window.onload = function () {{
                var twentyMinutes = 60 * 20,
                    display = document.querySelector('#time');
                startTimer(twentyMinutes, display);
            }};
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🔑 Key NiCue Mod</h1>
            <div class="key-box">
                <h3>Key của bạn:</h3>
                <p class="key">{key}</p>
            </div>
            <div class="info">
                <h3>⏰ Thời gian còn lại:</h3>
                <p class="timer"><span id="time">20:00</span></p>
            </div>
            <div class="info">
                <h3>📋 Hướng dẫn:</h3>
                <p>1. Copy key ở trên</p>
                <p>2. Mở tool NiCue Mod</p>
                <p>3. Chọn "Nhập Key & Sử Dụng Tool"</p>
                <p>4. Dán key vào và nhấn Enter</p>
            </div>
            <div class="info">
                <h3>⚠️ Lưu ý:</h3>
                <p>• Key chỉ có hiệu lực trong 20 phút</p>
                <p>• Key chỉ sử dụng được trên 1 máy</p>
                <p>• Không chia sẻ key cho người khác</p>
            </div>
        </div>
    </body>
    </html>
    """

# Tạo key mới
@app.route('/generate', methods=['POST'])
@limiter.limit("3/minute")
@security_check
def generate_key():
    try:
        # Kiểm tra Link4m token
        token = request.args.get('token')
        if not token:
            return jsonify({
                "status": "error",
                "code": "LINK4M_REQUIRED",
                "message": "Vui lòng vượt link để lấy key"
            }), 400
            
        # Tạo key mới với JWT
        ip = request.remote_addr
        hardware_id = request.headers.get('X-Hardware-ID')
        
        key_data = {
            "key_id": str(uuid.uuid4()),
            "ip": ip,
            "hardware_id": hardware_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=20)
        }
        
        # Mã hóa key
        encoded_key = jwt.encode(key_data, JWT_SECRET, algorithm='HS256')
        
        # Lưu vào database
        key_data['key'] = encoded_key
        keys_collection.insert_one(key_data)
        
        # Trả về key với giao diện đẹp
        return jsonify({
            "status": "success",
            "key": encoded_key,
            "expires_in": "20 minutes",
            "message": "Key đã được tạo thành công!"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Xác thực key
@app.route('/verify', methods=['POST'])
@limiter.limit("10/minute")
@security_check
def verify_key():
    try:
        data = request.get_json()
        key = data.get('key')
        
        if not key:
            return jsonify({
                "status": "error",
                "message": "Không tìm thấy key"
            }), 400
            
        # Giải mã và xác thực JWT
        try:
            key_data = jwt.decode(key, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({
                "status": "error",
                "message": "Key đã hết hạn"
            }), 400
        except jwt.InvalidTokenError:
            return jsonify({
                "status": "error",
                "message": "Key không hợp lệ"
            }), 400
            
        # Kiểm tra trong database
        stored_key = keys_collection.find_one({"key_id": key_data['key_id']})
        if not stored_key:
            return jsonify({
                "status": "error",
                "message": "Key không tồn tại"
            }), 400
            
        # Kiểm tra IP
        current_ip = request.remote_addr
        if stored_key['ip'] != current_ip:
            blacklist_collection.insert_one({
                "ip": current_ip,
                "reason": "IP mismatch attempt",
                "key_id": key_data['key_id']
            })
            return jsonify({
                "status": "error",
                "message": "Key không thể sử dụng trên IP này"
            }), 403
            
        # Kiểm tra hardware ID nếu có
        current_hw_id = request.headers.get('X-Hardware-ID')
        if current_hw_id and stored_key['hardware_id'] != current_hw_id:
            return jsonify({
                "status": "error",
                "message": "Key không thể sử dụng trên thiết bị này"
            }), 403
            
        # Tính thời gian còn lại
            expires_at = stored_key['expires_at']
            remaining = (expires_at - datetime.utcnow()).total_seconds()
        
        if remaining <= 0:
            return jsonify({
                "status": "error",
                "message": "Key đã hết hạn"
            }), 400
            
        return jsonify({
            "status": "ok",
            "expires_in": int(remaining),
            "message": "Key hợp lệ"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))