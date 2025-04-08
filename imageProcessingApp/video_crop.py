import cv2
import socket
import pickle
import struct
import json

def load_transform_params(json_path):
    # we open the json file and read the parameters from it
    with open(json_path, 'r') as f:
        params = json.load(f)
    
    return params

def apply_transform(frame, transform_params):
    """Apply rotation and cropping based on custom parameters."""
    # Get frame dimensions
    h, w = frame.shape[:2]
    
    # Extract parameters from the json file and use some default values in case one is not given
    alpha = transform_params.get('alpha', 0)  # Rotation angle in degrees
    ox = transform_params.get('ox', 0.5)      # Normalized center x-coordinate
    oy = transform_params.get('oy', 0.5)      # Normalized center y-coordinate
    crop_width = transform_params.get('width', 1.0)  # Normalized width
    crop_height = transform_params.get('height', 1.0)  # Normalized height
    
    # Convert normalized coordinates to absolute pixel values
    center_x = int(ox * w)
    center_y = int(oy * h)
    crop_w_pixels = int(crop_width * w)
    crop_h_pixels = int(crop_height * h)
    
    # Calculate the crop rectangle coordinates
    x1 = max(0, center_x - crop_w_pixels // 2)
    y1 = max(0, center_y - crop_h_pixels // 2)
    x2 = min(w, x1 + crop_w_pixels)
    y2 = min(h, y1 + crop_h_pixels)
    
    # Apply rotation using a rotation matrix
    # Get the rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), alpha, 1)
    # Apply the rotation
    rotated_frame = cv2.warpAffine(frame, rotation_matrix, (w, h))
    
    # Apply cropping
    cropped_frame = rotated_frame[y1:y2, x1:x2]
    
    # Print information for debugging
    print(f"Original dimensions: {w}x{h}")
    print(f"Rotation angle: {alpha} degrees around ({center_x}, {center_y})")
    print(f"Crop dimensions: {crop_w_pixels}x{crop_h_pixels} at ({x1}, {y1})")
    print(f"Resulting dimensions: {cropped_frame.shape[1]}x{cropped_frame.shape[0]}")
    
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