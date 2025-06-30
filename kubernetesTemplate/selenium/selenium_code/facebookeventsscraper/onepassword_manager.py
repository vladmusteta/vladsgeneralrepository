"""
1Password CLI Manager
Handles all 1Password related operations
"""
import subprocess
import json

class OnePasswordManager:
    def __init__(self, item_name="Facebook"):
        self.item_name = item_name
    
    def check_cli_availability(self):
        """Check if 1Password CLI is available and authenticated"""
        try:
            subprocess.run(["op", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_field(self, field_name):
        """Get a specific field from 1Password item"""
        try:
            result = subprocess.run(
                ["op", "item", "get", self.item_name, "--field", field_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error getting {field_name} from 1Password: {e}")
            return None
    
    def get_otp(self):
        """Get OTP from 1Password item"""
        try:
            result = subprocess.run(
                ["op", "item", "get", self.item_name, "--otp"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error getting OTP from 1Password: {e}")
            return None
    
    def get_credentials(self):
        """Get username and password from 1Password item"""
        try:
            # Get the full item as JSON
            result = subprocess.run(
                ["op", "item", "get", self.item_name, "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            item_data = json.loads(result.stdout)
            
            username = None
            password = None
            
            # Look through fields to find username and password
            for field in item_data.get("fields", []):
                if field.get("id") == "username" or field.get("label", "").lower() in ["username", "email"]:
                    username = field.get("value")
                elif field.get("id") == "password":
                    password = field.get("value")
            
            return username, password
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error getting credentials from 1Password: {e}")
            return None, None
