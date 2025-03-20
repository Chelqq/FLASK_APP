# -*- encoding: utf-8 -*-"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import serial
import time
from flask import jsonify


@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


# ⚙️ Configuración de conexión con Arduino
ARDUINO_PORT = "COM12"  # ⬅️ Cambia esto según tu sistema (Ejemplo: "COM3" en Windows, "/dev/ttyACM0" en Linux)
BAUD_RATE = 9600

try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Esperar que Arduino inicie
    print("✅ Conectado a Arduino en", ARDUINO_PORT)
except serial.SerialException:
    arduino = None
    print("⚠️ No se pudo conectar con Arduino. Verifica el puerto.")


# 📌 Lista de pines de los servos (en un Arduino Mega)
servo_pins = [i for i in range(2, 32)]  # Servos en pines 2-31

@blueprint.route('/set_servo', methods=['POST'])
def set_servo():
    try:
        # Obtener los datos del JSON
        data = request.json
        print(f"data {data}")
        servo_id = int(data['servo_id'])  # Convertir a entero
        angle = int(data['angle'])  # Convertir a entero

        # Validar que los valores sean correctos
        if not (0 <= angle <= 180):
            return jsonify({'status': 'error', 'message': 'Ángulo fuera de rango'}), 400
        if servo_id not in servo_pins:
            return jsonify({'status': 'error', 'message': 'ID de servo inválido'}), 400

        # Enviar el comando a Arduino
        command = f"{servo_id},{angle}\n"
        print(f"command {command}")
        if arduino:
            arduino.write(command.encode())  # Enviar a Arduino
            return jsonify({'status': 'success', 'servo_id': servo_id, 'angle': angle})
        else:
            return jsonify({'status': 'error', 'message': 'Arduino no conectado'}), 500

    except ValueError as e:
        return jsonify({'status': 'error', 'message': 'Datos inválidos, asegúrate de enviar números'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
