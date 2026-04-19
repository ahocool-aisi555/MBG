import cv2
import numpy as np
import threading
import time
import winsound

# Define RTSP stream URLs for both cameras
RTSP_URL_1 = "rtsp://admin:admin@192.168.1.51:8554/Streaming/Channels/101"
RTSP_URL_2 =  "" #"http://192.168.1.52:8080/video"

# Initialize the AprilTag detector with the 36h11 dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Shared variables and lock
id_counters = {}
id_last_detection_time = {}
cooldown = 5  # seconds
lock = threading.Lock()
stop_threads = threading.Event()  # Thread-safe stop flag


def process_camera(camera_id, rtsp_url):
    global id_counters, id_last_detection_time

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"Failed to open RTSP stream for {camera_id}. Please check the URL or network connection.")
        return

    print(f"Camera {camera_id} is now processing.")
    frame_count = 0

    while not stop_threads.is_set():  # Check if the stop signal is set
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to grab frame from {camera_id}. Check the camera connection.")
            continue

        # Process every 10th frame to save computational effort
        frame_count += 1
        if frame_count % 10 != 0:
            continue

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags
        corners, ids, _ = detector.detectMarkers(gray)

        # If any tags are detected
        if ids is not None:
            current_time = time.time()

            for corner, tag_id in zip(corners, ids.flatten()):
                tag_id = int(tag_id)  # Ensure ID is an integer
                with lock:
                    # Check cooldown for the ID
                    if tag_id not in id_last_detection_time or current_time - id_last_detection_time[tag_id] >= cooldown:
                        # Increment the counter for this ID
                        if tag_id not in id_counters:
                            id_counters[tag_id] = 0
                        id_counters[tag_id] += 1
                        id_last_detection_time[tag_id] = current_time
                        winsound.Beep(1000, 200)  # Frequency: 1000 Hz, Duration: 200 ms
                        print(f"Camera {camera_id} detected ID {tag_id}. Counter: {id_counters[tag_id]}")

                # Draw bounding boxes and IDs
                int_corners = corner.astype(np.intp)
                cv2.polylines(frame, [int_corners], isClosed=True, color=(0, 255, 0), thickness=2)
                tag_id_str = f"ID: {tag_id} ({id_counters[tag_id]})"
                cv2.putText(frame, tag_id_str, (int_corners[0][0][0], int_corners[0][0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Resize frame for display
        frame_resized = cv2.resize(frame, (600, 480))
        cv2.imshow(f"Camera {camera_id}", frame_resized)

        # Handle quit in a non-blocking way
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_threads.set()  # Signal all threads to stop
            break

    # Release resources
    cap.release()
    cv2.destroyWindow(f"Camera {camera_id}")


# Start threads for both cameras
thread1 = threading.Thread(target=process_camera, args=("camera1", RTSP_URL_1))
thread2 = threading.Thread(target=process_camera, args=("camera2", RTSP_URL_2))

thread1.start()
thread2.start()

try:
    # Monitor threads for keyboard interrupt
    while thread1.is_alive() or thread2.is_alive():
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Stopping threads...")
    stop_threads.set()

# Wait for threads to finish
thread1.join()
thread2.join()

# Cleanup
cv2.destroyAllWindows()
print("All threads stopped. Program terminated.")
