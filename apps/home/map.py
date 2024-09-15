from flask import Flask, Response, render_template
import cv2
# Inicializa las dos cámaras
cam_0 = cv2.VideoCapture(0)  # Webcam integrada
cam_1 = cv2.VideoCapture(1)  # Webcam USB

def generate_frames(camera):
    while True:
        # Lee el frame desde la cámara
        success, frame = camera.read()
        if not success:
            break
        else:
            # Codifica el frame como JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Genera el flujo de bytes para transmitir
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Página principal
    return "Página principal"

@app.route('/map')
def body_control():
    # Ruta para la página que muestra las cámaras
    return render_template('map.html')

@app.route('/video_feed_0')
def video_feed_0():
    # Genera el feed de la webcam 0
    return Response(generate_frames(cam_0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_1')
def video_feed_1():
    # Genera el feed de la webcam 1
    return Response(generate_frames(cam_1), mimetype='multipart/x-mixed-replace; boundary=frame')
