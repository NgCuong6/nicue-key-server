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
    active_keys = keys_collection.count_documents({"expires_at": {"$gt": datetime.utcnow().isoformat()}})
    total_requests = analytics_collection.count_documents({"event": "request"})
    total_keys = keys_collection.count_documents({})
    server_time = datetime.utcnow().isoformat()
    
    return render_template_string("""
    <html>
    <head>
        <title>NiCue Mod Key System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
                color: #fff;
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 50px;
                animation: fadeInDown 1s ease;
            }
            .header h1 {
                font-size: 2.5em;
                margin: 0;
                background: linear-gradient(45deg, #00ff00, #00cc00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 30px rgba(0,255,0,0.3);
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .stat-card {
                background: rgba(45, 45, 45, 0.9);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                backdrop-filter: blur(10px);
                animation: fadeInUp 1s ease;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0,255,0,0.1);
            }
            .stat-number {
                font-size: 2.5em;
                font-weight: 600;
                margin: 10px 0;
                background: linear-gradient(45deg, #00ff00, #00cc00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .stat-label {
                color: #aaa;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .info-section {
                background: rgba(45, 45, 45, 0.9);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                backdrop-filter: blur(10px);
                animation: fadeInUp 1s ease;
                transition: transform 0.3s ease;
            }
            .info-section:hover {
                transform: translateY(-5px);
            }
            .info-section h2 {
                color: #00ff00;
                margin-top: 0;
                font-size: 1.5em;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .info-section ul {
                list-style: none;
                padding: 0;
                margin: 20px 0;
            }
            .info-section li {
                margin: 15px 0;
                padding-left: 25px;
                position: relative;
            }
            .info-section li:before {
                content: "•";
                color: #00ff00;
                position: absolute;
                left: 0;
                font-size: 1.5em;
                line-height: 1;
            }
            .warning li {
                color: #ff4444;
            }
            .contact {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 30px;
            }
            .contact a {
                color: #fff;
                text-decoration: none;
                padding: 12px 25px;
                border-radius: 25px;
                background: linear-gradient(45deg, #00ff00, #00cc00);
                transition: all 0.3s ease;
                font-weight: 500;
            }
            .contact a:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,255,0,0.3);
            }
            .server-status {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(45, 45, 45, 0.9);
                padding: 10px 20px;
                border-radius: 25px;
                font-size: 0.9em;
                backdrop-filter: blur(10px);
            }
            .status-dot {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #00ff00;
                border-radius: 50%;
                margin-right: 5px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.5); opacity: 0.5; }
                100% { transform: scale(1); opacity: 1; }
            }
            @keyframes fadeInDown {
                from { transform: translateY(-30px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes fadeInUp {
                from { transform: translateY(30px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @media (max-width: 768px) {
                .container { padding: 20px; }
                .header h1 { font-size: 2em; }
                .stat-card { padding: 20px; }
                .info-section { padding: 20px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 NiCue Mod Key System</h1>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Active Keys</div>
                    <div class="stat-number">{{ active_keys }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Keys Generated</div>
                    <div class="stat-number">{{ total_keys }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Requests</div>
                    <div class="stat-number">{{ total_requests }}</div>
                </div>
            </div>

            <div class="info-section">
                <h2>⚡ System Status</h2>
                <ul>
                    <li>Server đang hoạt động bình thường</li>
                    <li>Thời hạn key: 20 phút</li>
                    <li>Chế độ bảo mật nâng cao đang được kích hoạt</li>
                    <li>Hệ thống đang được giám sát 24/7</li>
                </ul>
            </div>

            <div class="info-section warning">
                <h2>⚠️ Security Notice</h2>
                <ul>
                    <li>Chỉ sử dụng tool chính thức để lấy key</li>
                    <li>Không chia sẻ hoặc bán lại key</li>
                    <li>Mỗi key chỉ hoạt động trên một thiết bị</li>
                    <li>Hệ thống tự động phát hiện và chặn các hành vi bypass</li>
                </ul>
            </div>

            <div class="info-section">
                <h2>📞 Support</h2>
                <div class="contact">
                    <a href="https://zalo.me/0349667922" target="_blank">Zalo Support</a>
                    <a href="https://youtube.com/@NiCueMod" target="_blank">YouTube Channel</a>
                </div>
            </div>
        </div>

        <div class="server-status">
            <span class="status-dot"></span>
            Server Online
        </div>
    </body>
    </html>
    """, 
    active_keys=active_keys,
    total_keys=total_keys,
    total_requests=total_requests,
    server_time=server_time)


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
        client_version = data.get('version', '1.0.0')

        if not key:
            return jsonify({
                "status": "error", 
                "code": "NO_KEY",
                "message": "Không tìm thấy key"
            }), 400

        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or 'python-requests' in user_agent.lower():
            analytics_collection.insert_one({
                "event": "suspicious_activity",
                "type": "invalid_user_agent",
                "user_agent": user_agent,
                "ip": request.remote_addr,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error",
                "code": "INVALID_CLIENT",
                "message": "Vui lòng sử dụng phiên bản tool chính thức"
            }), 403

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
                    'verify_aud': False,
                    'require': ['key_id', 'created_at', 'expires_at']
                }
            )
        except jwt.ExpiredSignatureError:
            analytics_collection.insert_one({
                "event": "key_expired",
                "key_id": key_data.get('key_id'),
                "ip": request.remote_addr,
                "user_agent": user_agent,
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
                "error": str(e),
                "ip": request.remote_addr,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error",
                "code": "INVALID_KEY", 
                "message": "Key không hợp lệ hoặc đã bị chỉnh sửa",
                "detail": str(e)
            }), 400

        stored_key = keys_collection.find_one({"key_id": key_data['key_id']})
        if not stored_key:
            analytics_collection.insert_one({
                "event": "key_not_found",
                "key_id": key_data['key_id'],
                "ip": request.remote_addr,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error", 
                "code": "KEY_NOT_FOUND",
                "message": "Key không tồn tại hoặc đã bị xóa"
            }), 400

        current_ip = request.remote_addr
        if stored_key['ip'] != current_ip:
            analytics_collection.insert_one({
                "event": "suspicious_activity",
                "type": "ip_mismatch",
                "key_id": key_data['key_id'],
                "original_ip": stored_key['ip'],
                "attempt_ip": current_ip,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error", 
                "code": "IP_MISMATCH",
                "message": "Key này không thể sử dụng trên IP hiện tại"
            }), 403

        current_hw_id = request.headers.get('X-Hardware-ID')
        if current_hw_id and stored_key.get('hardware_id') != current_hw_id:
            analytics_collection.insert_one({
                "event": "suspicious_activity",
                "type": "hwid_mismatch",
                "key_id": key_data['key_id'],
                "original_hwid": stored_key.get('hardware_id'),
                "attempt_hwid": current_hw_id,
                "ip": current_ip,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error",
                "code": "HWID_MISMATCH", 
                "message": "Key này không thể sử dụng trên thiết bị hiện tại"
            }), 403

        # Check if key has been used too many times
        usage_count = analytics_collection.count_documents({
            "event": "key_verified",
            "key_id": key_data['key_id']
        })
        if usage_count > 5:  # Allow some retries but prevent excessive usage
            analytics_collection.insert_one({
                "event": "suspicious_activity",
                "type": "excessive_usage",
                "key_id": key_data['key_id'],
                "usage_count": usage_count,
                "ip": current_ip,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error",
                "code": "EXCESSIVE_USAGE",
                "message": "Key này đã được sử dụng quá nhiều lần"
            }), 403

        # Parse ISO format string back to datetime
        expires_at = datetime.fromisoformat(stored_key['expires_at'])
        remaining = (expires_at - datetime.utcnow()).total_seconds()
        if remaining <= 0:
            analytics_collection.insert_one({
                "event": "key_expired",
                "key_id": key_data['key_id'],
                "ip": current_ip,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            })
            return jsonify({
                "status": "error",
                "code": "KEY_EXPIRED",
                "message": "Key đã hết hạn"
            }), 400

        # Log successful verification
        analytics_collection.insert_one({
            "event": "key_verified",
            "key_id": key_data['key_id'],
            "ip": current_ip,
            "user_agent": user_agent,
            "client_version": client_version,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Return successful response with tool configuration
        return jsonify({
            "status": "ok",
            "expires_in": int(remaining),
            "message": "Key hợp lệ",
            "user_info": {
                "ip": current_ip,
                "hardware_id": current_hw_id,
                "created_at": stored_key['created_at'],
                "expires_at": stored_key['expires_at']
            },
            "tool_config": {
                "features": {
                    "mod_ff_max": True,
                    "mod_ff_th": True,
                    "optimize_image": True,
                    "advanced_features": usage_count < 3  # Disable advanced features after multiple uses
                },
                "files": {
                    "comic_bug": True,
                    "tanjiro": True,
                    "booya": True,
                    "seven": True,
                    "hippo": True
                },
                "version": {
                    "current": "1.2.0",
                    "required": "1.1.0",
                    "update_url": "https://example.com/update"
                }
            }
        })

    except Exception as e:
        analytics_collection.insert_one({"event": "error", "error": str(e), "timestamp": datetime.utcnow()})
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/analytics')
@log_request
def analytics():
    try:
        auth = request.authorization
        if not auth or auth.username != os.getenv('ADMIN_USER') or auth.password != os.getenv('ADMIN_PASS'):
            return ('Could not verify your credentials', 401,
                   {'WWW-Authenticate': 'Basic realm="Login Required"'})

        total_keys = keys_collection.count_documents({})
        active_keys = keys_collection.count_documents({"expires_at": {"$gt": datetime.utcnow().isoformat()}})
        total_requests = analytics_collection.count_documents({"event": "request"})
        successful_verifications = analytics_collection.count_documents({"event": "key_verified"})
        
        # Get recent activity
        recent_activity = list(analytics_collection.find({}, {'_id': 0})
                             .sort([('timestamp', -1)])
                             .limit(50))
        
        # Get hourly key generation stats for the last 24 hours
        now = datetime.utcnow()
        hourly_stats = []
        for i in range(24):
            start_time = now - timedelta(hours=i+1)
            end_time = now - timedelta(hours=i)
            count = analytics_collection.count_documents({
                "event": "key_generated",
                "timestamp": {
                    "$gte": start_time.isoformat(),
                    "$lt": end_time.isoformat()
                }
            })
            hourly_stats.append({
                "hour": start_time.strftime("%H:00"),
                "count": count
            })
        hourly_stats.reverse()

        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NiCue Mod - Analytics Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {
                    font-family: 'Poppins', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
                    color: #fff;
                    min-height: 100vh;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    margin-bottom: 40px;
                    padding: 20px;
                    background: rgba(45, 45, 45, 0.9);
                    border-radius: 15px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                .header h1 {
                    margin: 0;
                    font-size: 2em;
                    background: linear-gradient(45deg, #00ff00, #00cc00);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .stat-card {
                    background: rgba(45, 45, 45, 0.9);
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                .stat-card h3 {
                    margin: 0;
                    font-size: 0.9em;
                    color: #aaa;
                    text-transform: uppercase;
                }
                .stat-card .value {
                    font-size: 2em;
                    font-weight: 600;
                    color: #00ff00;
                    margin: 10px 0;
                }
                .chart-container {
                    background: rgba(45, 45, 45, 0.9);
                    padding: 20px;
                    border-radius: 15px;
                    margin: 20px 0;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                .activity-container {
                    background: rgba(45, 45, 45, 0.9);
                    padding: 20px;
                    border-radius: 15px;
                    margin: 20px 0;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                .activity-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                .activity-table th, .activity-table td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                .activity-table th {
                    background: rgba(0, 0, 0, 0.2);
                    color: #00ff00;
                }
                .activity-table tr:hover {
                    background: rgba(0, 255, 0, 0.1);
                }
                @media (max-width: 768px) {
                    .container {
                        padding: 10px;
                    }
                    .stat-card {
                        padding: 15px;
                    }
                    .activity-table {
                        display: block;
                        overflow-x: auto;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Analytics Dashboard</h1>
                    <p>Real-time statistics and monitoring</p>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Active Keys</h3>
                        <div class="value">{{ active_keys }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Total Keys</h3>
                        <div class="value">{{ total_keys }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Total Requests</h3>
                        <div class="value">{{ total_requests }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Successful Verifications</h3>
                        <div class="value">{{ successful_verifications }}</div>
                    </div>
                </div>

                <div class="chart-container">
                    <h2>Key Generation (Last 24 Hours)</h2>
                    <canvas id="keyChart"></canvas>
                </div>

                <div class="activity-container">
                    <h2>Recent Activity</h2>
                    <div style="overflow-x: auto;">
                        <table class="activity-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Event</th>
                                    <th>IP</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for activity in recent_activity %}
                                <tr>
                                    <td>{{ activity.timestamp }}</td>
                                    <td>{{ activity.event }}</td>
                                    <td>{{ activity.ip }}</td>
                                    <td>
                                        {% if activity.error %}
                                            <span style="color: #ff4444;">{{ activity.error }}</span>
                                        {% elif activity.key_id %}
                                            Key ID: {{ activity.key_id }}
                                        {% else %}
                                            -
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <script>
                const ctx = document.getElementById('keyChart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: {{ hourly_stats|map(attribute='hour')|list|tojson }},
                        datasets: [{
                            label: 'Keys Generated',
                            data: {{ hourly_stats|map(attribute='count')|list|tojson }},
                            borderColor: '#00ff00',
                            backgroundColor: 'rgba(0, 255, 0, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                },
                                ticks: {
                                    color: '#fff'
                                }
                            },
                            x: {
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)'
                                },
                                ticks: {
                                    color: '#fff'
                                }
                            }
                        }
                    }
                });
            </script>
        </body>
        </html>
        """, 
        active_keys=active_keys,
        total_keys=total_keys,
        total_requests=total_requests,
        successful_verifications=successful_verifications,
        recent_activity=recent_activity,
        hourly_stats=hourly_stats)

    except Exception as e:
        print(f"Error in analytics route: {e}")
        return jsonify({"error": str(e)}), 500


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