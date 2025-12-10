import time
import random
import json
from kafka import KafkaProducer

# --- CONFIGURACIÓN ---
# Asegúrate de que este puerto coincide con el docker-compose de la Persona A
KAFKA_SERVER = 'localhost:9092' 
TOPIC_NAME = 'tweets_topic'

# --- DATOS SIMULADOS (Fuente ) ---
usuarios = ["@DataFan", "@SparkGuru", "@PythonDev", "@EstudianteIng", "@BigDataLover"]

hashtags = [
    "#Spark", "#BigData", "#Streaming", "#Examen", 
    "#Python", "#Kafka", "#RealTime", "#IA"
]

frases_base = [
    "estoy aprendiendo mucho con",
    "el proyecto de clase usa",
    "qué complicado es configurar",
    "increíble la velocidad de",
    "mañana tengo examen de",
    "repasando conceptos de"
]

def generador_tweets():
    """
    Genera un diccionario (JSON) simulando un tweet.
    Diseñamos lógica aleatoria como pide la tarea[cite: 28].
    """
    usuario = random.choice(usuarios)
    hashtag = random.choice(hashtags)
    frase = random.choice(frases_base)
    
    # Construimos el mensaje completo
    mensaje_texto = f"{frase} {hashtag}"
    
    # Estructuramos el dato como JSON para que Spark lo lea mejor luego
    tweet = {
        "usuario": usuario,
        "texto": mensaje_texto,
        "hashtag_principal": hashtag, # Útil para el filtrado posterior
        "timestamp": time.time()
    }
    return tweet

def main():
    print(f"🔄 Iniciando simulador de Twitter hacia {KAFKA_SERVER}...")
    
    # Inicializamos el Producer
    # value_serializer asegura que enviamos JSON codificado en utf-8
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    try:
        # Bucle infinito 
        while True:
            tweet_simulado = generador_tweets()
            
            # Enviar al "buzón" (Topic)
            print(f"📩 Enviando: {tweet_simulado['texto']}")
            producer.send(TOPIC_NAME, value=tweet_simulado)
            
            # Simular tiempo real (1 tweet por segundo) 
            time.sleep(1) 
            
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error conectando con Kafka: {e}")
        print("Tip: Verifica que el contenedor de Docker de la Persona A esté encendido.")
    finally:
        producer.close()

if __name__ == "__main__":
    main()