#Script by Nyoman Yudi Kurniawan © 2025

import cv2
import numpy as np
import winsound
import threading
import time

# Define the RTSP stream URL
RTSP_URL = "rtsp://admin:SSNBVJ@192.168.1.102:554/Streaming/Channels/101"

# Initialize the AprilTag detector with the 36h11 dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
parameters = cv2.aruco.DetectorParameters()

# Create the detector
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Function to reconnect to the IP camera
def reconnect_camera(ipcam_url, retry_delay=5):
    print("Attempting to reconnect to the IP camera...")
    while True:
        cap = cv2.VideoCapture(ipcam_url)
        if cap.isOpened():
            print("Reconnected to the IP camera successfully!")
            return cap
        print(f"Failed to reconnect. Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)

# Beep function (runs in a separate thread)
def beep():
    #winsound.Beep(1000, 200)  # Frequency: 1000 Hz, Duration: 200 ms
    winsound.PlaySound('beep.wav', winsound.SND_FILENAME)
# Open the RTSP stream
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("Failed to open RTSP stream. Please check the URL or network connection.")
    exit()

frame_count = 0
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Reconnecting...")
            cap.release()
            cap = reconnect_camera(RTSP_URL, 5)
            continue

        # Only process every 15th frame to save computational effort
        frame_count += 1
        if frame_count % 3 != 0:
            continue

        # Convert the frame to grayscale (required for detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags
        corners, ids, _ = detector.detectMarkers(gray)
        
        # If any tags are detected
        if ids is not None:
            for corner, tag_id in zip(corners, ids.flatten()):
                # Draw the bounding box
                int_corners = corner.astype(np.intp)
                cv2.polylines(frame, [int_corners], isClosed=True, color=(0, 255, 0), thickness=2)

                # Display the tag ID
                tag_id_str = f"ID: {tag_id}"
                cv2.putText(frame, tag_id_str, (int_corners[0][0][0], int_corners[0][0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Run the beep function in a separate thread
            threading.Thread(target=beep).start()
            print(f"Detected IDs: {ids.flatten()}")
        frame_resized = cv2.resize(frame, (800,600))
        # Show the resized video feed
        cv2.imshow("IP Camera apriltag Code Detection - press q to quit", frame_resized)
        # Quit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Program interrupted.")

finally:
    # Release the resources
    cap.release()
    cv2.destroyAllWindows()
