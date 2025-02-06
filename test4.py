import serial
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import time

class ScannerVisualizer:
    def __init__(self, port='COM3', baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.points = []
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.setup_plot()
        self.scanning = False
        self.initialization_complete = False
        
    def setup_plot(self):
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title('2D Scanner Visualization (Fixed Height)')
        self.ax.view_init(elev=20, azim=45)
        
    def connect_serial(self):
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1,
                write_timeout=1
            )
            print(f"Connected to {self.port}")
            time.sleep(2)
            return True
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")
            return False
            
    def start_scan(self):
        if hasattr(self, 'ser'):
            try:
                self.ser.write(b'\n')
                self.scanning = True
                print("Scan command sent")
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except Exception as e:
                print(f"Error starting scan: {e}")
            
    def read_data(self):
        if not hasattr(self, 'ser'):
            return False
            
        try:
            if self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8').strip()
                print(f"Debug: {line}")  # Print all incoming data
                
                # Check for initialization messages
                if any(msg in line for msg in ["initialized", "configured", "detected", "starting", "ready", "Failed"]):
                    if "Failed" in line:
                        print(f"Error: {line}")
                        self.scanning = False
                        return False
                    print(f"Status: {line}")
                    return True
                
                # Check for scan completion
                if "Scan complete" in line:
                    print("Scan completed")
                    self.scanning = False
                    return False
                
                # Try to parse coordinate data
                try:
                    # Only try to parse if the line contains two commas (x,y,z format)
                    if line.count(',') == 2:
                        x, y, z = map(float, line.split(','))
                        print(f"Point data: x={x}, y={y}, z={z}")
                        self.points.append([x, y, z])
                except ValueError:
                    # Not coordinate data, ignore parsing error
                    pass
                    
            return True
        except serial.SerialException as e:
            print(f"Serial read error: {e}")
            return False
            
    def update_plot(self, frame):
        self.ax.cla()
        self.setup_plot()
        
        if self.points:
            points_array = np.array(self.points)
            scatter = self.ax.scatter(
                points_array[:, 0],
                points_array[:, 1],
                points_array[:, 2],
                c='b',
                s=30
            )
            
            # Update plot limits
            if len(points_array) > 0:  # Check if we have any points
                max_range = np.array([
                    points_array[:, 0].max() - points_array[:, 0].min(),
                    points_array[:, 1].max() - points_array[:, 1].min(),
                    points_array[:, 2].max() - points_array[:, 2].min()
                ]).max() / 2.0
                
                if max_range > 0:  # Prevent division by zero
                    mid_x = (points_array[:, 0].max() + points_array[:, 0].min()) * 0.5
                    mid_y = (points_array[:, 1].max() + points_array[:, 1].min()) * 0.5
                    mid_z = (points_array[:, 2].max() + points_array[:, 2].min()) * 0.5
                    
                    self.ax.set_xlim(mid_x - max_range, mid_x + max_range)
                    self.ax.set_ylim(mid_y - max_range, mid_y + max_range)
                    self.ax.set_zlim(mid_z - max_range, mid_z + max_range)
            
            self.ax.view_init(elev=20, azim=frame % 360)
            
        if self.scanning:
            self.read_data()
            
        return self.ax,
    
    def run(self):
        if not self.connect_serial():
            print("Failed to connect to serial port")
            return
        
        time.sleep(1)  # Wait for Arduino to initialize
        self.start_scan()
        
        anim = FuncAnimation(
            self.fig,
            self.update_plot,
            frames=range(0, 360, 2),
            interval=100,
            blit=False
        )
        
        plt.show()
        
        if hasattr(self, 'ser'):
            self.ser.close()

if __name__ == "__main__":
    visualizer = ScannerVisualizer()
    visualizer.run()