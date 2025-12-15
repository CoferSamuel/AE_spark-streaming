# 🚀 Proyecto Big Data: Simulador de Streaming (Kafka + Spark)

Este proyecto implementa una arquitectura de **Big Data en Tiempo Real**. Simulamos un flujo de datos de una red social (tipo Twitter/X) para procesar tendencias (Trending Topics) al instante.

La arquitectura se basa en un **Clúster de un solo nodo (Single-Node Cluster)** virtualizado con Docker.

-----

## 📋 Estructura del Proyecto

Antes de tocar nada, entiende qué es cada carpeta y archivo:

  * **`docker/docker-compose.yml`**: 🏗️ **Infraestructura.** Define los servicios Zookeeper y Kafka y cómo se conectan. Docker lee este archivo para levantar toda la infraestructura automáticamente.
  * **`src/producer/`**: 📤 **Productor.** Código fuente para simular el envío de mensajes (tweets).
  * **`src/consumer/`**: 📥 **Consumidor.** Código fuente para procesar los mensajes (Spark, etc.).
  * **`src/utils/`**: 🛠️ **Utilidades.** Funciones auxiliares y configuración.
  * **`tests/tester.py`**: 🧪 **Test.** Script de prueba para verificar la conexión con Kafka.
  * **`data/`**: 📁 **Datos.** Guarda ejemplos pequeños, dumps o logs que uses para pruebas locales.
  * **`requirements.txt`**: 📦 **Dependencias versionadas.** La lista que usamos dentro del entorno `arqesp`.
  * **`.gitignore`**: 🗑️ **Filtro.** Archivos ignorados por Git.
  * **`README.md`**: 📖 **Documentación principal.**

-----

## 🌳 Árbol de directorios

```text
AE_spark-streaming/
│
├── docker/
│   └── docker-compose.yml
├── src/
│   ├── producer/
│   ├── consumer/
│   └── utils/
├── tests/
│   └── tester.py
├── data/
├── requirements.txt
├── README.md
└── .gitignore
```

-----

## 🛠️ Requisitos Previos

Necesitas tener instalado en tu máquina:

1.  **Docker & Docker Compose**: El motor que ejecutará los servidores.
2.  **Python 3.9+**: Recomendamos usar **Anaconda/Miniconda**.
3.  **Git**: Para descargar este código.

-----

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos en orden exacto.

### 1\. Clonar el repositorio

Descarga el código a tu máquina:

```bash
git clone <URL_DEL_REPOSITORIO>
cd spark-streaming-project
```

### 2\. Preparar el entorno Python

Vamos a crear un entorno limpio para no mezclar librerías (es recomendable usar conda, pero no es necesario).

```bash
# Crear entorno llamado 'arqesp'
conda create --name arqesp python=3.9 -y

# Activar el entorno
conda activate arqesp

# Instalar las dependencias versionadas del proyecto
pip install -r requirements.txt
```

Además asegúrate de que Java 11 o 17 esté instalada y disponible en `PATH`, ya que PySpark necesita la JVM para arrancar.

### 3\. Levantar la Infraestructura (Docker)

Este comando descargará las imágenes y encenderá Zookeeper y Kafka en segundo plano.

```bash
# Si estás en Linux/Mac y requiere permisos, usa 'sudo' delante
cd docker
sudo docker compose up -d
```

*Espera unos segundos hasta que diga "Started" o "Running".*

### 4\. Crear el Canal de Comunicación (Topic)

**⚠️ IMPORTANTE:** Este paso solo es necesario hacerlo **una vez** (la primera vez que arrancas el sistema). Creamos el "buzón" donde se guardarán los tweets.

```bash
sudo docker compose exec kafka kafka-topics --create --topic tweets_topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
```

*Si sale bien, dirá: `Created topic tweets_topic`.*

-----

## ✅ Verificar que todo funciona

Para asegurarte de que tu ordenador puede hablar con el Kafka que vive dentro de Docker, hemos creado un script de prueba.

Asegúrate de tener el entorno activado (`conda activate arqesp`) y ejecuta:

```bash
python tests/tester.py
```

Si ves mensajes con **[✔] Enviado** y **[✔] Recibido**, ¡felicidades\! Tu entorno está listo para empezar a desarrollar.

-----

## ℹ️ Datos Técnicos (Para configuración)

Si necesitas configurar tus scripts (Producer o Spark), usa estos datos:

  * **Servidor Kafka (Bootstrap Server):** `localhost:9092`
  * **Nombre del Topic:** `tweets_topic`
  * **Zookeeper (Interno):** Puerto 2181

-----

## 🛑 Cómo detener todo

Cuando termines de trabajar, no dejes los contenedores consumiendo RAM. Apágalos con:

```bash
cd docker
sudo docker compose down
```

-----

*Arquitectura configurada por la Persona A.*

-----

## 🐦 Módulo: Generador de Datos (Producer)

**Estado:** ✅ Implementado por Persona B.

Este módulo sustituye a la API real de Twitter/X. Su función es generar **tráfico sintético** constante para asegurar que siempre haya datos entrando al sistema durante la demostración, evitando bloqueos por límites de API o pagos.

### 🏃🏻‍♂️ Cómo ejecutar el simulador

Una vez levantada la infraestructura (Docker), abre una terminal nueva y ejecuta:

# Desde la raíz del proyecto
python src/producer/producer.py

---------------------------------------------------------------------
INSTRUCCIONES DE VERIFICACIÓN RÁPIDA
---------------------------------------------------------------------
Si queréis comprobar que mi parte funciona sin arrancar Spark todavía:

1. Abrid una terminal en la raíz del proyecto y lanzad mi script:
   Command: python src/producer/producer.py

2. Abrid OTRA terminal para ver lo que llega a Kafka (Buzón):
   Command: docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic tweets_topic --from-beginning

NOTA: El paso 2 es solo para testear. Cuando la Persona C tenga el código de Spark listo, 
usaremos Spark para leer, no este comando de consola.