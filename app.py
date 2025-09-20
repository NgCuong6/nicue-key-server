from flask import Flask, request, jsonify, render_template_string, redirect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import jwt
import hashlib
import uuid
import datetime
import os
import json
import requests
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Cấu hình bảo mật
SECRET_KEY = os.getenv('SECRET_KEY')
MONGO_URI = os.getenv('MONGODB_URI')
JWT_SECRET = os.getenv('JWT_SECRET')
LINK4M_API_KEY = os.getenv('LINK4M_API_KEY')

# Tạo RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Kết nối MongoDB
client = MongoClient(MONGO_URI)
db = client.keydb
keys_collection = db.keys
blacklist_collection = db.blacklist
analytics_collection = db.analytics

# Rate limiting
limiter = Limiter(
    app=app,
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
            # Log analytics
            analytics_collection.insert_one({
                "event": "blocked_request",
                "ip": ip,
                "timestamp": datetime.datetime.utcnow(),
                "reason": "blacklisted"
            })
            return jsonify({"status": "error", "message": "IP đã bị chặn"}), 403
        
        # Kiểm tra User-Agent
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or any(bot in user_agent.lower() for bot in ['python-requests', 'curl', 'wget']):
            blacklist_collection.insert_one({
                "ip": ip,
                "reason": "Invalid User-Agent",
                "timestamp": datetime.datetime.utcnow()
            })
            return jsonify({"status": "error", "message": "Access denied"}), 403
            
        return f(*args, **kwargs)
    return decorated

def encrypt_key(key_data):
    """Mã hóa key với RSA"""
    message = json.dumps(key_data).encode()
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext.hex()

def decrypt_key(encrypted_key):
    """Giải mã key với RSA"""
    try:
        ciphertext = bytes.fromhex(encrypted_key)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return json.loads(plaintext.decode())
    except Exception:
        return None

@app.route('/')
def home():
    return render_template_string("""
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
            .stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin: 20px 0;
            }
            .stat-box {
                background: #4d4d4d;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
            }
            .stat-number {
                font-size: 24px;
                color: #00ff00;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 NiCue Mod Key System</h1>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{{ active_keys }}</div>
                    <div>Keys Active</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ uptime }}%</div>
                    <div>Uptime</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ blocked_ips }}</div>
                    <div>IPs Blocked</div>
                </div>
            </div>

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
                <p>• Hệ thống tự động phát hiện và chặn bypass</p>
            </div>

            <div class="info">
                <h3>📞 Liên hệ hỗ trợ:</h3>
                <p>• Zalo: 0349667922</p>
                <p>• Youtube: NiCue Mod</p>
            </div>
        </div>
    </body>
    </html>
    """, active_keys=keys_collection.count_documents({"expires_at": {"$gt": datetime.datetime.utcnow()}}),
        uptime=99.9,
        blocked_ips=blacklist_collection.count_documents({}))

@app.route('/key/')
def show_key():
    key = request.args.get('key')
    if not key:
        return "Key không hợp lệ!", 400
        
    return render_template_string("""
    <html>
    <head>
        <title>Key NiCue Mod</title>
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
            .key-box {
                background: #3d3d3d;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
                position: relative;
            }
            .key {
                font-size: 18px;
                color: #00ff00;
                word-break: break-all;
                font-family: monospace;
                margin: 10px 0;
            }
            .copy-btn {
                background: #00ff00;
                color: #000;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 10px;
            }
            .copy-btn:hover {
                background: #00cc00;
            }
            .timer {
                font-size: 24px;
                color: #ff3333;
                margin: 20px 0;
            }
            .info {
                background: #3d3d3d;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
            }
            .loading {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                border-radius: 5px;
            }
            .spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #00ff00;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
        <script>
            function startTimer(duration, display) {
                var timer = duration, minutes, seconds;
                setInterval(function () {
                    minutes = parseInt(timer / 60, 10);
                    seconds = parseInt(timer % 60, 10);

                    minutes = minutes < 10 ? "0" + minutes : minutes;
                    seconds = seconds < 10 ? "0" + seconds : seconds;

                    display.textContent = minutes + ":" + seconds;

                    if (--timer < 0) {
                        display.textContent = "HẾT HẠN!";
                        document.querySelector('.key-box').style.opacity = "0.5";
                    }
                }, 1000);
            }

            function copyKey() {
                var key = document.querySelector('.key').textContent;
                navigator.clipboard.writeText(key);
                var btn = document.querySelector('.copy-btn');
                btn.textContent = 'Đã Copy!';
                setTimeout(() => {
                    btn.textContent = 'Copy Key';
                }, 2000);
            }

            window.onload = function () {
                var twentyMinutes = 60 * 20,
                    display = document.querySelector('#time');
                startTimer(twentyMinutes, display);
                
                // Hiệu ứng loading
                setTimeout(() => {
                    document.querySelector('.loading').style.display = 'none';
                }, 1500);
            };
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🔑 Key NiCue Mod</h1>
            
            <div class="key-box">
                <div class="loading">
                    <div class="spinner"></div>
                </div>
                <h3>Key của bạn:</h3>
                <p class="key">{{ key }}</p>
                <button class="copy-btn" onclick="copyKey()">Copy Key</button>
            </div>

            <div class="info">
                <h3>⏰ Thời gian còn lại:</h3>
                <p class="timer"><span id="time">20:00</span></p>
            </div>

            <div class="info">
                <h3>📋 Hướng dẫn:</h3>
                <p>1. Nhấn nút "Copy Key" ở trên</p>
                <p>2. Mở tool NiCue Mod</p>
                <p>3. Chọn "Nhập Key & Sử Dụng Tool"</p>
                <p>4. Dán key vào và nhấn Enter</p>
            </div>

            <div class="info">
                <h3>⚠️ Lưu ý:</h3>
                <p>• Key chỉ có hiệu lực trong 20 phút</p>
                <p>• Key chỉ sử dụng được trên 1 máy</p>
                <p>• Không chia sẻ key cho người khác</p>
                <p>• Hệ thống tự động phát hiện hành vi bất thường</p>
            </div>
        </div>
    </body>
    </html>
    """, key=key)

@app.route('/generate', methods=['GET', 'POST'])
def generate_key():
    try:
        # Lấy thông tin từ request
        params = request.args.to_dict()
        print("DEBUG - Request params:", params)  # Debug line
        
        # Lấy thông tin thiết bị và IP
        ip = request.remote_addr
        hw_id = request.headers.get('X-Hardware-ID', '')
        user_agent = request.headers.get('User-Agent', '')
        
        # Tạo JWT token và key data
        now = datetime.datetime.utcnow()
        key_data = {
            "key_id": str(uuid.uuid4()),
            "ip": ip,
            "hardware_id": hw_id,
            "user_agent": user_agent,
            "created_at": now,
            "expires_at": now + datetime.timedelta(minutes=20),
            "params": params  # Lưu lại các params từ Link4M
        }
        
        # Mã hóa và lưu key
        jwt_token = jwt.encode(key_data, JWT_SECRET, algorithm='HS256')
        key_data['key'] = jwt_token
        key_data['encrypted_key'] = encrypt_key(key_data)
        
        # Lưu vào database
        keys_collection.insert_one(key_data)
        
        # Log analytics
        analytics_collection.insert_one({
            "event": "key_generated",
            "ip": ip,
            "key_id": key_data['key_id'],
            "user_agent": user_agent,
            "params": params,
            "timestamp": now
        })
        
        # Chuyển hướng đến trang hiển thị key
        return redirect(f"/key/?key={jwt_token}")
        
        # Thu thập thông tin
        ip = request.remote_addr
        
        # Kiểm tra xem IP này đã lấy key gần đây chưa
        recent_key = keys_collection.find_one({
            "ip": ip,
            "created_at": {"$gt": datetime.datetime.utcnow() - datetime.timedelta(minutes=20)}
        })
        
        if recent_key:
            if request.method == 'POST':
                return jsonify({
                    "status": "error",
                    "message": "Vui lòng đợi 20 phút trước khi lấy key mới"
                }), 400
            else:
                return render_template_string("""
                    <html>
                        <body style="text-align: center; font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px;">
                            <h2 style="color: #ff3333;">⚠️ Không thể lấy key</h2>
                            <p>Vui lòng đợi 20 phút trước khi lấy key mới</p>
                            <p>Thời gian chờ còn lại: {{ remaining_time }} phút</p>
                        </body>
                    </html>
                    """, remaining_time=int((recent_key['created_at'] + timedelta(minutes=20) - datetime.datetime.utcnow()).total_seconds() / 60))
        
        # Tạo key mới
        key_data = {
            "key_id": str(uuid.uuid4()),
            "ip": ip,
            "hardware_id": request.headers.get('X-Hardware-ID'),
            "tool_version": request.headers.get('X-Tool-Version'),
            "created_at": datetime.datetime.utcnow(),
            "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
        }
        
        # Mã hóa key
        encrypted_key = encrypt_key(key_data)
        
        # Tạo JWT token
        jwt_token = jwt.encode(key_data, JWT_SECRET, algorithm='HS256')
        
        # Lưu vào database
        key_data['key'] = jwt_token
        key_data['encrypted_key'] = encrypted_key
        keys_collection.insert_one(key_data)
        
        # Log analytics
        analytics_collection.insert_one({
            "event": "key_generated",
            "ip": ip,
            "key_id": key_data['key_id'],
            "timestamp": datetime.datetime.utcnow(),
            "tool_version": key_data['tool_version'],
            "params": params  # Lưu lại params nhận được từ Link4M
        })
        
        # Redirect đến trang hiển thị key
        if request.method == 'POST':
            return jsonify({
                "status": "success",
                "redirect_url": f"/key/?key={jwt_token}",
                "message": "Key đã được tạo thành công!"
            })
        else:
            return redirect(f"/key/?key={jwt_token}")
            
    except Exception as e:
        # Log lỗi
        analytics_collection.insert_one({
            "event": "error",
            "error": str(e),
            "timestamp": datetime.utcnow()
        })
        if request.method == 'POST':
            return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return render_template_string("""
                <html>
                    <body style="text-align: center; font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px;">
                        <h2 style="color: #ff3333;">❌ Lỗi</h2>
                        <p>{{ error }}</p>
                        <p><a href="/" style="color: #00ff00;">Quay lại trang chủ</a></p>
                    </body>
                </html>
            """, error=str(e))
            
        # Thu thập thông tin
        ip = request.remote_addr
        hw_id = request.headers.get('X-Hardware-ID')
        tool_version = request.headers.get('X-Tool-Version')
        
        # Kiểm tra xem IP này đã lấy key gần đây chưa
        recent_key = keys_collection.find_one({
            "ip": ip,
            "created_at": {"$gt": datetime.datetime.utcnow() - datetime.timedelta(minutes=20)}
        })
        
        if recent_key:
            return jsonify({
                "status": "error",
                "message": "Vui lòng đợi 20 phút trước khi lấy key mới"
            }), 400
        
        # Tạo key mới
        key_data = {
            "key_id": str(uuid.uuid4()),
            "ip": ip,
            "hardware_id": hw_id,
            "tool_version": tool_version,
            "created_at": datetime.datetime.utcnow(),
            "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
        }
        
        # Mã hóa key
        encrypted_key = encrypt_key(key_data)
        
        # Tạo JWT token
        jwt_token = jwt.encode(key_data, JWT_SECRET, algorithm='HS256')
        
        # Lưu vào database
        key_data['key'] = jwt_token
        key_data['encrypted_key'] = encrypted_key
        keys_collection.insert_one(key_data)
        
        # Log analytics
        analytics_collection.insert_one({
            "event": "key_generated",
            "ip": ip,
            "key_id": key_data['key_id'],
            "timestamp": datetime.datetime.utcnow(),
            "tool_version": tool_version
        })
        
        # Redirect đến trang hiển thị key
        return jsonify({
            "status": "success",
            "redirect_url": f"/key/?key={jwt_token}",
            "message": "Key đã được tạo thành công!"
        })
        
    except Exception as e:
        # Log lỗi
        analytics_collection.insert_one({
            "event": "error",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow()
        })
        return jsonify({"status": "error", "message": str(e)}), 500

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
            # Log suspicious activity
            analytics_collection.insert_one({
                "event": "suspicious_activity",
                "type": "ip_mismatch",
                "key_id": key_data['key_id'],
                "original_ip": stored_key['ip'],
                "attempt_ip": current_ip,
                "timestamp": datetime.datetime.utcnow()
            })
            
            blacklist_collection.insert_one({
                "ip": current_ip,
                "reason": "IP mismatch attempt",
                "key_id": key_data['key_id'],
                "timestamp": datetime.datetime.utcnow()
            })
            
            return jsonify({
                "status": "error",
                "message": "Key không thể sử dụng trên IP này"
            }), 403
            
        # Kiểm tra hardware ID
        current_hw_id = request.headers.get('X-Hardware-ID')
        if current_hw_id and stored_key['hardware_id'] != current_hw_id:
            # Log suspicious activity
            analytics_collection.insert_one({
                "event": "suspicious_activity",
                "type": "hwid_mismatch",
                "key_id": key_data['key_id'],
                "original_hwid": stored_key['hardware_id'],
                "attempt_hwid": current_hw_id,
                "timestamp": datetime.datetime.utcnow()
            })
            
            return jsonify({
                "status": "error",
                "message": "Key không thể sử dụng trên thiết bị này"
            }), 403
            
        # Kiểm tra version
        tool_version = request.headers.get('X-Tool-Version')
        if tool_version != stored_key.get('tool_version'):
            return jsonify({
                "status": "error",
                "message": f"Phiên bản tool không hợp lệ. Vui lòng cập nhật lên v{stored_key['tool_version']}"
            }), 400
            
        # Tính thời gian còn lại
        expires_at = stored_key['expires_at']
        remaining = (expires_at - datetime.datetime.utcnow()).total_seconds()
        
        if remaining <= 0:
            return jsonify({
                "status": "error",
                "message": "Key đã hết hạn"
            }), 400
            
        # Log successful verification
        analytics_collection.insert_one({
            "event": "key_verified",
            "key_id": key_data['key_id'],
            "ip": current_ip,
            "timestamp": datetime.datetime.utcnow()
        })
            
        return jsonify({
            "status": "ok",
            "expires_in": int(remaining),
            "message": "Key hợp lệ"
        })
        
    except Exception as e:
        # Log error
        analytics_collection.insert_one({
            "event": "error",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow()
        })
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/analytics')
@security_check
def analytics():
    try:
        # Basic authentication
        auth = request.authorization
        if not auth or auth.username != os.getenv('ADMIN_USER') or auth.password != os.getenv('ADMIN_PASS'):
            return 'Unauthorized', 401
            
        # Collect statistics
        total_keys = keys_collection.count_documents({})
        active_keys = keys_collection.count_documents({
            "expires_at": {"$gt": datetime.datetime.utcnow()}
        })
        blocked_ips = blacklist_collection.count_documents({})
        
        # Recent activity
        recent_activity = list(analytics_collection.find(
            {}, 
            {'_id': 0}
        ).sort([('timestamp', -1)]).limit(50))
        
        return render_template_string("""
        <html>
        <head>
            <title>NiCue Mod Analytics</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #1a1a1a;
                    color: #fff;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: #2d2d2d;
                    padding: 20px;
                    border-radius: 10px;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 15px;
                    margin: 20px 0;
                }
                .stat-box {
                    background: #3d3d3d;
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                }
                .stat-number {
                    font-size: 24px;
                    color: #00ff00;
                }
                .activity-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                .activity-table th, .activity-table td {
                    padding: 10px;
                    border: 1px solid #4d4d4d;
                    text-align: left;
                }
                .activity-table th {
                    background: #3d3d3d;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 NiCue Mod Analytics</h1>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{{ total_keys }}</div>
                        <div>Total Keys</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{{ active_keys }}</div>
                        <div>Active Keys</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{{ blocked_ips }}</div>
                        <div>Blocked IPs</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">99.9%</div>
                        <div>Uptime</div>
                    </div>
                </div>

                <h2>Recent Activity</h2>
                <table class="activity-table">
                    <tr>
                        <th>Time</th>
                        <th>Event</th>
                        <th>Details</th>
                    </tr>
                    {% for activity in recent_activity %}
                    <tr>
                        <td>{{ activity.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                        <td>{{ activity.event }}</td>
                        <td>{{ activity }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </body>
        </html>
        """, total_keys=total_keys, active_keys=active_keys, 
            blocked_ips=blocked_ips, recent_activity=recent_activity)
            
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))