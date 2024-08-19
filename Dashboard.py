## this subscribes to topic and showcases data 
import datetime
import json
import paho.mqtt.client as mqtt
from threading import Event

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature 

from dash import Dash, html, dcc, Input, Output
import dash_daq as daq
import datetime

topic = "TrafficLight"
topic_keys = "KeysVerification"
msg_count = 0
end_program = Event()
client = mqtt.Client("Client2")
broker_hostname = "10.172.19.253"
port = 1883
app = Dash(__name__)

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("client subscribed to various topicss")
        # subsribes to topics
        client.subscribe(topic_keys)
        client.subscribe(topic)
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode("utf-8"))
    if message.topic == topic_keys:
        # get public key
        serialized_public_key_str = payload
        serialized_public_key = serialized_public_key_str.encode('utf-8')
        
        global public_key
        public_key = serialization.load_pem_public_key(serialized_public_key)


        print("Received public key:", public_key)
        # Unsubscribe from KeysVerification topic
        client.unsubscribe(topic_keys)
        print("Unsubscribed from topic: " + topic_keys)
    try:
        if message.topic == topic and public_key:
            # Handle message for TrafficLight topic
            print("topic message recieved from topic: " + topic)
            # verify signature
            signature_hex = payload.get("signature")
            message_to_verify = json.dumps(payload.get("message"))
            # Convert the hex-encoded signature to bytes
            signature = bytes.fromhex(signature_hex)
            # Verify the signature with the public key
            if verify(signature, message_to_verify.encode('utf-8'), public_key):
                print("Signature verified successfully")
                # Update globalData based on incoming MQTT message
                global globalData
                globalData = json.loads(message_to_verify)
            else:
                print("Signature verified FAILED")
    except:
        # in case public key was never passed
        print("public key not defined for any messages to be validated")

# Dash layout
app.layout = html.Div(
    style={'background-color': 'black', 'text-align': 'center', 'padding': '10%', 
           'color': 'white'},
    children=[
        html.H1(id='dateTitle'),
        html.P(id='postalCode'),
        html.P(id='intensity-and-type'),
        html.P(id='collisionStatus'),
        html.P(id='temperature'),
        daq.Thermometer(
            id='my-thermometer',
            value=0,
            min=-40,
            max=40,
            style={'margin-top': '5%', 'backgroundColor': 'white', 'padding': '5%'},
            color='red',   
            height=150,
            width=5
        ),
        html.Img(id="image", src="", width="200px", style={'margin-top': '5%'}),
        dcc.Interval(
            id='interval-component',
            interval=1000,  # in milliseconds
            n_intervals=0
        )
    ]
)

# Callbacks to update the UI based on incoming MQTT messages
@app.callback(
    Output('dateTitle', 'children'),
    Output('postalCode', 'children'),
    Output('intensity-and-type', 'children'),
    Output('collisionStatus', 'children'),
    Output('temperature', 'children'),
    Output('my-thermometer', 'value'),
    Output('image', 'src'),
    Input('interval-component', 'n_intervals')
)
def update_layout(n_intervals):
    if 'globalData' not in globals():
        # If globalData is not initialized yet, return placeholder values
        return 'waiting for data...', '', '', '', '', 0, ''

    date_string = globalData.get('weather', {}).get('date', '')
    date_title = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
    postalCode = globalData.get('weather', {}).get('postal_code', '')
    intenseAndType = f'{globalData.get("weather", {}).get("condition", {}).get("intensity", "")}, {globalData.get("weather", {}).get("condition", {}).get("type", "")}'
    collision_status = '🚗 Collision detected' if globalData.get('detection', {}).get('detection', {}).get('type', '') == 'collision' else '🚦 Motion detected at red light'
    temperature = f'Temperature: {globalData.get("weather", {}).get("temperature", 0)} °C'
    thermometer_value = globalData.get('weather', {}).get('temperature', 0)
    image_data = "data:image/png;base64, " + globalData.get('image', '')

    return date_title, postalCode, intenseAndType, collision_status, temperature, thermometer_value, image_data
        
def setup():
    client.username_pw_set(username="trafficLight", password="password")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, port)
    client.loop_start()
        
def destroy():
    end_program.set()
    client.loop_stop()
    print("Program finished...")

def verify(signature, message, public_key):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

# Program entrance
if __name__ == '__main__': 
    # run setup to subscribe to topics before starting
    setup()    
    print ('Program is starting ... ')
    try:
        app.run(debug=False, host='0.0.0.0')
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()