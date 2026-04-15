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