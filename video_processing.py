import cv2
import mediapipe as mp

# Inicializamos MediaPipe para la estimación de pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def process_frame(frame, pose):
    """Procesa cada frame usando MediaPipe para la estimación de pose."""
    # Convertir la imagen de BGR a RGB para MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    # Dibujar la pose detectada en la imagen original (BGR)
    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    return frame

def gen_video_feed(camera_id):
    """Genera el video capturado y procesado por MediaPipe para la cámara especificada."""
    cap = cv2.VideoCapture(camera_id)

    # Crear una nueva instancia de MediaPipe Pose para esta cámara
    pose = mp_pose.Pose()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Procesar cada frame con la instancia de pose de esta cámara
        frame = process_frame(frame, pose)
        
        # Codificar la imagen a JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Devolver el frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

