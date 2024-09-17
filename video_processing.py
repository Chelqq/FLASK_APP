# video_processing.py
import cv2
import mediapipe as mp

# Inicializamos MediaPipe para la detección de manos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

def process_frame(frame):
    """Procesa cada frame usando MediaPipe para la detección de manos."""
    # Convertir la imagen de BGR a RGB para MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # Dibujar las manos detectadas en la imagen original (BGR)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    return frame

def gen_video_feed(camera_id):
    """Genera el video capturado y procesado por MediaPipe para la cámara especificada."""
    cap = cv2.VideoCapture(camera_id)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Procesar cada frame con MediaPipe
        frame = process_frame(frame)
        
        # Codificar la imagen a JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Devolver el frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
