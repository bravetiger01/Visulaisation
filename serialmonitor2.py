import serial
import time
from collections import defaultdict

def connect_to_esp32(port='COM3', baud_rate=115200):
    """
    Establish connection with ESP32
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to ESP32 on {port}")
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to ESP32: {e}")
        return None

def is_valid_data_line(line):
    """
    Check if the line contains valid scanner data
    """
    # Skip known boot messages and empty lines
    boot_messages = [
        "SPIWP:", "clk_drv:", "mode:", "load:",
        "Scanner initialized", "Starting full 3D scan",
        "Scanning at vertical angle"
    ]
    
    for msg in boot_messages:
        if msg in line:
            return False
            
    # Check if line contains expected number of values
    try:
        values = line.split(',')
        if len(values) == 5:  # x,y,z,vertical_angle,vertical_distance
            # Try converting values to float
            [float(v) for v in values]
            return True
    except:
        return False
        
    return False

def read_scanner_data(ser):
    """
    Read and parse data from ESP32
    """
    points_list = []
    points_by_angle = defaultdict(list)
    raw_data = []
    
    print("Waiting for scanner data... (Send 'S' to start scan)")
    print("Press Ctrl+C to stop")
    
    # Send 'S' command to start scan
    ser.write(b'S')
    
    try:
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                
                # Skip invalid lines
                if not line or not is_valid_data_line(line):
                    # Print important status messages
                    if "Starting full 3D scan" in line:
                        print("\nScan started...")
                    elif "Scan complete!" in line:
                        print("\nScan completed!")
                    elif "Scanning at vertical angle" in line:
                        print(f"\n{line}")
                    continue
                
                try:
                    # Parse the comma-separated values
                    x, y, z, vert_angle, vert_dist = map(float, line.split(','))
                    
                    # Store data
                    point_3d = (x, y, z)
                    points_list.append(point_3d)
                    points_by_angle[vert_angle].append(point_3d)
                    raw_data.append((x, y, z, vert_angle, vert_dist))
                    
                    # Print point in a clean format
                    print(f"Point captured: ({x:.1f}, {y:.1f}, {z:.1f}) at {vert_angle}°")
                    
                except ValueError as e:
                    continue
                    
    except KeyboardInterrupt:
        print("\nData collection stopped")
    
    return points_list, points_by_angle, raw_data

def save_data_to_file(points_list, points_by_angle, raw_data, filename='scanner_data.txt'):
    """
    Save collected data to a file
    """
    with open(filename, 'w') as f:
        f.write("=== 3D Points (x, y, z) ===\n")
        for point in points_list:
            f.write(f"{point}\n")
        
        f.write("\n=== Points by Vertical Angle ===\n")
        for angle in sorted(points_by_angle.keys()):
            f.write(f"\nAngle {angle}°:\n")
            for point in points_by_angle[angle]:
                f.write(f"{point}\n")
        
        f.write("\n=== Raw Data (x, y, z, vertical_angle, vertical_distance) ===\n")
        for data in raw_data:
            f.write(f"{data}\n")
    
    print(f"\nData saved to {filename}")

def main():
    # Connect to ESP32
    ser = connect_to_esp32()
    if not ser:
        return
    
    try:
        # Read data
        points_list, points_by_angle, raw_data = read_scanner_data(ser)
        
        if points_list:
            # Print summary 
            print(f"\nTotal points collected: {len(points_list)}")
            print(f"Vertical angles recorded: {sorted(points_by_angle.keys())}")
            
            # Save data
            save_data_to_file(points_list, points_by_angle, raw_data)
            
            # Print sample of collected data
            if len(points_list) > 0:
                print("\nSample of collected points:")
                for point in points_list[:3]:
                    print(f"({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")
        else:
            print("\nNo valid data points were collected")
        
    finally:
        ser.close()
        print("\nSerial connection closed")

if __name__ == "__main__":
    main()