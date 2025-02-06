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
        
    def setup_plot(self):
        """Initialize the 3D plot settings"""
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title('2D Scanner Visualization (Fixed Height)')
        self.ax.view_init(elev=20, azim=45)
        
    def connect_serial(self):
        """Establish serial connection with the scanner"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1,
                write_timeout=1
            )
            print(f"Connected to {self.port}")
            time.sleep(2)  # Wait for Arduino to reset
            return True
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")
            return False
            
    def start_scan(self):
        """Send command to start the scan"""
        if hasattr(self, 'ser'):
            try:
                self.ser.write(b'\n')  # Send newline character
                self.scanning = True
                print("Scan command sent")
                # Clear any pending data
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except serial.SerialTimeoutException:
                print("Error: Write timeout")
            except serial.SerialException as e:
                print(f"Serial error: {e}")
            
    def read_data(self):
        """Read and parse data from serial port"""
        if not hasattr(self, 'ser'):
            return False
            
        try:
            if self.ser.in_waiting:  # Check if there's data available
                line = self.ser.readline().decode('utf-8').strip()
                print(f"Raw data: {line}")  # Debug print
                
                if not line:
                    return True
                    
                # Check for status messages
                if "Scanner initialized" in line or "Starting" in line:
                    print(f"Status: {line}")
                    return True
                    
                if "Scan complete" in line:
                    print("Scan completed")
                    self.scanning = False
                    return False
                    
                try:
                    # Parse CSV format (x,y,z)
                    x, y, z = map(float, line.split(','))
                    print(f"Parsed point: x={x}, y={y}, z={z}")  # Debug print
                    self.points.append([x, y, z])
                    return True
                except ValueError as e:
                    print(f"Parse error: {e} on line: {line}")
                    return True
                    
            return True
        except serial.SerialException as e:
            print(f"Serial read error: {e}")
            return False
            
    def update_plot(self, frame):
        """Update function for animation"""
        self.ax.cla()  # Clear previous points
        self.setup_plot()
        
        if self.points:
            points_array = np.array(self.points)
            scatter = self.ax.scatter(
                points_array[:, 0],
                points_array[:, 1],
                points_array[:, 2],
                c='b',  # Single color since height is fixed
                s=30  # Larger point size
            )
            
            # Update plot limits based on data
            max_range = np.array([
                points_array[:, 0].max() - points_array[:, 0].min(),
                points_array[:, 1].max() - points_array[:, 1].min(),
                points_array[:, 2].max() - points_array[:, 2].min()
            ]).max() / 2.0
            
            mid_x = (points_array[:, 0].max() + points_array[:, 0].min()) * 0.5
            mid_y = (points_array[:, 1].max() + points_array[:, 1].min()) * 0.5
            mid_z = (points_array[:, 2].max() + points_array[:, 2].min()) * 0.5
            
            self.ax.set_xlim(mid_x - max_range, mid_x + max_range)
            self.ax.set_ylim(mid_y - max_range, mid_y + max_range)
            self.ax.set_zlim(mid_z - max_range, mid_z + max_range)
            
            # Rotate view
            self.ax.view_init(elev=20, azim=frame % 360)
            
        # Continue reading data while scanning
        if self.scanning:
            self.read_data()
            
        return self.ax,
    
    def run(self):
        """Main function to run the visualization"""
        if not self.connect_serial():
            print("Failed to connect to serial port")
            return
        
        self.start_scan()
        
        # Set up animation
        anim = FuncAnimation(
            self.fig,
            self.update_plot,
            frames=range(0, 360, 2),
            interval=100,  # Slower update rate
            blit=False
        )
        
        plt.show()
        
        # Clean up
        if hasattr(self, 'ser'):
            self.ser.close()

def main():
    # Test mode for development
    def test_mode():
        visualizer = ScannerVisualizer()
        # Generate sample points for a circle
        angles_h = np.linspace(0, 2*np.pi, 72)  # 5-degree increments
        fixed_height = 100  # Fixed height value
        radius = 100  # Fixed radius
        
        for angle in angles_h:
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = fixed_height
            visualizer.points.append([x, y, z])
        
        # Run visualization
        anim = FuncAnimation(
            visualizer.fig,
            visualizer.update_plot,
            frames=range(0, 360, 2),
            interval=100,
            blit=False
        )
        plt.show()

    # Uncomment to use test mode
    # test_mode()
    
    # Use real scanner
    visualizer = ScannerVisualizer()
    visualizer.run()

if __name__ == "__main__":
    main()