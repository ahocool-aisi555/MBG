# Script by Nyoman Yudi Kurniawan © 2025
# www.aisi555.com
# nyomanyudik@gmail.com

import cv2
import threading

class IPCameraThread(threading.Thread):
    def __init__(self, camera_url, name):
        threading.Thread.__init__(self)
        self.camera_url = camera_url
        self.name = name
        self.capture = cv2.VideoCapture(camera_url)
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                # Display the camera feed in a separate window
                cv2.imshow(self.name, frame)
                
                # Example: Process the frame here
                # (e.g., object detection, motion detection, etc.)

            # Press 'q' to quit the thread
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()

    def stop(self):
        self.running = False
        self.capture.release()
        cv2.destroyWindow(self.name)

# URLs of your IP cameras
camera1_url = "rtsp://admin:admin@192.168.1.190:8554/Streaming/Channels/101"
camera2_url = "http://192.168.1.189:8080/video"

# Create threads for each camera
camera1_thread = IPCameraThread(camera1_url, "Camera 1")
camera2_thread = IPCameraThread(camera2_url, "Camera 2")

# Start threads
camera1_thread.start()
camera2_thread.start()

# Wait for both threads to complete
camera1_thread.join()
camera2_thread.join()
