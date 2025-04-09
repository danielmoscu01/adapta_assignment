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

# def apply_transform(frame, transform_params):
#     """Apply rotation and cropping based on custom parameters."""
#     # Get frame dimensions
#     h, w = frame.shape[:2]
    
#     # Extract parameters from the json file and use some default values in case one is not given
#     alpha = transform_params.get('alpha', 0)  # Rotation angle in degrees
#     ox = transform_params.get('ox', 0.5)      # Normalized center x-coordinate
#     oy = transform_params.get('oy', 0.5)      # Normalized center y-coordinate
#     crop_width = transform_params.get('width', 1.0)  # Normalized width
#     crop_height = transform_params.get('height', 1.0)  # Normalized height
    
#     # Convert normalized coordinates to absolute pixel values
#     center_x = int(ox * w)
#     center_y = int(oy * h)
#     crop_w_pixels = int(crop_width * w)
#     crop_h_pixels = int(crop_height * h)
    
#     # Calculate the crop rectangle coordinates
#     x1 = max(0, center_x - crop_w_pixels // 2)
#     y1 = max(0, center_y - crop_h_pixels // 2)
#     x2 = min(w, x1 + crop_w_pixels)
#     y2 = min(h, y1 + crop_h_pixels)
    
#     # Apply rotation using a rotation matrix
#     # Get the rotation matrix
#     rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), alpha, 1)
#     # Apply the rotation
#     rotated_frame = cv2.warpAffine(frame, rotation_matrix, (w, h))
    
#     # Apply cropping
#     cropped_frame = rotated_frame[y1:y2, x1:x2]
    
#     # Print information for debugging
#     print(f"Original dimensions: {w}x{h}")
#     print(f"Rotation angle: {alpha} degrees around ({center_x}, {center_y})")
#     print(f"Crop dimensions: {crop_w_pixels}x{crop_h_pixels} at ({x1}, {y1})")
#     print(f"Resulting dimensions: {cropped_frame.shape[1]}x{cropped_frame.shape[0]}")
    
#     return cropped_frame

def apply_transform(frame, transform_params):

    # Get frame dimensions 0 = height, 1 = width
    frame_height, frame_width = frame.shape[:2]
    
    # Extract parameters from the json file and use some default values in case one is not given
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

    # # Calculate the maximum safe size for a rotated rectangle
    # # This accounts for rotation making the rectangle extend beyond its original bounds
    
    # # The maximum distance from center to corner of the crop rectangle
    # diagonal_half_length = np.sqrt((crop_w_pixels/2)**2 + (crop_h_pixels/2)**2)
    
    # # Calculate the worst-case scenario distances after rotation
    # # The inscribed circle within the frame that's guaranteed to be safe
    # max_safe_radius = min(center_x, center_y, frame_width - center_x, frame_height - center_y)
    
    # # If our diagonal exceeds the safe radius, we need to scale down
    # if diagonal_half_length > max_safe_radius:
    #     # Calculate scale factor needed
    #     scale_factor = max_safe_radius / diagonal_half_length
        
    #     # Apply scale factor to maintain aspect ratio
    #     crop_w_pixels = int(crop_w_pixels * scale_factor)
    #     crop_h_pixels = int(crop_h_pixels * scale_factor)
    
    # # Apply rotation first
    # rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), -alpha, 1)
    # rotated_frame = cv2.warpAffine(frame, rotation_matrix, (frame_width, frame_height))
    
    # # Then calculate the crop coordinates in the rotated frame
    # x1 = max(0, center_x - crop_w_pixels // 2)
    # y1 = max(0, center_y - crop_h_pixels // 2)
    # x2 = min(frame_width, x1 + crop_w_pixels)
    # y2 = min(frame_height, y1 + crop_h_pixels)
    
    # # Apply cropping to the rotated frame
    # cropped_frame = rotated_frame[y1:y2, x1:x2]
    
    # return cropped_frame

 # Calculate the desired aspect ratio
    aspect_ratio = crop_width / crop_height
    
    # Calculate crop boundaries (before rotation)
    half_width = crop_w_pixels // 2
    half_height = crop_h_pixels // 2
    
    # Check if crop exceeds frame boundaries
    left_edge = center_x - half_width
    right_edge = center_x + half_width
    top_edge = center_y - half_height
    bottom_edge = center_y + half_height

    # Determine if any part of the crop is outside the frame
    crop_exceeds_boundaries = (left_edge < 0 or right_edge > frame_width or 
                            top_edge < 0 or bottom_edge > frame_height)

    # If crop exceeds boundaries, scale it down while maintaining aspect ratio
    if crop_exceeds_boundaries:
        print("Initial crop area exceeds frame boundaries. Scaling down...")
        
        # Calculate scale factors for both dimensions
        scale_x = min(1.0, center_x / half_width, (frame_width - center_x) / half_width)
        scale_y = min(1.0, center_y / half_height, (frame_height - center_y) / half_height)
        
        # Use the smaller scale factor to maintain aspect ratio
        scale_factor = min(scale_x, scale_y)
        
        # Apply scale factor
        crop_w_pixels = int(crop_w_pixels * scale_factor)
        crop_h_pixels = int(crop_h_pixels * scale_factor)
        
        # Recalculate half dimensions
        half_width = crop_w_pixels // 2
        half_height = crop_h_pixels // 2
        
        print(f"Scaled crop dimensions to {crop_w_pixels}x{crop_h_pixels}")
    
    # Apply rotation first
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), -alpha, 1)
    #rotated_frame = cv2.warpAffine(frame, rotation_matrix, (frame_width, frame_height))
    rotated_frame = cv2.warpAffine(frame, rotation_matrix, (frame_width, frame_height), borderMode=cv2.BORDER_REPLICATE)
    
    # Calculate the final crop coordinates
    half_width = crop_w_pixels // 2
    half_height = crop_h_pixels // 2
    
    # Ensure we stay in bounds (this is a safety check, should be unnecessary after scaling)
    x1 = max(0, center_x - half_width)
    y1 = max(0, center_y - half_height)
    x2 = min(frame_width, center_x + half_width)
    y2 = min(frame_height, center_y + half_height)
    
    # Apply cropping
    cropped_frame = rotated_frame[y1:y2, x1:x2]
    
    return cropped_frame




def start_video_receiver(transform_json_path, host_ip='0.0.0.0', port=9999):
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
        # Clean up
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