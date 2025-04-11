# adapta_assignment


# Overview
The system is divided into two components:

    video_acquisition.py: Captures frames from a webcam and sends them over the network.
    
    video_crop.py: Receives frames, applies rotation and cropping based on a JSON configuration, and displays the results.

    treat edge case where crop section might be out of the frame bounds
    

# Requirements
A requirements list is provided in the project.


# Running the Program

Step 1: Start the Receiver
    Always start the receiver (video_crop.py) first:
    'python video_crop.py --json transform.json --ip 0.0.0.0 --port 9999'

Parameters:
    --json: Path to the JSON configuration file
    --ip: IP address to listen on (default: 0.0.0.0, which listens on all interfaces) (optional)
    --port: Port number to listen on (default: 9999) (optional)

Step 2: Start the Sender
    Once the receiver is running, start the sender (video_acquisition.py):
    'python video_acquisition.py --ip 127.0.0.1 --port 9999'

Parameters:
    --ip: IP address of the receiver (use the actual IP if on different machines) (optional)
    --port: Port number of the receiver (must match the receiver's port) (optional)