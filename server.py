#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import time
import random
import string
import hashlib
import threading
import logging
import signal
import sys
import os
from collections import defaultdict
from datetime import datetime, timedelta

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== CẤU HÌNH ====================
class Config:
    # Thời gian sống của key (20 phút)
    KEY_LIFETIME = 20 * 60
    
    # Giới hạn request (tối đa 5 request/phút từ 1 IP)
    MAX_REQUESTS_PER_MINUTE = 5
    
    # Thời gian cleanup định kỳ (3 phút)
    CLEANUP_INTERVAL = 3 * 60
    
    # Độ dài key
    KEY_LENGTH = 16
    
    # Thời gian cache fingerprint (1 giờ)
    FINGERPRINT_CACHE_TIME = 60 * 60
    
    # Maximum số key trong memory (để tránh memory leak)
    MAX_KEYS_IN_MEMORY = 10000

config = Config()

# ==================== STORAGE ====================
class KeyStorage:
    def __init__(self):
        self.keys = {}  # { "KEY": {"expire": timestamp, "ip": "1.2.3.4", "fingerprint": "hash"} }
        self.ip_to_key = {}  # IP -> key mapping
        self.request_count = defaultdict(list)  # Rate limiting
        self.fingerprint_cache = {}  # Cache fingerprint để tăng tốc
        self.lock = threading.RLock()  # RLock để tránh deadlock
        self.stats = {
            'total_keys_generated': 0,
            'total_requests': 0,
            'rate_limited_requests': 0,
            'expired_keys_cleaned': 0
        }
    
    def generate_key(self, length=None):
        """Tạo key ngẫu nhiên với entropy cao"""
        if length is None:
            length = config.KEY_LENGTH
        
        # Sử dụng multiple sources để tăng entropy
        timestamp = str(int(time.time() * 1000000))[-6:]  # Microsecond timestamp
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length-6))
        key = timestamp + random_chars
        
        # Shuffle để key không dễ đoán
        key_list = list(key)
        random.shuffle(key_list)
        return ''.join(key_list)
    
    def create_fingerprint(self, ip, user_agent):
        """Tạo fingerprint với cache để tăng tốc"""
        cache_key = f"{ip}:{user_agent}"
        
        # Kiểm tra cache trước
        if cache_key in self.fingerprint_cache:
            cache_data = self.fingerprint_cache[cache_key]
            if time.time() - cache_data['timestamp'] < config.FINGERPRINT_CACHE_TIME:
                return cache_data['fingerprint']
        
        # Tạo fingerprint mới
        combined = f"{ip}:{user_agent}:{int(time.time() // 3600)}"  # Include hour để rotate
        fingerprint = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        # Lưu vào cache
        self.fingerprint_cache[cache_key] = {
            'fingerprint': fingerprint,
            'timestamp': time.time()
        }
        
        return fingerprint
    
    def check_rate_limit(self, ip):
        """Rate limiting với sliding window"""
        now = time.time()
        minute_ago = now - 60
        
        # Cleanup old requests
        self.request_count[ip] = [req_time for req_time in self.request_count[ip] if req_time > minute_ago]
        
        # Check limit
        if len(self.request_count[ip]) >= config.MAX_REQUESTS_PER_MINUTE:
            self.stats['rate_limited_requests'] += 1
            return False
        
        # Add current request
        self.request_count[ip].append(now)
        self.stats['total_requests'] += 1
        return True
    
    def cleanup_expired_keys(self):
        """Dọn dẹp key hết hạn với batch processing"""
        now = int(time.time())
        expired_keys = []
        
        # Tìm key hết hạn
        for key, data in list(self.keys.items()):
            if data["expire"] <= now:
                expired_keys.append(key)
        
        # Xóa theo batch
        for key in expired_keys:
            try:
                key_data = self.keys.pop(key, None)
                if key_data:
                    ip = key_data["ip"]
                    if ip in self.ip_to_key and self.ip_to_key[ip] == key:
                        del self.ip_to_key[ip]
                    self.stats['expired_keys_cleaned'] += 1
            except KeyError:
                pass  # Key đã bị xóa bởi thread khác
        
        # Cleanup fingerprint cache
        self.cleanup_fingerprint_cache()
        
        # Cleanup request count cho IP không hoạt động
        self.cleanup_request_count()
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired keys")
        
        return len(expired_keys)
    
    def cleanup_fingerprint_cache(self):
        """Dọn dẹp fingerprint cache cũ"""
        now = time.time()
        expired_cache = []
        
        for cache_key, cache_data in list(self.fingerprint_cache.items()):
            if now - cache_data['timestamp'] > config.FINGERPRINT_CACHE_TIME:
                expired_cache.append(cache_key)
        
        for cache_key in expired_cache:
            self.fingerprint_cache.pop(cache_key, None)
    
    def cleanup_request_count(self):
        """Dọn dẹp request count cũ"""
        now = time.time()
        minute_ago = now - 60
        
        for ip in list(self.request_count.keys()):
            self.request_count[ip] = [req_time for req_time in self.request_count[ip] if req_time > minute_ago]
            if not self.request_count[ip]:
                del self.request_count[ip]
    
    def get_stats(self):
        """Lấy thống kê server"""
        return {
            **self.stats,
            'active_keys': len(self.keys),
            'active_ips': len(self.ip_to_key),
            'cached_fingerprints': len(self.fingerprint_cache),
            'tracked_ips_for_rate_limit': len(self.request_count),
            'server_uptime': int(time.time() - start_time),
            'memory_usage_keys': len(self.keys),
            'memory_usage_percentage': min(100, (len(self.keys) / config.MAX_KEYS_IN_MEMORY) * 100)
        }

