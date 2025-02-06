import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

# Your measurement points
measurement_points = [
    # Format: (distance, platform_angle, vertical_angle, height)
    (80, 0, 0, 0),    # Bottom level, front
    (80, 90, 0, 50),  # Middle level, side
    (80, 180, 0, 100),# Top level, back
    (80, 270, 0, 150) # Top level, other side
]

# Convert and visualize
points = convert_to_cartesian(measurement_points)
visualize_points(points)

# Print coordinates for verification
print("\nCartesian Coordinates (x, y, z):")
for i, point in enumerate(points):
    print(f"Point {i+1}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")