#include <Encoder.h>
#include <arduino.h>
#include "monster.h"

void setup() 
{
    Serial.begin(115200);
    motor_setup();
    motor_off(0); 
    motor_off(1);
}

void loop() 
{
    char ch;
    int  d;
    
    if (Serial.available() > 0) 
    {
        ch = Serial.read();
        if (ch == 10)
        {
            int8_t motor;
            int16_t speed;

            motor = buf[0] - '0';
            speed = atoi(buf + 1);
            if (speed < -255 || speed > 255 or motor < 0 or motor > 1)
                Serial.println("?");
            else
            {
                if (speed < 0)
                    dir = CCW
                else
                    dir = CW

                if (speed == 0)
                    motor_off(motor)
                else
                    motor_on(motor, dir, (uint8_t)abs(speed));

                Serial.print(motor);
                Serial.print(" ");
                Serial.print(dir);
                Serial.print(" ");
                Serial.println(abs(speed));
            }
            buf[0] = 0;
            buf_index = 0;
        }
        else
        {
            buf[buf_index] = ch;
            buf_index++;
            buf[buf_index] = 0;
        }
    }
}

