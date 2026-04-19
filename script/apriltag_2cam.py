import cv2
import cv2.aruco as aruco
import time

# Define video sources
ipcam_url1 = "rtsp://admin:admin@192.168.1.190:8554/Streaming/Channels/101"
ipcam_url2 = "http://192.168.1.189:8080/video"

# Initialize video captures
cap1 = cv2.VideoCapture(ipcam_url1)
cap2 = cv2.VideoCapture(ipcam_url2)


# Initialize the AprilTag detector with the 36h11 dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36H11)
aruco_params = cv2.aruco.DetectorParameters()


# Frame counters
frame_count1 = 0
frame_count2 = 0

# Process every Nth frame
process_interval = 15

try:
    while True:
        # Capture frame from Camera 1
        ret1, frame1 = cap1.read()
        if ret1:
            frame_count1 += 1
            if frame_count1 % process_interval == 0:
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                corners1, ids1, _ = aruco.detectMarkers(gray1, aruco_dict, parameters=aruco_params)
                if ids1 is not None:
                    frame1 = aruco.drawDetectedMarkers(frame1, corners1, ids1)
            cv2.imshow("Camera 1", frame1)

        # Capture frame from Camera 2
        ret2, frame2 = cap2.read()
        if ret2:
            frame_count2 += 1
            if frame_count2 % process_interval == 0:
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                corners2, ids2, _ = aruco.detectMarkers(gray2, aruco_dict, parameters=aruco_params)
                if ids2 is not None:
                    frame2 = aruco.drawDetectedMarkers(frame2, corners2, ids2)
            cv2.imshow("Camera 2", frame2)

        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopping...")

finally:
    # Release resources
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()
