from pymongo import MongoClient
import sys

try:
    # Adicionamos um timeout de 5 segundos para não travar o Django se o Mongo cair
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    
    # Testa a conexão
    client.server_info() 
    
    db = client["Monitoramento_iot"]
    collection = db["Sensor_logs"]
    
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível conectar ao MongoDB: {e}")
    # Em produção, você usaria um sistema de logs aqui
    db = None
    collection = None