import cv2
import threading
import time

# RTSP stream URLs for 4 cameras
rtsp_urls = [
    "rtsp://admin:CXPPTX@192.168.0.100:554/Streaming/Channels/101",
    "rtsp://admin:SSNBVJ@192.168.0.101:554/Streaming/Channels/101",
    "rtsp://admin:OJVXRC@192.168.0.102:554/Streaming/Channels/101",
    "rtsp://admin:LWHRTR@192.168.0.103:554/Streaming/Channels/101"
]

# Initialize the AprilTag detector with the 36h11 dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Shared variables for frames and timestamps
latest_frames = {i: None for i in range(len(rtsp_urls))}
last_frame_times = {i: time.time() for i in range(len(rtsp_urls))}
frame_locks = {i: threading.Lock() for i in range(len(rtsp_urls))}
stop_threads = False

def frame_grabber(camera_index, rtsp_url):
    global latest_frames, last_frame_times, stop_threads
    while not stop_threads:
        cap = cv2.VideoCapture(rtsp_url)
        while cap.isOpened() and not stop_threads:
            ret, frame = cap.read()
            if ret:
                with frame_locks[camera_index]:
                    latest_frames[camera_index] = frame
                    last_frame_times[camera_index] = time.time()
            else:
                break
        cap.release()
        time.sleep(1)  # Retry delay after disconnect

# Start a thread for each camera
threads = []
for i, url in enumerate(rtsp_urls):
    t = threading.Thread(target=frame_grabber, args=(i, url), daemon=True)
    threads.append(t)
    t.start()

try:
    while True:
        for i in range(len(rtsp_urls)):
            # Check for the latest frame
            with frame_locks[i]:
                frame = latest_frames[i]
            
            # Check if the frame is too old
            if time.time() - last_frame_times[i] > 5:
                print(f"Camera {i}: No frame received in 5 seconds, reconnecting...")
                latest_frames[i] = None  # Clear the frame
                last_frame_times[i] = time.time()  # Prevent repeated reconnect attempts
                continue
            
            # Process the latest frame
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                corners, ids, rejected = detector.detectMarkers(gray)
                
                # Draw detected markers
                if ids is not None:
                    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                
                # Display the frame for each camera
                frame_resized = cv2.resize(frame, (600, 400))
                cv2.imshow(f"Camera {i} Aruco Detection", frame_resized)
            
        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.01)  # Reduce CPU usage

except KeyboardInterrupt:
    print("Stopping...")
finally:
    stop_threads = True
    for t in threads:
        t.join()
    cv2.destroyAllWindows()
