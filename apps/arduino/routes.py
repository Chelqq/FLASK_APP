# -*- encoding: utf-8 -*-

from apps.arduino import blueprint
from flask import request, jsonify
from flask_login import login_required
from apps.arduino.controller import arduino_controller, init_arduino
import serial
import serial.tools.list_ports

@blueprint.route('/status')
@login_required
def status():
    """Devuelve el estado de la conexión con Arduino"""
    # Ensure controller is initialized
    if arduino_controller is None:
        init_arduino()
        
    if arduino_controller and arduino_controller.is_connected():
        return jsonify({
            'status': 'connected',
            'port': arduino_controller.port
        })
    else:
        return jsonify({
            'status': 'disconnected'
        })

@blueprint.route('/connect', methods=['POST'])
@login_required
def connect():
    """Intenta conectar con Arduino"""
    # Ensure controller is initialized
    if arduino_controller is None:
        init_arduino()
        
    data = request.json or {}
    
    if arduino_controller is None:
        # If still None after init attempt, use defaults
        port = data.get('port', 'COM12')
        baud_rate = data.get('baud_rate', 9600)
        # Try to initialize with the given port
        init_arduino(port=port, baud_rate=baud_rate)
    else:
        # Normal case - controller exists
        port = data.get('port', arduino_controller.port)
        baud_rate = data.get('baud_rate', arduino_controller.baud_rate)
        
        # Update settings if needed
        if port != arduino_controller.port:
            arduino_controller.port = port
        if baud_rate != arduino_controller.baud_rate:
            arduino_controller.baud_rate = baud_rate
    
    # Try to connect
    success = arduino_controller.connect() if arduino_controller else False
    
    if success:
        return jsonify({
            'status': 'success',
            'message': f'Conectado a Arduino en {port}'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No se pudo conectar con Arduino'
        }), 500

@blueprint.route('/set_servo', methods=['POST'])
@login_required
def set_servo():
    """Controla un servo específico"""
    try:
        # Ensure controller is initialized
        if arduino_controller is None:
            init_arduino()
            
        # If still None, return error
        if arduino_controller is None:
            return jsonify({
                'status': 'error',
                'message': 'Arduino controller not initialized'
            }), 500
            
        # Obtener los datos del JSON
        data = request.json
        servo_id = int(data['servo_id'])
        angle = int(data['angle'])
        
        success, message = arduino_controller.set_servo(servo_id, angle)
        
        if success:
            return jsonify({
                'status': 'success',
                'servo_id': servo_id,
                'angle': angle,
                'message': message
            })
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
            
    except ValueError as e:
        return jsonify({
            'status': 'error', 
            'message': 'Datos inválidos, asegúrate de enviar números'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500

@blueprint.route('/reset_servos', methods=['POST'])
@login_required
def reset_servos():
    """Resetea todos los servos a posición central"""
    # Ensure controller is initialized
    if arduino_controller is None:
        init_arduino()
        
    # If still None, return error
    if arduino_controller is None:
        return jsonify({
            'status': 'error',
            'message': 'Arduino controller not initialized'
        }), 500
        
    success, messages = arduino_controller.reset_servos()
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Todos los servos han sido reseteados'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Error al resetear algunos servos',
            'details': messages
        }), 500
        
        
        import serial.tools.list_ports

@blueprint.route('/diagnostico')
@login_required
def diagnostico():
    """Diagnóstico de puertos y conexión Arduino"""
    try:
        # Importar módulo serial si no está importado
        import serial
        import serial.tools.list_ports
        
        # Buscar puertos disponibles
        puertos = []
        for p in serial.tools.list_ports.comports():
            puertos.append({
                'dispositivo': p.device,
                'descripcion': p.description,
                'hwid': p.hwid
            })
        
        # Verificar configuración actual
        config_actual = {
            'puerto_configurado': arduino_controller.port if arduino_controller else 'No inicializado',
            'baud_rate': arduino_controller.baud_rate if arduino_controller else 'No inicializado',
            'estado_conexion': 'Conectado' if (arduino_controller and arduino_controller.is_connected()) else 'Desconectado'
        }
        
        # Intentar información adicional
        info_adicional = {}
        if arduino_controller and arduino_controller.arduino:
            try:
                info_adicional['arduino_abierto'] = arduino_controller.arduino.is_open
                info_adicional['arduino_nombre'] = arduino_controller.arduino.name
                info_adicional['arduino_timeout'] = arduino_controller.arduino.timeout
            except Exception as e:
                info_adicional['error'] = f'No se pudo obtener información adicional: {str(e)}'
        
        # Verificar instalación de pyserial
        import pkg_resources
        pyserial_version = pkg_resources.get_distribution("pyserial").version
        
        return jsonify({
            'pyserial_version': pyserial_version,
            'puertos_disponibles': puertos,
            'configuracion_actual': config_actual,
            'info_adicional': info_adicional
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': error_trace
        }), 500

# Add to your arduino/routes.py

@blueprint.route('/diagnostics')
@login_required
def diagnostics():
    """Returns detailed diagnostic information"""
    # Ensure controller is initialized
    if arduino_controller is None:
        init_arduino()
        
    if arduino_controller is None:
        return jsonify({
            'status': 'error',
            'message': 'No se pudo inicializar el controlador de Arduino'
        })
    
    # Get diagnostic information
    diagnostics = arduino_controller.get_diagnostics()
    
    # Add pyserial version
    import serial
    diagnostics['pyserial_version'] = serial.__version__
    
    return jsonify(diagnostics)