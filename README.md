# adapta_assignment


task breakdown:

video_acquisition.py

    record frames with camera
    send them to the other script via network (we will use tcp websockets so we dont lose frames or quality)


video_crop.py


    receive frames on websocket (will listen on the websocket untill the other script connects and starts sending data)
    parse the json file for crop / rotate parameters
    apply said modifiers to frames incoming on the websocket

    treat edge case where crop section might be out of the frame bounds
    


first run the server ( video_crop.py ) with "python video_crop.py --json rcrop_parameters.json"

then the client (video_acquisition.py) with  "python video_acquisition.py" (if any other ip than localhost is used, add --ip 'ip_address')