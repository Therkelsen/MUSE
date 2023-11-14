import cv2
import csv
import time
import mediapipe
import numpy as np
mp_drawing = mediapipe.solutions.drawing_utils
mp_pose = mediapipe.solutions.pose

print(cv2.__version__)
print(np.__version__)


def calculate_angle(a, b, c):
    a = np.array(a)         # First
    b = np.array(b)         # Midd
    c = np.array(c)         # End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle


# Enumerate possible states
class State:
    IDLE = 0
    RECORDING = 1
    SAVING = 2
    EXIT = 3


# Video feed
cap = cv2.VideoCapture(0)    # number that represents the webcam == 0

# Specify the file path where you want to save the CSV file
csv_file_path = 'elbow_angles.csv'

# Create an empty array to store angles
shape = (0, 1)
angles = np.zeros(shape)
times = np.zeros(shape)

# Initialize a variable to keep track of the start time
start_time = time.time()

# Initialize the state
current_state = State.IDLE

# Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:
    while current_state != State.EXIT:
        cap.isOpened()
        ret, frame = cap.read()     # Gets the current feed from the camera. ret isn't used, frame gives the actual videoframe
        cv2.imshow('Mediapip Feed', frame)

        if current_state == State.IDLE:
            angles = np.zeros(shape)
            times = np.zeros(shape)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                current_state = State.RECORDING
        elif current_state == State.RECORDING:
            # Get the current system time
            current_time = time.time()

            # # Calculate the elapsed time in seconds
            # elapsed_time = current_time - start_time
            # #     # Check if 1 second has passed
            # if elapsed_time >= 10.0:
            #     print("Broke loop after ", elapsed_time, " seconds")
            #     current_state = State.SAVING

            ret, frame = cap.read()     # Gets the current feed from the camera. ret isn't used, frame gives the actual videoframe

            # Recolor image. frame comes in BGR, but we need it in RGB to predict the pose
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Make detection. Makes the predictions from the pose object to the image object, and stores it in results array
            results = pose.process(image)

            # Changes back to BGR, since openCV wants it in that format
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates
                shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y
                wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y

                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Save to angles array
                angles = np.vstack((angles, angle))
                times = np.vstack((times, current_time))

                # Visualize. Coordinates of the elbow is being multiplied by the webcam image resolution (640,480), to put the coordinate at the tip of the elbow
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )
            except:
                pass

            # Render detections. Draws detections unto image. pose_landmarks gives all the predicted points and POSE_CONNECTIONS gives poit connections
            # draw_landmarks param: image as np array, list of landmarks, connections between landmarks, dots, lines
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Mediapip Feed', image)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('k'):
                current_state = State.SAVING
            if current_state == State.SAVING:
                with open(csv_file_path, mode='w', newline='') as file:
                    # Create a CSV writer with a custom format for floating-point numbers
                    csv_writer = csv.writer(file)  # Adjust the format as needed
                    # Combine angle and time data into a list of lists
                    data = list(zip(angles, times))

                    # Save to CSV with the custom format
                    csv_writer.writerows(data)
                    current_state = State.IDLE

        if key == ord('q'):  # Checks if we try to close the feed by pressing 'q'
            current_state = State.EXIT

    cap.release()   # Releases the webcam
    cv2.destroyAllWindows()
