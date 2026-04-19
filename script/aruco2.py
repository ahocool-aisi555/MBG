import cv2
import time
import winsound
import numpy as np

# RTSP stream URL
rtsp_url = "rtsp://admin:admin@192.168.1.52:8554/Streaming/Channels/101"

# Load ArUco dictionary and parameters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

# Open the RTSP stream
cap = cv2.VideoCapture(rtsp_url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)

if not cap.isOpened():
    print("Failed to connect to RTSP stream. Please check the URL.")
    exit()

frame_count = 0  # Counter for frames

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame. Reconnecting...")
            time.sleep(2)  # Wait before retrying
            cap = cv2.VideoCapture(rtsp_url)
            continue

        frame_count += 1
        
        # Process every 15th frame
        if frame_count % 15 == 0:
            # Convert to grayscale for ArUco detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect markers
            corners, ids, rejected = detector.detectMarkers(gray)
            

            if ids is not None:
                winsound.Beep(1000, 200)  # Frequency: 1000 Hz, Duration: 200 ms
                
               
                # Iterate over detected markers
                for i, corner in enumerate(corners):
                    # Convert corner points to integer
                    int_corners = np.intp(corner)

                    # Draw the bounding box
                    cv2.polylines(frame, [int_corners], isClosed=True, color=(0, 255, 0), thickness=2)

                    # Display the tag ID
                    tag_id_str = f"ID: {ids[i][0]}"
                    cv2.putText(frame, tag_id_str, (int_corners[0][0][0], int_corners[0][0][1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                print(f"Detected IDs: {ids.flatten()}")
            else:
                print("No markers detected.")
        
            frame_resized = cv2.resize(frame, (600,480))
            # Show the resized video feed
            cv2.imshow("IP Camera ARUCO Code Detection", frame_resized)
        
        else:
            continue
        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Detection stopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
