import paho.mqtt.client as mqtt
import mysql.connector

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
    client.subscribe("R01/ON")
    client.subscribe("R02/ON")
    client.subscribe("R12/OFF")

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

    qry = ""
    c = msg.payload.decode()

    if msg.topic == "R01/ON":
        if c == "true":
            qry = "INSERT INTO fanuc (date, start_time, status) VALUES (CURDATE(), CURTIME(), 'RUNNING')"
        else:
            qry = "UPDATE fanuc SET end_time = CURTIME(), duration = TIMEDIFF(CURTIME(), start_time) WHERE duration is NULL AND status = 'RUNNING'"
    elif msg.topic == "R02/ON":
        if c == "true":
            qry = "INSERT INTO fanuc (date, start_time, status) VALUES (CURDATE(), CURTIME(), 'DOWN')"
        else:
            qry = "UPDATE fanuc SET end_time = CURTIME(), duration = TIMEDIFF(CURTIME(), start_time) WHERE duration is NULL AND status = 'DOWN'"
    elif msg.topic == "R12/OFF":
        if c == "true":
            qry = "INSERT INTO fanuc (date, start_time, status) VALUES (CURDATE(), CURTIME(), 'IDLE')"
        else:
            qry = "UPDATE fanuc SET end_time = CURTIME(), duration = TIMEDIFF(CURTIME(), start_time) WHERE duration is NULL AND status = 'IDLE'"
    
    cursor.execute(qry)
    connection.commit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttServer, 1883, 0)
client.loop_forever()
