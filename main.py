import cv2
import mediapipe as mp
from tkinter import Tk, Label, Entry, Button
import time

# Настройка медиапайпа
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Интерфейс приложения
root = Tk()
root.title(" ")
input_field = Entry(root, font=("Arial", 24), width=20)
input_field.pack(pady=20)
current_letter_label = Label(root, text="A", font=("Arial", 48))
current_letter_label.pack(pady=20)

# Переменные
letters = list("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЭЮЯ")
current_index = 0
input_text = ""
last_action_time = 0
DELAY = 0.7  # Задержка 500 мс

# Управление жестами
def process_gesture(landmarks):
    global current_index, input_text, last_action_time
    current_time = time.time()
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    # Функция для проверки сгибания пальцев
    def is_finger_bent(finger_tip, finger_base):
        return finger_tip.y > finger_base.y

    # Проверка сгибания большого пальца по оси X
    def is_thumb_bent():
        return thumb_tip.x > landmarks[3].x  # Сгибание по X

    # Проверка жеста сохранения
    def is_save_gesture():
        return all(is_finger_bent(tip, base) for tip, base in zip([index_tip, middle_tip, ring_tip, pinky_tip], [landmarks[6], landmarks[10], landmarks[14], landmarks[18]])) and is_thumb_bent()

    # Жесты
    if current_time - last_action_time > DELAY:
        # Жест "Подтверждение"
        if is_save_gesture():
            input_text += letters[current_index]
            input_field.delete(0, 'end')
            input_field.insert(0, input_text)
            print(f"Жест сохранения: Текущий текст: {input_text}")
            last_action_time = current_time
        # Жест "Вперед"
        elif is_thumb_bent() and not is_save_gesture():
            current_index = (current_index + 1) % len(letters)
            print("Жест вперед: Переход к следующей букве")
            last_action_time = current_time
        # Жест "Назад"
        elif all(is_finger_bent(tip, base) for tip, base in zip([index_tip, middle_tip, ring_tip, pinky_tip], [landmarks[6], landmarks[10], landmarks[14], landmarks[18]])):
            current_index = (current_index - 1) % len(letters)
            print("Жест назад: Переход к предыдущей букве")
            last_action_time = current_time


    current_letter_label.config(text=letters[current_index])

# Основной цикл
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            process_gesture(hand_landmarks.landmark)

    cv2.imshow("cam", frame)
    root.update()  # Обновление интерфейса

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
