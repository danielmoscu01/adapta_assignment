import cv2
import socket
import pickle
import struct
import json
import math

def load_transform_params(json_path):
    # we open the json file and read the parameters from it
    with open(json_path, 'r') as f:
        params = json.load(f)
    
    return params


def get_rotated_rect_corners(center_x, center_y, width, height, angle_rad):
    """Calculate the four corners of a rotated rectangle."""
    # Half dimensions
    w2 = width / 2
    h2 = height / 2
    
    # Calculate coordinates before rotation (relative to center)
    corners_rel = [(-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2)]
    
    # Rotation matrix components
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Rotate each corner and translate to the center position
    corners = []
    for x_rel, y_rel in corners_rel:
        x = center_x + (x_rel * cos_a - y_rel * sin_a)
        y = center_y + (x_rel * sin_a + y_rel * cos_a)
        corners.append((x, y))
    
    return corners

def is_rect_inside_frame(corners, frame_width, frame_height):
    """Check if the rotated rectangle is completely inside the frame."""
    for x, y in corners:
        if x < 0 or x >= frame_width or y < 0 or y >= frame_height:
            return False
    return True

def calculate_scaling_factor(corners, frame_width, frame_height):
    """Calculate the scaling factor needed to fit the rectangle inside the frame."""
    min_x = min(corner[0] for corner in corners)
    max_x = max(corner[0] for corner in corners)
    min_y = min(corner[1] for corner in corners)
    max_y = max(corner[1] for corner in corners)
    
    # Calculate how much the rectangle extends beyond the frame
    x_overflow = max(0, -min_x, max_x - frame_width)
    print(f"x_overflow: {x_overflow}")
    y_overflow = max(0, -min_y, max_y - frame_height)
    print(f"y_overflow: {y_overflow}")
    
    # Calculate scaling factors for width and height
    scale_x = frame_width / (max_x - min_x) if x_overflow > 0 else 1.0
    print(f"scale_x: {scale_x}")
    scale_y = frame_height / (max_y - min_y) if y_overflow > 0 else 1.0
    print(f"scale_y: {scale_y}")
    
    # Use the smaller scaling factor to maintain aspect ratio
    #return min(scale_x, scale_y)
    return min(scale_x, scale_y)


def apply_transform(frame, transform_params):

    # Get frame dimensions 0 = height, 1 = width
    frame_height, frame_width = frame.shape[:2]
    print(f"Frame dimensions: {frame_width}x{frame_height}")
    
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
    print(f"Crop dimensions: {crop_w_pixels}x{crop_h_pixels}, Center: ({center_x}, {center_y}), Angle: {alpha}")

    corners = get_rotated_rect_corners(center_x, center_y, crop_w_pixels, crop_h_pixels, math.radians(alpha))
    print (f"Corners before scaling: {corners}")

    if not is_rect_inside_frame(corners, frame_width, frame_height):
        # Calculate scaling factor needed to fit within the frame
        scale_factor = calculate_scaling_factor(corners, frame_width, frame_height)
        
        # Apply scaling to both dimensions to preserve aspect ratio
        crop_w_pixels = int(crop_w_pixels * scale_factor)
        crop_h_pixels = int(crop_h_pixels * scale_factor)
        print(f"New dimensions: {crop_w_pixels}x{crop_h_pixels}")


    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), alpha, 1)
    rotated_frame = cv2.warpAffine(
        frame, 
        rotation_matrix, 
        (frame_width, frame_height),
        borderMode=cv2.BORDER_REPLICATE  # This prevents black corners in the rotated image
    )
    
    # Calculate the final crop coordinates based on center and dimensions
    half_width = crop_w_pixels // 2
    half_height = crop_h_pixels // 2
    
    x1 = max(0, center_x - half_width)  # Protect against edge cases
    y1 = max(0, center_y - half_height)
    x2 = min(frame_width, center_x + half_width)
    y2 = min(frame_height, center_y + half_height)
    
    # Apply cropping to the rotated frame
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