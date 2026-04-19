import cv2
import numpy as np
import xlwings as xw
import time
import winsound


# Initialize the AprilTag detector with the 36h11 dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
parameters = cv2.aruco.DetectorParameters()

# Create the detector
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

#file excel nama dan sheetnya harus sama, jangan lupa dibuka
wb = xw.Book('laporan.xlsm')
sht = wb.sheets['pelari']
awal = 7 #penanda mulai buat awal row
max_run = sht.range('E5').value

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
                        if detected_runners.get(tag_id, 0) < int(max_run) :
                            detected_runners[tag_id] = detected_runners.get(tag_id, 0) + 1
                        
                            runner_timestamps[tag_id] = current_time
                            #winsound.Beep(3000, 200)  # Frequency: 1000 Hz, Duration: 100 ms
                            winsound.PlaySound("Default Beep", winsound.SND_ALIAS)
                            #tulis ke excel
                            waktu_start= sht.range('K100').value
                            waktu_pelari=  current_time - waktu_start
                            # Convert elapsed seconds to hours, minutes, and seconds
                            hours, remainder = divmod(waktu_pelari, 3600)  # 3600 seconds in an hour
                            minutes, seconds = divmod(remainder, 60)          # 60 seconds in a minute
                            waktu_excel = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                            sht.range('E' + str(awal + tag_id )).value = detected_runners[tag_id]
                            sht.range('F' + str(awal + tag_id )).value = waktu_excel
                        
                            print(f"Pelari No-{tag_id} terdeteksi. Putaran: {detected_runners[tag_id]} kali")
                            if detected_runners.get(tag_id, 0) == int(max_run) :
                                sht.range('G' + str(awal + tag_id )).value = "SELESAI"
                        else:
                            runner_timestamps[tag_id] = current_time
                            winsound.Beep(500, 200)  # Frequency: 1000 Hz, Duration: 200 ms
                            print(f"Pelari No-{tag_id} terdeteksi. Putaran: {detected_runners[tag_id]} kali - SUDAH SELESAI")                            
                    
                    # Draw the bounding box
                    int_corners = corner.astype(np.intp)
                    cv2.polylines(frame, [int_corners], isClosed=True, color=(0, 255, 0), thickness=2)

                    # Display the tag ID
                    tag_id_str = f"ID: {tag_id}"
                    cv2.putText(frame, tag_id_str, (int_corners[0][0][0], int_corners[0][0][1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                
            # Display the appearance report on the video feed
            y_offset = 145
            cv2.putText(frame, "Laporan Pelari:", (35, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 2)
            for i, (runner_id, count) in enumerate(sorted(detected_runners.items())):
                cv2.putText(frame, f"No-{runner_id}: {count}", (35, y_offset + (i * 40)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2)


            frame_resized = cv2.resize(frame, (600,480))
            # Show the resized video feed
            cv2.imshow("IP Camera QR Code Detection - tekan keyboard q untuk keluar ", frame_resized)
        else:
            continue
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("keluar dari program")
            break


    cap.release()
    cv2.destroyAllWindows()


# Replace with your IP camera URL
ipcam_url = "rtsp://admin:SSNBVJ@192.168.1.102:554/Streaming/Channels/101"
#ipcam_url = "http://192.168.1.51:8080/video"
detect_and_count_runners(ipcam_url)