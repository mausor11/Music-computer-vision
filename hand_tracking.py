import csv

import cv2
import mediapipe as mp
import tensorflow as tf
import numpy as np
from gesture_voice_controller import GestureVoiceController
import tkinter as tk
from threading import Thread
import music_player
import spotify_api as sp
from dotenv import load_dotenv
import os

gesture_recognition_active = True

def create_button_window(gesture_controller, spotifyApi):
    global gesture_recognition_active
    def on_button_click():
        Thread(target=gesture_controller.set_music_by_saying_title(spotifyApi)).start()

    def toggle_gesture_recognition():
        global gesture_recognition_active
        gesture_recognition_active = not gesture_recognition_active

    window = tk.Tk()
    button = tk.Button(window, text="Set Music By Saying Title", command=on_button_click)
    toggle_button = tk.Button(window, text="Toggle Gesture Recognition", command=toggle_gesture_recognition)
    button.pack()
    toggle_button.pack()
    window.mainloop()


def load_labels(filename):
    with open(filename, newline='') as file:
        reader = csv.reader(file)
        return list(reader)[0]


def normalization(landmarks):
    landmarks = np.reshape(landmarks, (1, -1))  # Zamienia tablicę 1x42 na 21x2
    mean_x = np.mean(landmarks[:, ::2], dtype=float)  # Średnia dla pierwszej kolumny
    mean_y = np.mean(landmarks[:, 1::2], dtype=float)  # Średnia dla drugiej kolumny

    normalized_landmarks = np.zeros_like(landmarks, dtype=float)

    normalized_landmarks[:, ::2] = landmarks[:, ::2] - mean_x
    normalized_landmarks[:, 1::2] = landmarks[:, 1::2] - mean_y

    return np.reshape(normalized_landmarks, (1, -1))


def predict(landmarks, model):
    landmarks = normalization(landmarks)
    prediction = model.predict(landmarks, verbose=0)
    hand_state = np.argmax(prediction)
    if hand_state == 0:
        return "CLOSE"
    elif hand_state == 1:
        return "OPEN"
    elif hand_state == 2:
        return "POINTER"
    else:
        return "NONE"


