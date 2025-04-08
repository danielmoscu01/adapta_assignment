import cv2
import socket
import pickle
import struct
import time

def start_video_capture(receiver_ip='127.0.0.1', receiver_port=9999):

    # Initialize webcam capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    
    # Set up the TCP socket for transmitting the webcam frames to the video_crop script
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((receiver_ip, receiver_port))
    
    print(f"Connected to receiver at {receiver_ip}:{receiver_port}")
    
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            # Serialize frame so we can send it through the socket and easily unpickle it
            data = pickle.dumps(frame)
            
            # Pack the serialized data with its length as a prefix
            # (struct packs it as a binary format that can be sent over the network)
            message_size = struct.pack("L", len(data))
            client_socket.sendall(message_size + data)
            
            # Delay to control frame rate and CPU usage
            time.sleep(0.03)  # ~30 fps
            
    except KeyboardInterrupt:
        print("Stopping video capture")
    finally:
        # Clean up used resources
        cap.release()
        client_socket.close()
        print("Resources released")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Capture and send webcam video')
    parser.add_argument('--ip', type=str, default='127.0.0.1', 
                        help='IP address of the receiver')
    parser.add_argument('--port', type=int, default=9999, 
                        help='Port number of the receiver')
    
    args = parser.parse_args()
    
    start_video_capture(args.ip, args.port)