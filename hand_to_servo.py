import cv2
import mediapipe as mp
import serial
import time

ser = serial.Serial('COM6', 115200, timeout=1)
time.sleep(2)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# from MediaPipe
finger_tips = [4, 8, 12, 16, 20]
finger_base = [2, 6, 10, 14, 18]

MIN_ANGLE = 30
MAX_ANGLE = 180
THUMB_MIN = 100
THUMB_MAX = 160

def get_finger_states(landmarks):
    states = []
    for tip, base in zip(finger_tips, finger_base):
        if tip == 4:  
            state = landmarks[tip].x < landmarks[base].x
        else:
            state = landmarks[tip].y < landmarks[base].y
        states.append(1 if state else 0)
    return states

def map_angles(finger_states):
    angles = []
    for i, state in enumerate(finger_states):
        if i == 0:  # Thumb
            angle = THUMB_MAX if state else THUMB_MIN
        elif i == 2:  # middle finger since servo not workin properly
            angle = MAX_ANGLE * 0.7 if state else MIN_ANGLE * 0.7
        else:
            angle = MAX_ANGLE if state else MIN_ANGLE
        angles.append(int(angle))
    return angles

#opencv code
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            states = get_finger_states(lm)
            angles = map_angles(states)
            angles = angles[::-1]  #fingers were flipped so flipped them to fix

            angle_str = ','.join(map(str, angles)) + '\n'
            ser.write(angle_str.encode('utf-8'))
            print(f"Sent: {angle_str.strip()}")

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()
