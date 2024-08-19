## this publishes to broker 
import datetime
import json
import paho.mqtt.client as mqtt
import time
from threading import Event, Thread

import jwt
from picamera2 import Picamera2

from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa  
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature 

end_program = Event()
Redlight_on = Event()
broker_hostname = "localhost"
port = 1883 

picam2 = Picamera2()

# connect to broker
def on_connect(client, userdata, flags, return_code):
    print("CONNACK received with code %s." % return_code)
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)

client = mqtt.Client(client_id="Client1", userdata=None)
topic = "TrafficLight"
msg_count = 0

def setup():
    client.on_connect = on_connect
    # # change with your user and password auth
    # authentication for broker
    client.username_pw_set(username="trafficLight", password="password")
    client.connect(broker_hostname, port, 60)
    #client.loop_forever()
    client.loop_start()
    
    #for camera
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()
   
def main():
    from LightTimer import LightTimer
    from Publisher import Publisher
    
    end_program.clear()
    # token AUTHENTICATION
    # recieve token if successful good
    while True:
       # Get username and password from the user
        username = input("Enter username: ")
        password = input("Enter password: ")

        # Authenticate the user
        global token
        token = authenticate(username, password)

        if token:
            print("Authentication successful")
            break
        else:
            print("Authentication failed. Please try again.")
    
    # keys extraction 
    # extract public key and send to dashboard and private key and sign messages
    public_key, private_key = extract_keys()
    # Serialize the public key to bytes
    serialized_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # Convert bytes to string and send public key to dashboard
    serialized_public_key_str = serialized_public_key.decode('utf-8')
    client.publish(topic="KeysVerification", payload=json.dumps(serialized_public_key_str))

    # start light and publishing threads
    redLightSensor = LightTimer(3)
    redLightSensorThread = Thread(target=redLightSensor.lightChanger, args=(Redlight_on, end_program ))
    publisher = Publisher(1)
    publisherThread = Thread(target=publisher.detectMotions, args=(Redlight_on, end_program, picam2, token, client, private_key ))
    
    redLightSensorThread.start()
    publisherThread.start()
    redLightSensorThread.join()
    publisherThread.join()
        
def destroy():
    end_program.set()
    client.loop_stop()
    print("Program finished...")
    
# JWT Authorization method
SECRET = "my-secret"
def authenticate(username, password):
    if username == "admin" and password == "password":
        # Create a JWT token with a subject claim "admin" and an expiration time of 1 hour
        expire_on = datetime.datetime.utcnow() + datetime.timedelta(days=100)
        payload = {"sub": "admin", "exp": expire_on.timestamp()}
        token = jwt.encode(payload, SECRET, algorithm="HS256")
        return token
    else:
        return None  

# Extraction of keys from pem file method
def extract_keys():
    private_pem_bytes = Path("Keys/key.pem").read_bytes()
    public_pem_bytes = Path("Keys/public.pem").read_bytes()
    private_key = serialization.load_pem_private_key(
        private_pem_bytes,
        password = b"my secret",
    )
    public_key = serialization.load_pem_public_key(public_pem_bytes)
    return public_key, private_key
    
# Program entrance
if __name__ == '__main__':     
    print ('Program is starting ... ')
    setup()
    try:
        main()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()
