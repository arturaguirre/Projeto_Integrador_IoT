from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["Monitoramento_iot"]
collection = db["Sensor_logs"]
