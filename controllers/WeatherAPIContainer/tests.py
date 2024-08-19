import unittest
from flask import json
from WeatherApi import app
import jwt
import datetime

# Helper methods
SECRET = "my-secret"

def authenticate(username, password):
    if username == "admin" and password == "password":
        expire_on = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        payload = {"sub": "admin", "exp": expire_on.timestamp()}
        token = jwt.encode(payload, SECRET, algorithm="HS256")
        return token
    else:
        return None
    
def decode(valid_token):
    decoded = jwt.decode(valid_token, SECRET, verify=True, algorithms=["HS256"])
    return decoded

class WeatherApiTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_get_weather_forecast_valid(self):
        
        token = authenticate("admin", "password")
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        response = self.app.get('/WeatherForecast/A4L5J3?token=' + token)
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('postal_code', data)
        self.assertIn('temperature', data)
        self.assertIn('condition', data)
        self.assertIn('type', data['condition'])
        self.assertIn('intensity', data['condition'])
        self.assertIn('date', data)

    def test_get_weather_forecast_invalid_token(self):
        
        expire_on = datetime.datetime.utcnow() + datetime.timedelta(seconds=0)
        payload = {"sub": "admin", "exp": expire_on.timestamp()}
        token = jwt.encode(payload, SECRET, algorithm="HS256")

        if isinstance(token, bytes):
            token = token.decode('utf-8')

        response = self.app.get('/WeatherForecast/A4L5J3?token=' + token)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_data(as_text=True), "Invalid token")

    def test_get_weather_forecast_invalid_postal_code(self):
        
        token = authenticate("admin", "password")
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        response = self.app.get('/WeatherForecast/INVALID?token=' + token)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_data(as_text=True), "Invalid Postal Code")

    def test_not_found(self):
        
        response = self.app.get('/nonexistentroute')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_data(as_text=True), "Could not find what you are looking for")

if __name__ == '__main__':
    unittest.main()
