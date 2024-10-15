import requests
import time
import serial

SERVER_URL = "http://172.20.10.11:5000/get_last_command"  # Replace <server_ip> with actual IP or hostname
POST_SERIAL_URL = "http://172.20.10.11:5000/received_raspi_command"  # URL to post serial commands

ser = serial.Serial(
    port='/dev/serial0',
    baudrate= 9600,
    timeout = 1
)
ser.flushInput()

def get_last_command(): # Get data from server
    try:
        response = requests.get(SERVER_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get('last_command')
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error connecting to server: {e}")
        return None

def send_command_over_serial(command): # Send data to arduino
    if ser.isOpen():
        print(f"Sending command over serial: {command}")
        ser.write(command.encode())
    else:
        print("Error: Serial port is not open.")

def receive_command_from_serial(): # Get data from arduino
    ser.flushInput()
    arduino_data=ser.readline().decode('utf-8')
    ser_bytes=arduino_data.rstrip()

    if ser_bytes:
        print(f"Received from arduino: {ser_bytes}")
        return ser_bytes
    return None

def post_serial_to_server(serial_command): # Send data to server
    try:
        response = requests.post(POST_SERIAL_URL, json={'serial_command': serial_command})
        if response.status_code == 200:
            print(f"Serial command '{serial_command}' posted successfully to the server>")
        else:
            print(f"Error posting serial command: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error posting serial command to server: {e}")

def main():
    print("Starting to monitor server for commands...")
    last_seen_command = None
    arduino_serial_commmand = None
    while True:
        current_command = get_last_command()
        arduino_serial_command = receive_command_from_serial()

        if current_command is not None and current_command != "" and current_command != "0":
            if current_command != last_seen_command:
                print(f"New command received: {current_command}")
                last_seen_command = current_command
                send_command_over_serial(current_command)

        if arduino_serial_command is not None and arduino_serial_command != "" and arduino_serial_command != "0":
            post_serial_to_server(arduino_serial_command)

        time.sleep(1)  # Check every second

if __name__ == "__main__":
    try:
        ser.open()
    except serial.SerialException:
        print("Serial port failed to open or is already open")
    main()
    ser.close()
    
