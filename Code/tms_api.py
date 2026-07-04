from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
import asyncio
import websockets
import json

# Initialize Firebase Admin SDK
cred = credentials.Certificate('keys/firebase_key.json')
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

app = Flask(__name__)
CORS(app)

# WebSocket server address
WEBSOCKET_SERVER = 'ws://localhost:8765'

async def send_websocket_message(message):
    async with websockets.connect(WEBSOCKET_SERVER) as websocket:
        await websocket.send(json.dumps(message))  # Serialize message to JSON string
        response = await websocket.recv()
        return response

def send_message_to_websocket(message):
    return asyncio.run(send_websocket_message(message))

@app.route('/', methods=['GET'])
def view_lights():
    try:
        lights = db.collection('Traffic Lights').get()
        lights_dict = [light.to_dict() for light in lights]
        return jsonify(lights_dict)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/', methods=['POST'])
def add_light():
    try:
        data = request.get_json()
        db.collection('Traffic Lights').add(data)
        return jsonify({'message': 'Traffic light added successfully'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/traffic_phase/<string:light_id>', methods=['PUT'])
def update_light(light_id):
    try:
        data = request.get_json()
        db.collection('Traffic Lights').document(light_id).update(data)

        message = {
            'action': 'update_light',
            'light_id': light_id,
            'phase_index': data.get('phase_index')
        }
        response = send_message_to_websocket(message)
        print(response)  # Log the response for debugging

        return jsonify({'message': 'Traffic light phase updated successfully', 'response': response})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/connect_sumo', methods=['GET'])
def connect_sumo():
    try:
        message = {
            'action': 'connect_sumo'
        }
        response = send_message_to_websocket(message)
        print(response)  # Log the response for debugging
        return jsonify({'message': 'Connected to SUMO', 'response': response})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/sumo_step', methods=['GET'])
def sumo_step():
    try:
        message = {
            'action': 'sumo_step'
        }
        response = send_message_to_websocket(message)
        print(response)  # Log the response for debugging
        return jsonify({'message': 'SUMO stepped', 'response': response})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/disconnect_sumo', methods=['GET'])
def disconnect_sumo():
    try:
        message = {
            'action': 'disconnect_sumo'
        }
        response = send_message_to_websocket(message)
        print(response)  # Log the response for debugging
        return jsonify({'message': 'Disconnected from SUMO', 'response': response})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/change_phase', methods=['POST'])
def change_phase():
    data = request.get_json()
    print(data)
    try:    
        message = {
            'action': 'change_phase',
            'junction_id': data['junction_id'],
            'phase': data['phase']
        }
        response = send_message_to_websocket(message)
        print(response)  # Log the response for debugging
        return jsonify({'message': 'Test', 'response': response})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
