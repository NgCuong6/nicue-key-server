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
import os
import json
import requests
import random
import string
import time
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
from link4m import Link4M

# Load environment variables
load_dotenv()

# Initialize Link4M API
link4m_api = Link4M()

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
analytics_collection = db.analytics

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


# Enhanced decorator for logging with comprehensive request info
def log_request(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            ip = request.remote_addr
            hw_id = request.headers.get('X-Hardware-ID', '')
            analytics_collection.insert_one({
                "event": "request",
                "ip": ip,
                "path": request.path,
                "method": request.method,
                "user_agent": request.headers.get('User-Agent', ''),
                "hardware_id": hw_id,
                "args": dict(request.args),
                "referrer": request.headers.get('Referer', ''),
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": f.__name__
            })
        except Exception as e:
            print(f"Error logging request: {e}")
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
    """, 
        active_keys=keys_collection.count_documents({"expires_at": {"$gt": datetime.utcnow().isoformat()}}),
        uptime=99.9,
        total_requests=analytics_collection.count_documents({"event": "request"}),
        total_keys=keys_collection.count_documents({}),
        server_time=datetime.utcnow().isoformat())


@app.route('/key/')
@log_request
def show_key():
    token = request.args.get('key')
    if not token:
        return "Key không hợp lệ!", 400
        
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256']) 
        key_id = decoded.get('key_id')
        display_key = decoded.get('display_key')
    except:
        return "Key không hợp lệ!", 400

    key_data = keys_collection.find_one({"key_id": key_id})
    if not key_data:
        return "Key không tồn tại!", 400
        
    # Parse ISO format string back to datetime
    expires_at = datetime.fromisoformat(key_data['expires_at'])
    remaining = (expires_at - datetime.utcnow()).total_seconds()
    remaining_minutes = max(0, int(remaining / 60))

    return render_template_string("""
    <html>
    <head>
        <title>NiCue Mod Key</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                background: #1a1a1a;
                font-family: 'Segoe UI', sans-serif;
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .container {
                width: 100%;
                max-width: 500px;
                background: linear-gradient(145deg, #2d2d2d, #1f1f1f);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
            }

            .header img {
                width: 120px;
                height: 120px;
                border-radius: 60px;
                border: 3px solid #00ff00;
                margin-bottom: 15px;
            }

            .header h1 {
                color: #00ff00;
                font-size: 24px;
                margin: 0;
                text-shadow: 0 0 10px rgba(0,255,0,0.5);
            }

            .key-box {
                background: #2d2d2d;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
                border: 2px solid #00ff00;
                position: relative;
                overflow: hidden;
            }

            .key {
                font-family: monospace;
                font-size: 24px;
                color: #00ff00;
                margin: 10px 0;
                text-shadow: 0 0 5px rgba(0,255,0,0.5);
                word-break: break-all;
            }

            .timer {
                font-size: 36px;
                color: #ff3333;
                margin: 10px 0;
                font-weight: bold;
            }

            .copy-btn {
                background: #00ff00;
                color: #000;
                border: none;
                padding: 10px 20px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 10px;
            }

            .copy-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 0 15px rgba(0,255,0,0.5);
            }

            .info-box {
                background: #2d2d2d;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
            }

            .info-box h3 {
                color: #00ff00;
                margin-top: 0;
                font-size: 18px;
            }

            .info-box p {
                margin: 10px 0;
                color: #ccc;
            }

            .warning {
                color: #ff3333;
            }

            .social {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 20px;
            }

            .social a {
                color: #00ff00;
                text-decoration: none;
                font-size: 16px;
                transition: all 0.3s ease;
            }

            .social a:hover {
                transform: scale(1.1);
                text-shadow: 0 0 10px rgba(0,255,0,0.5);
            }

            @keyframes glow {
                0% { box-shadow: 0 0 5px #00ff00; }
                50% { box-shadow: 0 0 20px #00ff00; }
                100% { box-shadow: 0 0 5px #00ff00; }
            }

            .key-box {
                animation: glow 2s infinite;
            }
        </style>
        <script>
            function startTimer(duration, display) {
                var timer = duration, minutes, seconds;
                setInterval(function () {
                    minutes = parseInt(timer / 60, 10)
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
                btn.textContent = 'Đã Copy ✓';
                setTimeout(() => { btn.textContent = 'Copy Key'; }, 2000);
            }

            window.onload = function () {
                var minutes = {{ remaining_minutes }};
                var display = document.querySelector('#time');
                startTimer(minutes * 60, display);
            };
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/YOUR_IMAGE.jpg" alt="NiCue Mod">
                <h1>NiCue Mod</h1>
            </div>

            <div class="key-box">
                <h2>🔑 Key của bạn</h2>
                <p class="key">{{ display_key }}</p>
                <p class="timer" id="time">{{ remaining_minutes }}:00</p>
                <button class="copy-btn" onclick="copyKey()">Copy Key</button>
            </div>

            <div class="info-box">
                <h3>📋 Hướng dẫn</h3>
                <p>• Copy key ở trên</p>
                <p>• Mở tool NiCue Mod</p>
                <p>• Dán key vào và nhấn Enter</p>
            </div>

            <div class="info-box warning">
                <h3>⚠️ Lưu ý</h3>
                <p>• Key chỉ có hiệu lực trong {{ remaining_minutes }} phút</p>
                <p>• Key chỉ sử dụng được 1 lần</p>
                <p>• Không chia sẻ key cho người khác</p>
            </div>

            <div class="social">
                <a href="https://zalo.me/0349667922">💬 Zalo</a>
                <a href="https://youtube.com/@NiCueMod">📺 Youtube</a>
            </div>
        </div>
    </body>
    </html>
    """, display_key=display_key, remaining_minutes=remaining_minutes)


@app.route('/generate', methods=['GET', 'POST'])
@log_request
def generate_key():
    try:
        params = request.args.to_dict()
        url = params.get('url', '')

        print("[DEBUG] Generate Key Request:")
        print(f"Parameters: {params}")
        print(f"IP: {request.remote_addr}")
        print(f"User-Agent: {request.headers.get('User-Agent')}")

        if url:
            link4m_info = link4m_api.verify_link(url)
            if not link4m_info or link4m_info.get('status') != 'success':
                return render_template_string("<h1>❌ Link không hợp lệ</h1>"), 400
            link4m_data = link4m_info.get('data', {})

        ip = request.remote_addr
        hw_id = request.headers.get('X-Hardware-ID', '')
        user_agent = request.headers.get('User-Agent', '')

        recent_key = keys_collection.find_one({
            "ip": ip,
            "created_at": {"$gt": datetime.utcnow() - timedelta(minutes=20)}
        })

        if recent_key:
            now = datetime.utcnow()
            # Parse ISO format string back to datetime
            created_at = datetime.fromisoformat(recent_key['created_at'])
            expires_at = created_at + timedelta(minutes=20)
            remaining = (expires_at - now).total_seconds()
            return render_template_string("<h1>⚠️ Bạn đã lấy key trong 20 phút qua</h1>"), 400

        now = datetime.utcnow()
        display_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

        # Create datetime objects
        created_at = now
        expires_at = now + timedelta(minutes=20)
        
        key_data = {
            "key_id": str(uuid.uuid4()),
            "display_key": display_key,
            "ip": ip,
            "hardware_id": hw_id,
            "user_agent": user_agent,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "params": params,
            "url": url,
            "link4m_info": link4m_data if url else None,
            "status": "active"
        }

        jwt_token = jwt.encode({
            "key_id": key_data["key_id"],
            "display_key": key_data["display_key"],
            "created_at": key_data["created_at"].isoformat(),
            "expires_at": key_data["expires_at"].isoformat()
        }, JWT_SECRET, algorithm='HS256')

        key_data['key'] = jwt_token
        key_data['encrypted_key'] = encrypt_key(key_data)
        keys_collection.insert_one(key_data)

        analytics_collection.insert_one({
            "event": "key_generated",
            "ip": ip,
            "key_id": key_data['key_id'],
            "user_agent": user_agent,
            "params": params,
            "timestamp": now
        })

        return redirect(f"/key/?key={jwt_token}")

    except Exception as e:
        print(f"Error in generate_key: {e}")
        analytics_collection.insert_one({"event": "error", "error": str(e), "timestamp": datetime.utcnow()})
        return render_template_string("<h1>❌ Đã xảy ra lỗi</h1><p>{{error}}</p>", error=str(e)), 500


@app.route('/verify', methods=['POST'])
@limiter.limit("10/minute")
@log_request
def verify_key():
    try:
        data = request.get_json() or {}
        key = data.get('key')

        if not key:
            return jsonify({"status": "error", "message": "Không tìm thấy key"}), 400

        try:
            key_data = jwt.decode(
                key, 
                JWT_SECRET, 
                algorithms=['HS256'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': False,
                    'verify_iat': True,
                    'verify_aud': False
                }
            )
        except jwt.ExpiredSignatureError:
            analytics_collection.insert_one({
                "event": "key_expired",
                "key": key,
                "ip": request.remote_addr,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error", 
                "code": "KEY_EXPIRED",
                "message": "Key đã hết hạn"
            }), 400
        except jwt.InvalidTokenError as e:
            analytics_collection.insert_one({
                "event": "invalid_key",
                "key": key,
                "error": str(e),
                "ip": request.remote_addr,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error",
                "code": "INVALID_KEY", 
                "message": "Key không hợp lệ",
                "detail": str(e)
            }), 400

        stored_key = keys_collection.find_one({"key_id": key_data['key_id']})
        if not stored_key:
            return jsonify({"status": "error", "message": "Key không tồn tại"}), 400

        current_ip = request.remote_addr
        if stored_key['ip'] != current_ip:
            analytics_collection.insert_one({"event": "suspicious_activity","type": "ip_mismatch","key_id": key_data['key_id'],"original_ip": stored_key['ip'],"attempt_ip": current_ip,"timestamp": datetime.utcnow()})
            return jsonify({"status": "error", "message": "Key không thể sử dụng trên IP này"}), 403

        current_hw_id = request.headers.get('X-Hardware-ID')
        if current_hw_id and stored_key.get('hardware_id') != current_hw_id:
            analytics_collection.insert_one({"event": "suspicious_activity","type": "hwid_mismatch","key_id": key_data['key_id'],"original_hwid": stored_key.get('hardware_id'),"attempt_hwid": current_hw_id,"timestamp": datetime.utcnow()})
            return jsonify({"status": "error", "message": "Key không thể sử dụng trên thiết bị này"}), 403

        # Parse ISO format string back to datetime
        expires_at = datetime.fromisoformat(stored_key['expires_at'])
        remaining = (expires_at - datetime.utcnow()).total_seconds()
        if remaining <= 0:
            return jsonify({"status": "error", "message": "Key đã hết hạn"}), 400

        analytics_collection.insert_one({"event": "key_verified", "key_id": key_data['key_id'], "ip": current_ip, "timestamp": datetime.utcnow()})

        return jsonify({"status": "ok", "expires_in": int(remaining), "message": "Key hợp lệ", "tool_config": {"features": {"mod_ff_max": True, "mod_ff_th": True, "optimize_image": True}, "files": {"comic_bug": True, "tanjiro": True, "booya": True, "seven": True, "hippo": True}}})

    except Exception as e:
        analytics_collection.insert_one({"event": "error", "error": str(e), "timestamp": datetime.utcnow()})
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/analytics')
@log_request
def analytics():
    try:
        auth = request.authorization
        if not auth or auth.username != os.getenv('ADMIN_USER') or auth.password != os.getenv('ADMIN_PASS'):
            return 'Unauthorized', 401

        total_keys = keys_collection.count_documents({})
        active_keys = keys_collection.count_documents({"expires_at": {"$gt": datetime.utcnow()}})
        
        recent_activity = list(analytics_collection.find({}, {'_id': 0}).sort([('timestamp', -1)]).limit(50))

        return render_template_string("<h1>Analytics</h1>"), 200
    except Exception as e:
        return str(e), 500


# Cleanup scheduler
def cleanup_old_data():
    try:
        # Xóa key hết hạn sau 1 ngày
        keys_collection.delete_many({
            "expires_at": {"$lt": (datetime.utcnow() - timedelta(days=1)).isoformat()}
        })
        
        # Giữ lại analytics trong 7 ngày
        analytics_collection.delete_many({
            "timestamp": {"$lt": (datetime.utcnow() - timedelta(days=7)).isoformat()}
        })
        
        print(f"Cleanup completed at {datetime.utcnow().isoformat()}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Scheduled cleanup every hour
def run_scheduled_cleanup():
    while True:
        cleanup_old_data()
        time.sleep(3600)  # 1 hour

if __name__ == '__main__':
    # Start cleanup thread
    import threading
    cleanup_thread = threading.Thread(target=run_scheduled_cleanup, daemon=True)
    cleanup_thread.start()
    
    # Run app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))