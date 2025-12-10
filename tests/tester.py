"""
=============================================================================
SCRIPT DE VERIFICACIÓN DE INFRAESTRUCTURA (TESTER)
=============================================================================
Descripción:
    Este script valida que el entorno de Docker (Zookeeper + Kafka) está
    funcionando correctamente y es accesible desde fuera de los contenedores.

Funcionalidad:
    1. Actúa como PRODUCTOR: Envía 5 mensajes de prueba en formato JSON al
       topic 'tweets_topic'.
    2. Actúa como CONSUMIDOR: Lee esos mismos mensajes del topic para
       confirmar que el flujo de datos es correcto.

Prerrequisitos:
    - El entorno Docker debe estar levantado (docker compose up -d).
    - El topic debe existir (kafka-topics --create ...).
    - Librería necesaria: pip install kafka-python
=============================================================================
"""

import json
import time
from kafka import KafkaProducer, KafkaConsumer

# CONFIGURACIÓN
TOPIC_NAME = 'tweets_topic'
SERVER = 'localhost:9092'

def probando_productor():
    print(f"\n>>> 1. INICIANDO PRODUCTOR (Enviando mensajes a {SERVER})...")
    try:
        # Conectamos con el Kafka que tienes en Docker
        producer = KafkaProducer(
            bootstrap_servers=SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8') # Convertir a JSON automáticamente
        )
        
        # Enviamos 5 mensajes simulados
        for i in range(1, 6):
            mensaje = {"usuario": f"User_{i}", "mensaje": "Hola Kafka", "contador": i}
            producer.send(TOPIC_NAME, value=mensaje)
            print(f" [✔] Enviado: {mensaje}")
            time.sleep(0.5) # Pequeña pausa
            
        producer.flush() # Asegurar que todo se envía
        print(">>> Productor finalizado con éxito.\n")
        
    except Exception as e:
        print(f" [X] ERROR en el Productor: {e}")

def probando_consumidor():
    print(f">>> 2. INICIANDO CONSUMIDOR (Leyendo de {TOPIC_NAME})...")
    try:
        # Creamos un consumidor para leer lo que acabamos de enviar
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=SERVER,
            auto_offset_reset='earliest', # Leer desde el principio
            enable_auto_commit=True,
            consumer_timeout_ms=5000, # Cerrarse si no hay mensajes nuevos en 5 seg
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        print(" ... Escuchando mensajes ...")
        count = 0
        for message in consumer:
            print(f" [✔] Recibido: {message.value}")
            count += 1
            if count >= 5: # Parar después de leer los 5 mensajes de prueba
                break
                
        if count == 0:
            print(" [!] No se leyeron mensajes. ¿Seguro que el topic existe?")
        else:
            print(">>> Consumidor finalizado con éxito. ¡TODO FUNCIONA!")

    except Exception as e:
        print(f" [X] ERROR en el Consumidor: {e}")

if __name__ == "__main__":
    probando_productor()
    time.sleep(1)
    probando_consumidor()