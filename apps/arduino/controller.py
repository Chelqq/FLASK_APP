# -*- encoding: utf-8 -*-

import serial
import time
import threading
import logging
import serial.tools.list_ports  # Add this for port enumeration

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
        
        # Don't try to connect at init time, just setup
        logger.info(f"ArduinoController initialized with port={port}, baud_rate={baud_rate}")

    def get_available_ports(self):
        """Returns a list of available serial ports"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid
            })
        return ports

    def connect(self, retries=3, delay=0.5):
        """Intenta conectar con Arduino con reintentos"""
        if not self.port:
            logger.error("No se especificó ningún puerto")
            return False
            
        logger.info(f"Intentando conectar a Arduino en {self.port} (baud_rate={self.baud_rate})")
        
        # List available ports to help debugging
        available_ports = self.get_available_ports()
        if available_ports:
            logger.info(f"Puertos disponibles: {available_ports}")
        else:
            logger.warning("No se encontraron puertos seriales disponibles")
            
        for attempt in range(retries):
            try:
                logger.info(f"Intento de conexión {attempt+1}/{retries}")
                
                # Make sure port is closed before trying
                with self.lock:
                    if self.arduino:
                        try:
                            self.arduino.close()
                        except:
                            pass
                        self.arduino = None
                
                # Open new connection
                with self.lock:
                    self.arduino = serial.Serial(self.port, self.baud_rate, timeout=2)
                    # Add a delay to give Arduino time to reset after connection
                    time.sleep(2)  # Esperar que Arduino inicie
                
                # Try a simple command to test connection
                test_result = self._test_connection()
                if test_result:
                    self.connected = True
                    logger.info(f"✅ Conectado a Arduino en {self.port}")
                    return True
                else:
                    logger.warning("La conexión no respondió a la prueba")
                    
            except serial.SerialException as e:
                self.arduino = None
                self.connected = False
                logger.error(f"⚠️ Error de conexión en intento {attempt+1}: {str(e)}")
                print(f"⚠️ Error de conexión en intento {attempt+1}: {str(e)}")
                time.sleep(delay)  # Wait before retry
                
        logger.error(f"⚠️ No se pudo conectar con Arduino después de {retries} intentos")
        return False

    def _test_connection(self):
        """Send a simple command to test if Arduino is responding"""
        try:
            # Send a neutral command (move servo 2 to its current position)
            with self.lock:
                if not self.arduino or not self.arduino.is_open:
                    return False
                
                # Flush buffers
                self.arduino.reset_input_buffer()
                self.arduino.reset_output_buffer()
                
                # Send test command
                test_cmd = "2,90\n"
                self.arduino.write(test_cmd.encode())
                
                # Wait for response with timeout
                start_time = time.time()
                while (time.time() - start_time) < 1.0:  # 1 second timeout
                    if self.arduino.in_waiting > 0:
                        response = self.arduino.readline().decode().strip()
                        logger.info(f"Arduino respondió: {response}")
                        return True
                    time.sleep(0.1)
                    
                logger.warning("Arduino no respondió a la prueba en el tiempo esperado")
                return False
                
        except Exception as e:
            logger.error(f"Error durante prueba de conexión: {str(e)}")
            return False

    def disconnect(self):
        """Cierra la conexión con Arduino"""
        with self.lock:
            if self.arduino and self.arduino.is_open:
                self.arduino.close()
                self.connected = False
                logger.info("Desconectado de Arduino")

    def is_connected(self):
        """Verifica si la conexión está activa"""
        with self.lock:
            connected = self.connected and self.arduino and self.arduino.is_open
        return connected

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
                # Wait brief time for response
                time.sleep(0.1)
                if self.arduino.in_waiting > 0:
                    response = self.arduino.readline().decode().strip()
                    logger.debug(f"Respuesta Arduino: {response}")
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
        
    def get_diagnostics(self):
        """Returns diagnostic information about the controller"""
        diagnostics = {
            "configuracion_actual": {
                "puerto_configurado": self.port if self.port else "No configurado",
                "baud_rate": self.baud_rate,
                "estado_conexion": "Conectado" if self.is_connected() else "Desconectado"
            },
            "puertos_disponibles": self.get_available_ports(),
            "info_adicional": {}
        }
        
        return diagnostics

# Singleton para usar en toda la aplicación
arduino_controller = None
def init_arduino(port="COM12", baud_rate=9600):
    """Inicializa el controlador de Arduino como singleton"""
    global arduino_controller
    try:
        if arduino_controller is None:
            logger.info(f"Inicializando ArduinoController con port={port}, baud_rate={baud_rate}")
            arduino_controller = ArduinoController(port, baud_rate)
            
            # Try to connect immediately once during initialization
            if port:
                connect_result = arduino_controller.connect()
                logger.info(f"Resultado de conexión inicial: {'Éxito' if connect_result else 'Falló'}")
            
        return arduino_controller
    except Exception as e:
        logger.error(f"Error al inicializar ArduinoController: {str(e)}")
        return None