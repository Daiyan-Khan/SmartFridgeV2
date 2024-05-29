import threading
import time
from flask import Flask, send_file, jsonify, render_template
from flask_socketio import SocketIO, emit
import fridge_camera
import sensor
import servo_motor

app = Flask(__name__)
socketio = SocketIO(app)

servo = servo_motor.ServoMotor()
servo.center_camera()
# Global variable to store the latest sensor values
latest_sensor_values = {
    "temperature1": None,
    "humidity1": None,
    "temperature2": None,
    "humidity2": None
}

@app.route('/capture')
def capture():
    try:
        # Capture image
        fridge_camera.capture_image()
        return jsonify({'image': '/fridge_image.jpg'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fridge_image.jpg')
def get_image():
    return send_file('/home/danny/SmartFridge/fridge_image.jpg', mimetype='image/jpeg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/turn_left', methods=['POST'])
def turn_left():
    try:
        print("Received request to turn left")
        servo.turn_left()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error turning left: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/turn_right', methods=['POST'])
def turn_right():
    try:
        print("Received request to turn right")
        servo.turn_right()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error turning right: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/center_camera', methods=['POST'])
def center_camera():
    try:
        print("Received request to center camera")
        servo.center_camera()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error centering camera: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/refresh_sensor_data', methods=['POST'])
def refresh_sensor_data():
    try:
        latest_data = sensor.get_sensor_data("D4:D4:DA:4E:FC:9E")  # Function to get latest sensor data
        if latest_data:
            global latest_sensor_values
            latest_sensor_values = latest_data
            socketio.emit('sensor_update', {'sensor_data': latest_sensor_values})
            return jsonify({'status': 'success', 'sensor_data': latest_sensor_values})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to get sensor data'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def background_sensor_update():
    while True:
        try:
            latest_data = sensor.get_sensor_data("D4:D4:DA:4E:FC:9E")  # Function to get latest sensor data
            if latest_data:
                global latest_sensor_values
                latest_sensor_values = latest_data
                socketio.emit('sensor_update', {'sensor_data': latest_sensor_values})
            time.sleep(10)  # Update every 10 seconds
        except Exception as e:
            print(f"Error in background sensor update: {e}")

@socketio.on('connect')
def handle_connect():
    emit('sensor_update_response', {'sensor_data': latest_sensor_values})

if __name__ == "__main__":
    try:
        
        # Start the background thread to update sensor values
        sensor_thread = threading.Thread(target=background_sensor_update)
        sensor_thread.daemon = True
        sensor_thread.start()
        socketio.run(app, host='0.0.0.0', port=5000)
    finally:
        servo.cleanup()
        print("Exit")
