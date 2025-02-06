import serial
import time
import json
import numpy as np

def setup_serial_connection(port='COM3', baud_rate=115200):
    """
    Setup serial connection with the ESP32
    Returns serial object if successful
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to {port} at {baud_rate} baud")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def read_serial_data(ser):
    """
    Read and parse data from serial port
    Returns list of measurement points
    """
    measurement_points = []
    try:
        while True:  # Continue reading until stopped
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                
                # Check if line contains valid data
                if line:
                    try:
                        # Assuming data format is "distance,platform_angle,vertical_angle,height"
                        values = line.split(',')
                        if len(values) == 4:
                            distance = float(values[0])
                            platform_angle = float(values[1])
                            vertical_angle = float(values[2])
                            height = float(values[3])
                            
                            point = (distance, platform_angle, vertical_angle, height)
                            measurement_points.append(point)
                            
                            # Print the received point
                            print(f"Received: Distance={distance}mm, "
                                  f"Platform={platform_angle}°, "
                                  f"Vertical={vertical_angle}°, "
                                  f"Height={height}mm")
                    
                    except ValueError as e:
                        print(f"Error parsing line: {line}")
                        print(f"Error details: {e}")
                        continue
                    
            # Small delay to prevent CPU overload
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nStopped reading data")
        return measurement_points

def save_measurements(points, filename='scanner_data.txt'):
    """
    Save measurement points to a file
    """
    with open(filename, 'w') as f:
        f.write("distance,platform_angle,vertical_angle,height\n")
        for point in points:
            f.write(f"{point[0]},{point[1]},{point[2]},{point[3]}\n")
    print(f"Data saved to {filename}")

def main():
    # Setup serial connection
    ser = setup_serial_connection()
    if not ser:
        return
    
    try:
        # Read data until keyboard interrupt
        print("Reading data... Press Ctrl+C to stop")
        measurement_points = read_serial_data(ser)
        
        # Save data
        if measurement_points:
            save_measurements(measurement_points)
            print(f"Collected {len(measurement_points)} points")
        
    finally:
        # Clean up
        ser.close()
        print("Serial connection closed")

if __name__ == "__main__":
    main()