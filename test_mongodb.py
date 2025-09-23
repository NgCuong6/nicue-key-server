from pymongo import MongoClient

# Thay connection_string bằng connection string của bạn
connection_string = "mongodb+srv://nicueadmin:hFseNHGc19UEA5pT@cluster0.bs6ce9q.mongodb.net/?retryWrites=true&w=majority"

try:
    # Thử kết nối
    client = MongoClient(connection_string)
    
    # Ping database để test kết nối
    client.admin.command('ping')
    
    print("✅ Kết nối MongoDB thành công!")
    
except Exception as e:
    print(f"❌ Lỗi kết nối: {str(e)}")