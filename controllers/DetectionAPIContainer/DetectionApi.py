from flask import Flask, jsonify, request
import random
import jwt

import datetime

app = Flask(__name__)

Postal_codes = [
    "A4L5J3", "M9A1A8", "D8F3ZR", "PU6J9W", "Z2E4F9"
]

# validation for token
SECRET = "my-secret"
def validate_token(token):
    try:
        # Convert the token string to bytes
        token_bytes = token.encode('utf-8')
        decoded = jwt.decode(token_bytes, SECRET, verify=True, algorithms=["HS256"])
        if datetime.datetime.utcnow().timestamp() > decoded["exp"]:
            return None
        return decoded
    except:
        return None
    
@app.route('/MotionCollisionDetection/<postal_code>', methods=['GET'])
def get_motion_collision_detection(postal_code):
    token = request.args.get('token')
    # Validate the token
    if not token:
        return "Token is missing", 401
    validated_payload = validate_token(token)
    if not validated_payload :
        return "Invalid token", 401
    
    if not isinstance(postal_code, str) or not postal_code in Postal_codes:
        return "Invalid Postal Code", 400
    
    detection_type = random.choice(["motion", "collision"])
    detection_value = random.choice([True, False])
    current_datetime = datetime.datetime.now().isoformat()

    detection = {
        'postal_code': postal_code,
        'detection': {
            'type': detection_type,
            'value': detection_value
        },
        'datetime': current_datetime
    }

    return jsonify(detection), 200

@app.errorhandler(404)
def not_found(e):
    return "Could not find what you are looking for", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5227)
