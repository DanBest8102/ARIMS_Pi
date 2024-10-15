from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# Global variables
global last_command
last_command = None
status = 'R'  # Default status offline
last_g_timestamp = datetime.now()
pi_command = None  # Initialized globally to prevent undefined issues
TIMEOUT_DURATION = 15

@app.route('/')
def index():
    return render_template('ARIMS.html')

@app.route('/button_click', methods=['POST'])
def button_click():
    global last_command
    data = request.json
    last_command = data.get('command')
    print(f"Received command: {last_command}")
    return jsonify({"status": "success", "received_command": last_command})

@app.route('/get_last_command', methods=["GET"])
def get_last_command():
    global last_command
    print(f"Sending last command: {last_command}")
    return jsonify({"last_command": last_command if last_command else ""})

@app.route('/received_raspi_command', methods=['POST'])
def received_raspi_command():
    global status, last_g_timestamp, pi_command

    data = request.json
    serial_command = data.get('serial_command')
    print(f"Received serial command: {serial_command}")

    pi_command = serial_command

    if serial_command == 'G':
        status = 'G'
        last_g_timestamp = datetime.now()  # Update timestamp on 'G' command
    elif serial_command == 'R':
        status = 'R'
    else:
        status = 'R'  # Default status for unknown commands

    return jsonify({"status": "success", "received_command": serial_command})

@app.route('/get_charge_level', methods=['GET'])
def get_charge_level():
    if pi_command == 'A':
        charge_image_url = 'static/images/ARIMS_100%.png'
    elif pi_command == 'B':
        charge_image_url = 'static/images/ARIMS_75%.png'
    elif pi_command == 'C':
        charge_image_url = 'static/images/ARIMS_50%.png'
    elif pi_command == 'D':
        charge_image_url = 'static/images/ARIMS_25%.png'
    elif pi_command == 'E':
        charge_image_url = 'static/images/ARIMS_0%.png'
    else:
        charge_image_url = 'static/images/ARIMS_0%.png'  # Default case

    return jsonify({'charge_image_url': charge_image_url})

@app.route('/get_status', methods=['GET'])
def get_status():
    if status == 'R':
        image_url = 'static/images/ARIMS_offline.png'
    elif status == 'G':
        image_url = 'static/images/ARIMS_online.png'
    else:
        image_url = 'static/images/ARIMS_offline.png'  # Default to offline

    return jsonify({'image_url': image_url})

def check_status_timeout():
    global status, last_g_timestamp
    while True:
        now = datetime.now()
        if (now - last_g_timestamp) > timedelta(seconds=TIMEOUT_DURATION):
            status = 'R'  # Default to 'R' on timeout
        time.sleep(10)

threading.Thread(target=check_status_timeout, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
