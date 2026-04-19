import cv2
import time
import winsound

# RTSP stream URL
rtsp_url = "http://192.168.43.1:8080/video"

# Load ArUco dictionary and parameters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

# Open the RTSP stream
cap = cv2.VideoCapture(rtsp_url)

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
                print(f"Detected IDs: {ids.flatten()}")
            else:
                print("No markers detected.")
        
        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Detection stopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
