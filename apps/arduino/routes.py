# -*- encoding: utf-8 -*-

from apps.arduino import blueprint
from flask import request, jsonify
from flask_login import login_required
from apps.arduino.controller import arduino_controller

@blueprint.route('/status')
@login_required
def status():
    """Devuelve el estado de la conexión con Arduino"""
    if arduino_controller.is_connected():
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
    data = request.json or {}
    port = data.get('port', arduino_controller.port)
    baud_rate = data.get('baud_rate', arduino_controller.baud_rate)
    
    # Actualizar configuración si es necesario
    if port != arduino_controller.port:
        arduino_controller.port = port
    if baud_rate != arduino_controller.baud_rate:
        arduino_controller.baud_rate = baud_rate
    
    success = arduino_controller.connect()
    
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