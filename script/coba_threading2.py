import cv2
import numpy as np
import threading
import winsound
import time


# Define the RTSP stream URLs for both cameras
CAMERA_1_URL = "rtsp://admin:admin@192.168.1.190:8554/Streaming/Channels/101"
CAMERA_2_URL = "http://192.168.1.189:8080/video"



# Initialize the AprilTag detector with the 36h11 dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Initialize runner appearance tracking
detected_runners = {}  # Dictionary to store appearance counts
runner_timestamps = {}  # Cooldown timestamps
cooldown_time = 5  # Cooldown in seconds

# Define a thread class for camera processing
class CameraThread(threading.Thread):
    def __init__(self, camera_url, name):
        threading.Thread.__init__(self)
        self.camera_url = camera_url
        self.name = name
        self.capture = cv2.VideoCapture(camera_url)
        self.running = True

        if not self.capture.isOpened():
            print(f"Failed to open {self.name} stream. Please check the URL or network connection.")
            self.running = False

    def run(self):
        frame_count = 0       
        
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                print(f"Failed to grab frame from {self.name}.")
                continue

            # Only process every 10th frame to save computational effort
            frame_count += 1
            if frame_count % 10 != 0:
                continue
            
            current_time = time.time()
            # Convert the frame to grayscale (required for detection)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect AprilTags
            corners, ids, _ = detector.detectMarkers(gray)

            # If any tags are detected
            if ids is not None:
                for corner, tag_id in zip(corners, ids.flatten()):
                    last_seen_time = runner_timestamps.get(tag_id, 0)
                    if current_time - last_seen_time > cooldown_time:
                        # Increment count, update timestamp, and beep
                        detected_runners[tag_id] = detected_runners.get(tag_id, 0) + 1
                        runner_timestamps[tag_id] = current_time
                        winsound.Beep(1000, 200)  # Frequency: 1000 Hz, Duration: 200 ms
                        print(f"Pelari No-{tag_id} terdeteksi. Putaran: {detected_runners[tag_id]} kali")
                    
                    # Draw the bounding box
                    int_corners = corner.astype(np.intp)
                    cv2.polylines(frame, [int_corners], isClosed=True, color=(0, 255, 0), thickness=2)

                    # Display the tag ID
                    tag_id_str = f"ID: {tag_id}"
                    cv2.putText(frame, tag_id_str, (int_corners[0][0][0], int_corners[0][0][1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Resize and show the frame
            frame_resized = cv2.resize(frame, (400, 300))
            cv2.imshow(self.name, frame_resized)

            # Quit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()

    def stop(self):
        self.running = False
        self.capture.release()
        cv2.destroyWindow(self.name)

# Create and start threads for both cameras
camera1_thread = CameraThread(CAMERA_1_URL, "Camera 1 - q untuk keluar")
camera2_thread = CameraThread(CAMERA_2_URL, "Camera 2 - q untuk keluar")

camera1_thread.start()
camera2_thread.start()

# Wait for threads to complete
camera1_thread.join()
camera2_thread.join()
