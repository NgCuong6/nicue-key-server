import requests
import os
from dotenv import load_dotenv

load_dotenv()

class Link4M:
    def __init__(self):
        self.api_key = os.getenv('LINK4M_API_KEY')
        self.base_url = "https://api.link4m.vn"
    
    def verify_link(self, url):
        """Verify a Link4M shortened URL and get info"""
        try:
            response = requests.post(
                f"{self.base_url}/verify-link",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": url
                }
            )
            return response.json()
        except Exception as e:
            print(f"Error verifying Link4M URL: {str(e)}")
            return None
            
    def create_link(self, target_url, title=""):
        """Create a new Link4M shortened URL"""
        try:
            response = requests.post(
                f"{self.base_url}/create-link",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": target_url,
                    "title": title
                }
            )
            return response.json()
        except Exception as e:
            print(f"Error creating Link4M URL: {str(e)}")
            return None