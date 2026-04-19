import cv2
import numpy as np
import time
import winsound


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


def detect_and_count_runners(ipcam_url):
    cap = cv2.VideoCapture(ipcam_url)

    # Initialize runner appearance tracking
    detected_runners = {}  # Dictionary to store appearance counts
    runner_timestamps = {}  # Cooldown timestamps
    frame_skip = 10  # Process every 5rd frame for better performance
    frame_counter = 0  # Counter to skip frames
    cooldown_time = 5  # Cooldown in seconds
    retry_delay = 5  # Retry delay in seconds if connection drops

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Reconnecting...")
            cap.release()
            cap = reconnect_camera(ipcam_url, retry_delay)
            continue

        frame_counter += 1
        
		# Process detection every 'frame_skip' frames
        if frame_counter % frame_skip == 0:
            current_time = time.time()
			
            #Convert to grayscale
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
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
            # Display the appearance report on the video feed
            y_offset = 145
            cv2.putText(frame, "Laporan Pelari:", (35, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 2)
            for i, (runner_id, count) in enumerate(sorted(detected_runners.items())):
                cv2.putText(frame, f"No-{runner_id}: {count}", (35, y_offset + (i * 40)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2)


            frame_resized = cv2.resize(frame, (600,480))
            # Show the resized video feed
            cv2.imshow("IP Camera QR Code Detection", frame_resized)
        else:
            continue
        
        # Exit and save results on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Saving results to 'report.txt'...")
            with open("report.txt", "w") as file:
                file.write("  Laporan Kegiatan Lari \n")
                file.write("========================\n")
                for runner_id, count in sorted(detected_runners.items()):
                    file.write(f"No-{runner_id}: {count} Putaran\n")
            print("Report saved. Exiting program.")
            break

    cap.release()
    cv2.destroyAllWindows()


# Replace with your IP camera URL
ipcam_url = "rtsp://admin:admin@192.168.1.101:8554/Streaming/Channels/101"
#ipcam_url = "rtsp://192.168.1.189:8080/h264_ulaw.sdp"
#ipcam_url = "http://192.168.1.189:8080/video"
detect_and_count_runners(ipcam_url)