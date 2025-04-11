import cv2
import socket
import pickle
import struct
import json
import numpy as np

def load_transform_params(json_path):
    # we open the json file and read the parameters from it
    with open(json_path, 'r') as f:
        params = json.load(f)
    
    return params


def apply_transform(frame, transform_params):
    """Apply rotation and cropping with precise boundary checking."""

    # Get frame dimensions
    frame_height, frame_width = frame.shape[:2]
    
    # Extract parameters from JSON
    alpha = transform_params.get('alpha', 0)  # Rotation angle in degrees
    ox = transform_params.get('ox', 0.5)      # Normalized center x-coordinate
    oy = transform_params.get('oy', 0.5)      # Normalized center y-coordinate
    crop_width = transform_params.get('width', 1.0)  # Normalized width
    crop_height = transform_params.get('height', 1.0)  # Normalized height
    
    # Convert normalized coordinates to absolute pixel values
    center_x = int(ox * frame_width)
    center_y = int(oy * frame_height)
    crop_w_pixels = int(crop_width * frame_width)
    crop_h_pixels = int(crop_height * frame_height)
   
    # Calculate the coordinates of the four corners of the crop rectangle (before rotation)
    half_width = crop_w_pixels / 2
    half_height = crop_h_pixels / 2
  
    # Corners relative to center (top-left, top-right, bottom-right, bottom-left)
    corners_rel = [
        (-half_width, -half_height),
        (half_width, -half_height),
        (half_width, half_height),
        (-half_width, half_height)
    ]
 
    # Convert rotation angle to radians for calculation
    angle_rad = np.radians(alpha)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    # Check if any corner would fall outside the frame after rotation
    corners_rotated = []
    outside_frame = False
    
    for dx, dy in corners_rel:
        # Rotate the corner around center
        # Rotation matrix: [cos(a) -sin(a); sin(a) cos(a)]
        rotated_dx = dx * cos_a - dy * sin_a
        rotated_dy = dx * sin_a + dy * cos_a
        
        # Calculate absolute position
        abs_x = center_x + rotated_dx
        abs_y = center_y + rotated_dy
        
        corners_rotated.append((abs_x, abs_y))
        
        # Check if this corner is outside the frame
        if abs_x < 0 or abs_x >= frame_width or abs_y < 0 or abs_y >= frame_height:
            outside_frame = True
    
    # If any corner is outside, find the scaling factor needed
    scale_factor = 1.0
    
    if outside_frame:
        # Calculate how much each corner exceeds the frame
        scale_factors = []
        
        for corner_x, corner_y in corners_rotated:
            # Calculate how much this corner needs to be scaled
            if corner_x < 0:
                # Left boundary exceeded
                scale_x = center_x / (center_x - corner_x)
                scale_factors.append(scale_x)
            elif corner_x >= frame_width:
                # Right boundary exceeded
                scale_x = (frame_width - center_x) / (corner_x - center_x)
                scale_factors.append(scale_x)
                
            if corner_y < 0:
                # Top boundary exceeded
                scale_y = center_y / (center_y - corner_y)
                scale_factors.append(scale_y)
            elif corner_y >= frame_height:
                # Bottom boundary exceeded
                scale_y = (frame_height - center_y) / (corner_y - center_y)
                scale_factors.append(scale_y)
        
        # Use the smallest scale factor to ensure all corners are inside
        if scale_factors:
            scale_factor = min(scale_factors)
            
            # Apply scaling to the crop dimensions
            crop_w_pixels = int(crop_w_pixels * scale_factor)
            crop_h_pixels = int(crop_h_pixels * scale_factor)
  
    # Apply rotation to the frame
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), alpha, 1)
    rotated_frame = cv2.warpAffine(frame, rotation_matrix, (frame_width, frame_height))
    
    # Calculate the final crop coordinates based on center and dimensions
    half_width = crop_w_pixels // 2
    half_height = crop_h_pixels // 2
    
    x1 = max(0, center_x - half_width)
    y1 = max(0, center_y - half_height)
    x2 = min(frame_width, center_x + half_width)
    y2 = min(frame_height, center_y + half_height)
    
    # Apply cropping to the rotated frame
    cropped_frame = rotated_frame[y1:y2, x1:x2]
    
    return cropped_frame


def start_video_receiver(transform_json_path, host_ip='0.0.0.0', port=9999):
    """Start a video receiver that listens for frames and applies transformations."""
    # Load transformation parameters
    transform_params = load_transform_params(transform_json_path)
    
    # Set up socket server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host_ip, port))
    server_socket.listen(5)
    
    print(f"Listening for connections on {host_ip}:{port}")
    
    # Accept a client connection
    client_socket, addr = server_socket.accept()
    print(f"Connection established with {addr}")
    
    # Variable to store the frame size
    data_size = struct.calcsize("L")
    data = b""
    
    try:
        while True:
            # Retrieve the message size
            while len(data) < data_size:
                packet = client_socket.recv(4096)
                if not packet:
                    break
                data += packet
            
            if not data:
                break
                
            # Extract the frame size
            packed_msg_size = data[:data_size]
            data = data[data_size:]
            msg_size = struct.unpack("L", packed_msg_size)[0]
            
            # Retrieve the frame data
            while len(data) < msg_size:
                data += client_socket.recv(4096)
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            # Deserialize the frame
            frame = pickle.loads(frame_data)
            
            # Apply transformations
            processed_frame = apply_transform(frame, transform_params)
            
            # Display the received and processed frames
            cv2.imshow('Received Frame', frame)
            cv2.imshow('Processed Frame', processed_frame)
            
            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Stopping video receiver")
    finally:
        # Clean up used resources
        client_socket.close()
        server_socket.close()
        cv2.destroyAllWindows()
        print("Resources released")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Receive and process video frames')
    parser.add_argument('--json', type=str, required=True,
                        help='Path to the JSON file with transformation parameters')
    parser.add_argument('--ip', type=str, default='0.0.0.0',
                        help='IP address to listen on')
    parser.add_argument('--port', type=int, default=9999,
                        help='Port number to listen on')
    
    args = parser.parse_args()
    
    start_video_receiver(args.json, args.ip, args.port)