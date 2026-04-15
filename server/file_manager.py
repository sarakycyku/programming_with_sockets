import os
import json
from datetime import datetime
from config import DATA_DIR

class FileManager:
    def __init__(self):
        self.data_dir = DATA_DIR
    
    def list_files(self):
        """Lista e te gjithe files qe ndodhen ne server"""
        try:
            files = os.listdir(self.data_dir)
            return {"status": "success", "files": files}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def read_file(self, filename):
        """Leximi i permbajtjes se file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.abspath(filepath).startswith(os.path.abspath(self.data_dir)):
                return {"status": "error", "message": "Nuk lejohet qasja"}
            
            if not os.path.exists(filepath):
                return {"status": "error", "message": f"File '{filename}' nuk ekziston!"}
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    def upload_file(self, filename, content):
        """Upload nje file ne server"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "success", "message": f"File '{filename}' u ngarkua me sukses!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def download_file(self, filename):
        """Download file nga serveri"""
        return self.read_file(filename)
    
    def delete_file(self, filename):
        """Fshije nje file nga serveri"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.abspath(filepath).startswith(os.path.abspath(self.data_dir)):
                return {"status": "error", "message": "Qasje e ndaluar!"}
            
            if not os.path.exists(filepath):
                return {"status": "error", "message": f"File '{filename}' nuk ekziston!"}
            
            os.remove(filepath)
            return {"status": "success", "message": f"File '{filename}' u fshi me sukses!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}