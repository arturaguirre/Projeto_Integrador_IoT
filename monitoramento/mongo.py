from pymongo import MongoClient
import sys

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    
    client.server_info()
    
    db = client["Monitoramento_iot"]
    collection = db["Sensor_logs"]
    
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível conectar ao MongoDB: {e}")
    db = None
    collection = None