def hand_tracker(width: int, height: int):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    hand = mp_hands.Hands()

    labels = load_labels('model/landmark_data/landmark_classifier_label.csv')
    current_label = None

    with open('model/landmark_data/landmarks_data.csv', mode='a', newline='') as landmark_file:
        landmarks_writer = csv.writer(landmark_file)

        while True:
            success, frame = cap.read()
            if success:
                RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hand.process(RGB_frame)

                drawing_spec = mp_drawing.DrawingSpec(color=(189, 183, 107), thickness=2, circle_radius=1)
                if result.multi_hand_landmarks:
                    for hand_landmarks in result.multi_hand_landmarks:
                        landmarks = []
                        for idx, lm in enumerate(hand_landmarks.landmark):
                            h, w, c = frame.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            landmarks.extend([cx, cy])

                            cv2.putText(frame, f"{idx}: ({cx, cy})", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (255, 255, 255), 1, cv2.LINE_AA)

                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                                  landmark_drawing_spec=drawing_spec)

                        key = cv2.waitKey(1)
                        if key == ord('c'):
                            if current_label is not None:
                                landmarks_writer.writerow([current_label] + landmarks)
                            else:
                                print("Nie wybrano etykiety.")
                if current_label is not None:
                    cv2.putText(frame, f"Label: {current_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 255, 255), 2, cv2.LINE_AA)

                cv2.imshow("Music.", frame)

                key = cv2.waitKey(1)
                if key in range(ord('0'), ord('5')):
                    label_index = key - ord('0')
                    if label_index < len(labels):
                        current_label = labels[label_index]

                        print(f"Wybrano etykietę: {current_label}")
                    else:
                        print("Nieprawidłowy wybór etykiety.")

                if key == ord('q'):
                    break

    cap.release()
    cv2.destroyAllWindows()


def hand_tracker_img(width: int, height: int):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    hand = mp_hands.Hands()

    labels = load_labels('model/landmark_data/landmark_classifier_label.csv')
    current_label = None

    with open('model/landmark_data/landmarks_data.csv', mode='a', newline='') as landmark_file:
        landmarks_writer = csv.writer(landmark_file)

        while True:
            success, frame = cap.read()
            if success:
                RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hand.process(RGB_frame)

                drawing_spec = mp_drawing.DrawingSpec(color=(189, 183, 107), thickness=2, circle_radius=1)
                if result.multi_hand_landmarks:
                    for hand_landmarks in result.multi_hand_landmarks:
                        landmarks = []
                        for idx, lm in enumerate(hand_landmarks.landmark):
                            h, w, c = frame.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            landmarks.extend([cx, cy])

                        key = cv2.waitKey(1)
                        if key == ord('c'):
                            if current_label is not None:
                                if current_label == 'OPEN':  # open
                                    image_name = f"o_{len(os.listdir('model/landmark_data/gesture_open'))}.jpg"
                                    cv2.imwrite(os.path.join('model/landmark_data/gesture_open', image_name), frame)
                                elif current_label == 'CLOSE':  # close
                                    image_name = f"c_{len(os.listdir('model/landmark_data/gesture_close'))}.jpg"
                                    cv2.imwrite(os.path.join('model/landmark_data/gesture_close', image_name), frame)
                                elif current_label == 'POINTER':  # pointer
                                    image_name = f"p_{len(os.listdir('model/landmark_data/gesture_pointer'))}.jpg"
                                    cv2.imwrite(os.path.join('model/landmark_data/gesture_pointer', image_name), frame)

                                landmarks_writer.writerow([current_label] + landmarks)
                            else:
                                print("Nie wybrano etykiety.")
                if current_label is not None:
                    cv2.putText(frame, f"Label: {current_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 255, 255), 2, cv2.LINE_AA)

                cv2.imshow("Music.", frame)

                key = cv2.waitKey(1)
                if key in range(ord('0'), ord('5')):
                    label_index = key - ord('0')
                    if label_index < len(labels):
                        current_label = labels[label_index]

                        print(f"Wybrano etykietę: {current_label}")
                    else:
                        print("Nieprawidłowy wybór etykiety.")

                if key == ord('q'):
                    break

    cap.release()
    cv2.destroyAllWindows()


def hand_recognition(width: int, height: int):
    global gesture_recognition_active

    model = tf.keras.models.load_model('model/model_save/hand_tracking_model.keras')
    previous_mode = 'PAUSE'
    previous_gesture = 'NONE'
    gesture_sequence = []
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    mp_hands = mp.solutions.hands
    hand = mp_hands.Hands()

    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")
    prev_cx = None
    swipe_threshold = 50

    gesture_controller = GestureVoiceController()

    spotifyApi = sp.SpotifyAPI(client_id, client_secret, redirect_uri)
    Thread(target=create_button_window, args=(gesture_controller,spotifyApi)).start()

    while True:
        success, frame = cap.read()
        if success and gesture_recognition_active:
            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand.process(RGB_frame)

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                landmarks = []
                for idx, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks.extend([cx, cy])

                predict_gesture = predict(landmarks, model)
                if predict_gesture != previous_gesture:
                    current_mode = gesture_recognition(gesture_sequence, predict_gesture, previous_mode)
                    if current_mode != previous_mode:
                        if current_mode == 'PLAY' or current_mode == 'PAUSE':
                            if spotifyApi.get_current_song()['is_playing'] is True:
                                spotifyApi.pause_song()
                            else:
                                spotifyApi.resume_song()
                        previous_mode = current_mode
                    previous_gesture = predict_gesture

                cv2.putText(frame, predict_gesture, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2, cv2.LINE_AA)

                if predict_gesture == "POINTER":
                    index_tip = hand_landmarks.landmark[8]
                    h, w, c = frame.shape
                    cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                    cv2.circle(frame, (cx, cy), radius=5, color=(0, 0, 255), thickness=-1)

                    if prev_cx is not None:
                        if cx - prev_cx > swipe_threshold:
                            print("Mode: SWIPE RIGHT")
                            spotifyApi.skip_song()
                        elif prev_cx - cx > swipe_threshold:
                            print("Mode: SWIPE LEFT")
                            spotifyApi.previous_song()
                    prev_cx = cx
                if predict_gesture != "POINTER":
                    prev_cx = None

            cv2.imshow("Music.", frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


def extract_landmarks(image, hand):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    result = hand.process(image_rgb)

    landmarks = []

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                h, w, _ = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.extend([cx, cy])
    return np.array(landmarks)


def gesture_recognition(gesture_sequence, current_gesture, current_mode):
    if current_gesture in ['OPEN', 'CLOSE']:
        gesture_sequence.append(current_gesture)
    if len(gesture_sequence) > 3:
        gesture_sequence.pop(0)
    if gesture_sequence == ['OPEN', 'CLOSE', 'OPEN']:
        if current_mode == 'PLAY':
            current_mode = 'PAUSE'
        elif current_mode == 'PAUSE':
            current_mode = 'PLAY'
        gesture_sequence.clear()
    return current_mode
