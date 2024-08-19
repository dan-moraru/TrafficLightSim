import time
import requests
from threading import Thread
import random  
import datetime
import os
import json
import base64 
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# publisher class- requests from Apis, takes a picture and publishes
class Publisher:
    def __init__(self, delay=0.5):
        self.time_to_sleep = delay
    
    # uses in detection thread 
    def detectMotions(self, redLight_on, end_program, picam2, token, client, private_key):
        while True:
            time.sleep(self.time_to_sleep)
            if end_program.is_set():
                return
            # Convert token to string if it's bytes
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            # Define the URL 
            endpoint_url = 'http://localhost:5227/MotionCollisionDetection/M9A1A8?token='+ token


            try:
                #  # Generate a random integer between 1 and 5 for every 3 cars only 1
                # for more time and randomizing
                random_number = random.randint(1, 3)
                        
                if random_number == 1:
                    # Make a GET request to the endpoint
                    response = requests.get(endpoint_url)

                    # Check if the response status code is 200 (OK)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('detection').get('value') is True:
                            # validate that detection is either collision or motion on relight
                            if data.get('detection').get('type') == 'motion' and redLight_on.is_set():
                                publishThread = Thread(target=Publisher.publish, args=(self, data, picam2, token, client, private_key))
                                publishThread.start()
                                publishThread.join()
                            elif data.get('detection').get('type') == 'collision':
                                publishThread = Thread(target=Publisher.publish, args=(self, data, picam2, token, client, private_key))
                                publishThread.start()
                                publishThread.join()
                                
                    else:
                        print("Request failed with status code:", response)
            except requests.exceptions.RequestException as e:
                print("Request failed with an exception:", str(e))

    # used in publishing thread            
    def publish(self, dataDetection, picam2, token, client, private_key):
        print(dataDetection)
        # get weather from api
        # Convert token to string if it's bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        # Define the URL 
        endpoint_url = 'http://localhost:5226/WeatherForecast/M9A1A8?token='+ token
        try:
                # Make a GET request to the endpoint
                response = requests.get(endpoint_url)
                 # Check if the response status code is 200 (OK)
                if response.status_code == 200:
                    # with this data weather and detection and camera we publish
                    dataWeather = response.json()
                    # capture photo
                    print(dataWeather)
                    
                    os.makedirs("captured", exist_ok = True)
                    timestamp= datetime.datetime.now()
                    photopath= "captured/" + "car_at_" + str(timestamp)
                    picam2.capture_file(photopath+".jpg")
                    
                    # Read the captured image as bytes and encode as base64
                    with open(photopath + ".jpg", "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode('utf-8')

                    # Create a message with detection data, weather data, and the base64-encoded image
                    message = {
                        'detection': dataDetection,
                        'weather': dataWeather,
                        'image': image_data
                    }
                    # Convert the message to JSON and then encode it to bytes
                    message_json = json.dumps(message).encode('utf-8')
                    # Sign the encoded message
                    signature = self.sign(message_json, private_key)
                    # Create a topicObject with the signature and the original message
                    topic_object = {
                        'signature': signature.hex(),
                        'message': message
                    }
                    client.publish(topic="TrafficLight", payload=json.dumps(topic_object))

        except requests.exceptions.RequestException as e:
                print("Request failed with an exception:", str(e))
                    
    def sign(self, message, private_key):
            return private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
    
        

    