# Global storage instance
storage = KeyStorage()
start_time = time.time()

# ==================== API ENDPOINTS ====================
@app.route("/")
def index():
    """Root endpoint với thông tin server"""
    return jsonify({
        "status": "ok",
        "message": "NiCue Key Server v2.0",
        "endpoints": {
            "getkey": "/getkey",
            "verify": "/verify/<key>", 
            "status": "/status",
            "health": "/health"
        },
        "server_time": datetime.now().isoformat(),
        "uptime": int(time.time() - start_time)
    })

@app.route("/getkey")
def get_key():
    try:
        with storage.lock:
            user_ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown')
            user_agent = request.headers.get('User-Agent', 'Unknown')
            now = int(time.time())
            link4m_token = request.args.get('link4m_token')
            
            # Verify Link4M token
            if not link4m_token:
                return jsonify({
                    "status": "error",
                    "message": "Vui lòng vượt link để lấy key",
                    "code": "LINK4M_REQUIRED"
                }), 403
            
            # Kiểm tra rate limiting
            if not storage.check_rate_limit(user_ip):
                return jsonify({
                    "status": "error",
                    "message": "Quá nhiều request! Vui lòng đợi 1 phút.",
                    "retry_after": 60
                }), 429
            
            # Kiểm tra memory limit
            if len(storage.keys) >= config.MAX_KEYS_IN_MEMORY:
                # Force cleanup khi đạt limit
                cleaned = storage.cleanup_expired_keys()
                if len(storage.keys) >= config.MAX_KEYS_IN_MEMORY:
                    logger.warning("Server memory limit reached, rejecting new requests")
                    return jsonify({
                        "status": "error",
                        "message": "Server đang quá tải, vui lòng thử lại sau."
                    }), 503
            
            # Tạo fingerprint
            fingerprint = storage.create_fingerprint(user_ip, user_agent)
            
            # Kiểm tra key hiện tại
            if user_ip in storage.ip_to_key:
                existing_key = storage.ip_to_key[user_ip]
                if existing_key in storage.keys and storage.keys[existing_key]["expire"] > now:
                    # Kiểm tra fingerprint
                    if storage.keys[existing_key]["fingerprint"] == fingerprint:
                        expire_in = storage.keys[existing_key]["expire"] - now
                        return jsonify({
                            "status": "ok",
                            "key": existing_key,
                            "expire_in": expire_in,
                            "message": "Key đã tồn tại",
                            "expires_at": datetime.fromtimestamp(storage.keys[existing_key]["expire"]).isoformat()
                        })
                    else:
                        # Fingerprint không khớp
                        return jsonify({
                            "status": "error",
                            "message": "Đã có key active từ IP này với trình duyệt khác!",
                            "code": "FINGERPRINT_MISMATCH"
                        }), 403
            
            # Tạo key mới
            new_key = storage.generate_key()
            expire_time = now + config.KEY_LIFETIME
            
            storage.keys[new_key] = {
                "expire": expire_time,
                "ip": user_ip,
                "fingerprint": fingerprint,
                "created_at": now,
                "user_agent": user_agent[:100]  # Truncate user agent
            }
            storage.ip_to_key[user_ip] = new_key
            storage.stats['total_keys_generated'] += 1
            
            logger.info(f"Generated new key for IP {user_ip}")
            
            return jsonify({
                "status": "ok",
                "key": new_key,
                "expire_in": config.KEY_LIFETIME,
                "message": "Key mới được tạo",
                "expires_at": datetime.fromtimestamp(expire_time).isoformat(),
                "server_time": datetime.fromtimestamp(now).isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in get_key: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Lỗi server nội bộ"
        }), 500

