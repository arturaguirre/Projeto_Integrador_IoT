import random
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from monitoramento.models import Sensor
from monitoramento.mongo import collection  # Importamos nossa conexão do Mongo

class Command(BaseCommand):
    help = 'Simula o envio de dados de sensores IoT em tempo real (Background Worker)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO SIMULAÇÃO IoT BOREAS ---"))
        self.stdout.write(self.style.WARNING("Pressione CTRL+C para parar"))

        while True:
            # Pega apenas sensores que estão marcados como 'Ativo'
            sensores = Sensor.objects.filter(ativo=True)
            
            if not sensores.exists():
                self.stdout.write(self.style.ERROR("Nenhum sensor ativo encontrado. Aguardando cadastro..."))
                time.sleep(10)
                continue

            for sensor in sensores:
                # 1. Gerar dados aleatórios realistas
                temp = round(random.uniform(18.0, 32.0), 1)  # 18°C a 32°C
                umid = round(random.uniform(40.0, 70.0), 1)  # 40% a 70%
                gas = round(random.uniform(0.0, 3.5), 2)     # 0 a 3.5 ppm

                # 2. Atualizar o "Estado Atual" no SQL (O que aparece nos Cards do Dashboard)
                sensor.temperatura = temp
                sensor.umidade = umid
                sensor.gas_nh3 = gas
                sensor.save()

                # 3. Gravar Histórico no MongoDB (Para os gráficos e logs)
                if collection is not None:
                    try:
                        documento = {
                            "sensor_id": sensor.id,
                            "sensor_nome": sensor.nome,
                            "unidade_id": sensor.unidade.id,
                            "unidade_nome": sensor.unidade.nome,
                            "temperatura": temp,
                            "umidade": umid,
                            "gas_nh3": gas,
                            "timestamp": datetime.now()
                        }
                        collection.insert_one(documento)
                        status_mongo = "SAVED"
                    except Exception as e:
                        status_mongo = f"ERROR ({e})"
                else:
                    status_mongo = "OFFLINE"

                # Log no terminal para você acompanhar visualmente
                msg = f"[{datetime.now().strftime('%H:%M:%S')}] {sensor.nome}: {temp}°C | {umid}% | Mongo: {status_mongo}"
                self.stdout.write(msg)

            # Espera 10 segundos antes da próxima leitura geral
            self.stdout.write("--- Aguardando ciclo... ---")
            time.sleep(10)