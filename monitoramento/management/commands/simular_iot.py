import random, time
from django.core.management.base import BaseCommand
from monitoramento.models import Sensor

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Simulando dados IoT... CTRL+C para parar")
        while True:
            sensores = Sensor.objects.filter(ativo=True)
            for sensor in sensores:
                valor = random.uniform(15.0, 35.0) 
                print(f"Sensor {sensor.nome}: {valor:.2f}°C")
            time.sleep(10) 