@app.route("/verify/<key>")
def verify_key(key):
    try:
        with storage.lock:
            now = int(time.time())
            user_ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown')
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            # Validate key format
            if not key or len(key) != config.KEY_LENGTH or not key.isalnum():
                return jsonify({
                    "status": "fail", 
                    "message": "Key không đúng định dạng",
                    "code": "INVALID_FORMAT"
                })
            
            if key not in storage.keys:
                return jsonify({
                    "status": "fail", 
                    "message": "Key không tồn tại",
                    "code": "KEY_NOT_FOUND"
                })
            
            key_data = storage.keys[key]
            
            # Kiểm tra hết hạn
            if key_data["expire"] <= now:
                # Xóa key hết hạn
                ip = key_data["ip"]
                storage.keys.pop(key, None)
                if ip in storage.ip_to_key and storage.ip_to_key[ip] == key:
                    storage.ip_to_key.pop(ip, None)
                
                return jsonify({
                    "status": "fail", 
                    "message": "Key đã hết hạn",
                    "code": "EXPIRED"
                })
            
            # Kiểm tra IP
            if key_data["ip"] != user_ip:
                logger.warning(f"IP mismatch for key {key}: expected {key_data['ip']}, got {user_ip}")
                return jsonify({
                    "status": "fail", 
                    "message": "IP không khớp",
                    "code": "IP_MISMATCH"
                })
            
            # Kiểm tra fingerprint
            fingerprint = storage.create_fingerprint(user_ip, user_agent)
            if key_data["fingerprint"] != fingerprint:
                return jsonify({
                    "status": "fail", 
                    "message": "Fingerprint không khớp",
                    "code": "FINGERPRINT_MISMATCH"
                })
            
            expire_in = key_data["expire"] - now
            return jsonify({
                "status": "ok",
                "expire_in": expire_in,
                "message": "Key hợp lệ",
                "expires_at": datetime.fromtimestamp(key_data["expire"]).isoformat(),
                "created_at": datetime.fromtimestamp(key_data["created_at"]).isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in verify_key: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Lỗi server nội bộ"
        }), 500

@app.route("/status")
def get_status():
    """API kiểm tra trạng thái hệ thống"""
    try:
        with storage.lock:
            # Cleanup trước khi trả stats
            storage.cleanup_expired_keys()
            stats = storage.get_stats()
            
            return jsonify({
                "status": "ok",
                "server_status": "running",
                "timestamp": datetime.now().isoformat(),
                **stats
            })
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Không thể lấy thống kê server"
        }), 500

@app.route("/health")
def health_check():
    """Health check endpoint cho load balancer"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": int(time.time() - start_time)
    })

# ==================== BACKGROUND TASKS ====================
def background_cleanup():
    """Background task dọn dẹp định kỳ"""
    logger.info("Background cleanup thread started")
    
    while True:
        try:
            time.sleep(config.CLEANUP_INTERVAL)
            
            with storage.lock:
                cleaned_keys = storage.cleanup_expired_keys()
                stats = storage.get_stats()
                
                # Log stats định kỳ
                if cleaned_keys > 0 or stats['active_keys'] > 0:
                    logger.info(
                        f"Cleanup stats - Cleaned: {cleaned_keys}, "
                        f"Active keys: {stats['active_keys']}, "
                        f"Active IPs: {stats['active_ips']}, "
                        f"Memory usage: {stats['memory_usage_percentage']:.1f}%"
                    )
                
                # Warning nếu memory cao
                if stats['memory_usage_percentage'] > 80:
                    logger.warning(f"High memory usage: {stats['memory_usage_percentage']:.1f}%")
                    
        except Exception as e:
            logger.error(f"Error in background cleanup: {str(e)}")
            time.sleep(30)  # Wait before retry

def signal_handler(signum, frame):
    """Graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    
    # Log final stats
    with storage.lock:
        final_stats = storage.get_stats()
        logger.info(f"Final stats: {final_stats}")
    
    sys.exit(0)

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint không tồn tại",
        "code": "NOT_FOUND",
        "available_endpoints": ["/getkey", "/verify/<key>", "/status", "/health"],
        "requested_url": request.url
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "status": "error",
        "message": "Lỗi server nội bộ",
        "code": "INTERNAL_ERROR"
    }), 500

@app.errorhandler(429)
def rate_limit_handler(error):
    return jsonify({
        "status": "error",
        "message": "Quá nhiều request",
        "code": "RATE_LIMITED",
        "retry_after": 60
    }), 429

# ==================== MAIN ====================
if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Khởi động background cleanup thread
    cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
    cleanup_thread.start()
    
    logger.info("🚀 Optimized Key Server starting...")
    logger.info(f"Server will run on http://0.0.0.0:5000")
    logger.info("🔒 Security features enabled:")
    logger.info(f"   • Rate limiting ({config.MAX_REQUESTS_PER_MINUTE} req/min/IP)")
    logger.info("   • Fingerprint verification (IP + User Agent)")
    logger.info(f"   • Auto cleanup every {config.CLEANUP_INTERVAL//60} minutes")
    logger.info(f"   • Key lifetime: {config.KEY_LIFETIME//60} minutes")
    logger.info(f"   • Max keys in memory: {config.MAX_KEYS_IN_MEMORY}")
    logger.info("👉 API Endpoints:")
    logger.info("   • GET /getkey - Lấy key")
    logger.info("   • GET /verify/<key> - Xác minh key")
    logger.info("   • GET /status - Trạng thái server")
    logger.info("   • GET /health - Health check")
    
    try:
        # Production settings
        app.run(
            host="0.0.0.0", 
            port=5000, 
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)