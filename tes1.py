import paho.mqtt.client as mqtt
import mysql.connector
import time


mqttServer = "10.63.29.96"

db_config = {
    "host": "localhost",
    "user": "ISUZU",
    "password": "12345",
    "database": "isuzudb"
}
    
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("runTimeElapsed")
    client.subscribe("idleTimeElapsed")
    client.subscribe("downTimeElapsed")

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

    today = time.strftime("%Y-%m-%d")
    crtime = time.strftime("%H:%M:%S")

    qry = ""
    c = msg.payload.decode()

    if msg.topic == "runTimeElapsed":
        qry = "INSERT INTO mesinsatu (date, time, runTimeElapsed) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE runTimeElapsed = %s"
    elif msg.topic == "idleTimeElapsed":
        qry = "INSERT INTO mesinsatu (date, time, idleTimeElapsed) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE idleTimeElapsed = %s"
    elif msg.topic == "downTimeElapsed":
        qry = "INSERT INTO mesinsatu (date, time, downTimeElapsed) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE downTimeElapsed = %s"
    
    cursor.execute(qry, (today, crtime, c, c))
    connection.commit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttServer, 1883, 60)
client.loop_forever()
