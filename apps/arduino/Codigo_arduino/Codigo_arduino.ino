#include <Servo.h>

Servo servos[30];  // Array para 30 servos
int servo_pins[30] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39};

void setup() {
    Serial.begin(9600);  // Inicializar comunicación serial

    // Asociar los pines con los servos
    for (int i = 0; i < 30; i++) {
        servos[i].attach(servo_pins[i]);
        servos[i].write(0);  // Inicializar servos en 90°
    }

    Serial.println("Listo para recibir comandos.");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');  // Leer comando
        command.trim();

        int commaIndex = command.indexOf(',');  // Buscar la coma que separa los valores
        if (commaIndex > 0) {
            int servo_id = command.substring(0, commaIndex).toInt();
            int angle = command.substring(commaIndex + 1).toInt();

            if (servo_id >= 2 && servo_id <= 31 && angle >= 0 && angle <= 180) {
                int servo_index = servo_id - 2;  // Convertir pin a índice en array
                servos[servo_index].write(angle);
                Serial.print("Servo ");
                Serial.print(servo_id);
                Serial.print(" ajustado a ");
                Serial.print(angle);
                Serial.println("°");
            }
        }
    }
}
