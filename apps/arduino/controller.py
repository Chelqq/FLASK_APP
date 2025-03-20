# -*- encoding: utf-8 -*-

import serial
import time
import threading
import logging

logger = logging.getLogger(__name__)

class ArduinoController:
    def __init__(self, port=None, baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.arduino = None
        self.connected = False
        self.lock = threading.Lock()  # Para asegurar operaciones thread-safe
        # Lista de pines de los servos (en un Arduino Mega)
        self.servo_pins = [i for i in range(2, 32)]  # Servos en pines 2-31
        self.connect()

    def connect(self):
        """Intenta conectar con Arduino"""
        if self.port:
            try:
                with self.lock:
                    self.arduino = serial.Serial(self.port, self.baud_rate, timeout=1)
                    time.sleep(2)  # Esperar que Arduino inicie
                self.connected = True
                logger.info(f"✅ Conectado a Arduino en {self.port}")
                return True
            except serial.SerialException as e:
                self.arduino = None
                self.connected = False
                logger.error(f"⚠️ No se pudo conectar con Arduino: {str(e)}")
                return False
        return False

    def disconnect(self):
        """Cierra la conexión con Arduino"""
        with self.lock:
            if self.arduino and self.arduino.is_open:
                self.arduino.close()
                self.connected = False

    def is_connected(self):
        """Verifica si la conexión está activa"""
        return self.connected and self.arduino and self.arduino.is_open

    def set_servo(self, servo_id, angle):
        """Mueve un servo a una posición específica"""
        # Validar que los valores sean correctos
        if not (0 <= angle <= 180):
            return False, "Ángulo fuera de rango (0-180)"
        if servo_id not in self.servo_pins:
            return False, f"ID de servo inválido, debe estar entre {min(self.servo_pins)} y {max(self.servo_pins)}"

        # Enviar el comando a Arduino
        command = f"{servo_id},{angle}\n"
        logger.debug(f"Enviando comando: {command}")
        
        with self.lock:
            if not self.is_connected():
                if not self.connect():
                    return False, "Arduino no conectado"
            
            try:
                self.arduino.write(command.encode())  # Enviar a Arduino
                # Opcional: leer respuesta de Arduino
                # response = self.arduino.readline().decode().strip()
                return True, f"Servo {servo_id} movido a posición {angle}"
            except Exception as e:
                logger.error(f"Error enviando comando: {str(e)}")
                return False, f"Error: {str(e)}"

    def reset_servos(self):
        """Resetea todos los servos a posición central"""
        success = True
        messages = []
        
        for servo_id in self.servo_pins:
            result, message = self.set_servo(servo_id, 90)
            if not result:
                success = False
            messages.append(message)
            
        return success, messages

# Singleton para usar en toda la aplicación
arduino_controller = None

def init_arduino(port=None, baud_rate=9600):
    """Inicializa el controlador de Arduino como singleton"""
    global arduino_controller
    if arduino_controller is None:
        arduino_controller = ArduinoController(port, baud_rate)
    return arduino_controller