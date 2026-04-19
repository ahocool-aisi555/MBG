# Script by Nyoman Yudi Kurniawan © 2025
# www.aisi555.com
# nyomanyudik@gmail.com

import cv2
import numpy as np
import concurrent.futures
import time
import winsound
import threading

# List of RTSP/HTTP camera streams
RTSP_URLS = [
    "rtsp://admin:admin@192.168.1.51:8554/Streaming/Channels/101",
    "http://192.168.1.52:8080/video"
]

# Initialize the AprilTag detector with the 36h11 dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Cooldown tracking per ID
cooldown_tracker = {}
id_counters = {}

# Shutdown flag to gracefully stop threads
shutdown_flag = threading.Event()

# Function to handle the beep
def play_beep():
    winsound.Beep(1000, 200)  # Frequency: 1000 Hz, Duration: 200 ms

# Adaptive sleep time for problematic cameras
adaptive_delay = {idx: 0.1 for idx in range(len(RTSP_URLS))}  # Start with a 100ms delay

def process_camera(rtsp_url, camera_id, beep_executor):
    global cooldown_tracker, id_counters, adaptive_delay
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"Failed to open RTSP stream for Camera {camera_id}. Check the URL or network.")
        return

    frame_count = 0
    failed_attempts = 0

    while not shutdown_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            failed_attempts += 1
            print(f"Camera {camera_id}: Failed to grab frame. Attempt {failed_attempts}.")
            
            # Slow down retries for problematic cameras
            time.sleep(adaptive_delay[camera_id])
            adaptive_delay[camera_id] = min(adaptive_delay[camera_id] + 0.1, 1.0)  # Max delay 1s
            continue
        else:
            # Reset adaptive delay on successful frame grab
            adaptive_delay[camera_id] = 0.1
            failed_attempts = 0

        frame_count += 1
        if frame_count % 5 != 0:  # Process every 5th frame
            continue

        # Detect AprilTags
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            for corner, tag_id in zip(corners, ids.flatten()):
                tag_id = int(tag_id)
                current_time = time.time()

                # Initialize counter for new IDs
                if tag_id not in id_counters:
                    id_counters[tag_id] = 0

                # Apply cooldown
                if tag_id not in cooldown_tracker or (current_time - cooldown_tracker[tag_id] > 5):
                    cooldown_tracker[tag_id] = current_time
                    id_counters[tag_id] += 1

                    # Trigger a beep in parallel
                    beep_executor.submit(play_beep)

                    print(f"Camera {camera_id}: ID {tag_id} Count: {id_counters[tag_id]} @ {time.ctime(current_time)}")

                # Draw the bounding box and ID
                int_corners = corner.astype(np.intp)
                cv2.polylines(frame, [int_corners], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.putText(frame, f"ID: {tag_id} Cnt: {id_counters[tag_id]}", 
                            (int_corners[0][0][0], int_corners[0][0][1] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        # Display the video feed
        frame_resized = cv2.resize(frame, (600, 480))
        cv2.imshow(f"Camera {camera_id}", frame_resized)

        # Check for quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            shutdown_flag.set()
            break

    cap.release()
    cv2.destroyWindow(f"Camera {camera_id}")

if __name__ == "__main__":
    try:
        # Executor for beep sounds
        with concurrent.futures.ThreadPoolExecutor() as beep_executor:
            # Executor for cameras
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(process_camera, url, idx, beep_executor) 
                    for idx, url in enumerate(RTSP_URLS)
                ]
                # Wait for threads to finish
                concurrent.futures.wait(futures)
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting gracefully...")
        shutdown_flag.set()  # Signal all threads to stop
    finally:
        # Ensure all OpenCV windows are closed
        cv2.destroyAllWindows()
        print("Cleanup complete.")
