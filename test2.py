import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def read_points_from_file(filename='scanner_data.txt'):
    """
    Read points from scanner data file
    Returns list of measurement points
    """
    measurement_points = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            
            # Find the section with raw data
            start_reading = False
            for line in lines:
                if "=== Raw Data" in line:
                    start_reading = True
                    continue
                
                if start_reading and line.strip() and ',' in line:
                    # Parse the line: (x, y, z, vertical_angle, vertical_distance)
                    values = eval(line.strip())
                    x, y, z, vert_angle, vert_dist = values
                    
                    # Convert to required format: (distance, platform_angle, vertical_angle, height)
                    distance = np.sqrt(x*x + y*y)  # Calculate distance from x,y
                    platform_angle = np.degrees(np.arctan2(y, x))  # Calculate platform angle
                    if platform_angle < 0:
                        platform_angle += 360  # Convert to 0-360 range
                        
                    measurement_points.append((vert_dist, platform_angle, vert_angle, z))
    
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
        
    return measurement_points

def convert_to_cartesian(measurement_points):
    """
    Convert scanner measurements to cartesian coordinates
    
    Parameters:
    measurement_points: List of tuples (distance, platform_angle, vertical_angle, height)
    
    Returns:
    Array of [x, y, z] coordinates
    """
    cartesian_points = []
    
    for distance, platform_angle, vertical_angle, height in measurement_points:
        # Convert angles to radians
        platform_rad = np.radians(platform_angle)
        vertical_rad = np.radians(vertical_angle)
        
        # Calculate cartesian coordinates
        x = distance * np.cos(platform_rad)
        y = distance * np.sin(platform_rad)
        z = height  # Direct height from measurement
        
        cartesian_points.append([x, y, z])
    
    return np.array(cartesian_points)

def visualize_points(points):
    """
    Create 3D visualization of the scanned points
    
    Parameters:
    points: numpy array of [x, y, z] coordinates
    """
    # Create new figure
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot points
    ax.scatter(points[:, 0], points[:, 1], points[:, 2],
              c=points[:, 2],  # Color based on height
              cmap='viridis',
              s=100)  # Point size
    
    # Add connecting lines to show scan path
    for i in range(len(points)-1):
        ax.plot([points[i,0], points[i+1,0]],
                [points[i,1], points[i+1,1]],
                [points[i,2], points[i+1,2]],
                'gray', alpha=0.5)
    
    # Set labels
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    
    # Set title
    plt.title('3D Scanner Measurements')
    
    # Equal aspect ratio
    ax.set_box_aspect([1,1,1])
    
    # Add colorbar
    scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                        c=points[:, 2], cmap='viridis')
    plt.colorbar(scatter, label='Height (mm)')
    
    # Show plot
    plt.show()

def main():
    # Read points from file
    print("Reading points from scanner_data.txt...")
    measurement_points = read_points_from_file('scanner_data.txt')
    
    if not measurement_points:
        print("No points found in file!")
        return
        
    print(f"Found {len(measurement_points)} points")
    
    # Convert and visualize
    points = convert_to_cartesian(measurement_points)
    visualize_points(points)
    
    # Print first few coordinates for verification
    print("\nFirst 5 Cartesian Coordinates (x, y, z):")
    for i, point in enumerate(points[:5]):
        print(f"Point {i+1}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")

if __name__ == "__main__":
    main()