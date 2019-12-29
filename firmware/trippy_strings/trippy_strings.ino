#include <Encoder.h>
#include <arduino.h>
#include "monster.h"

uint32_t off_target0 = 0;
uint32_t on_target0 = 0;
uint8_t  curr_dir = CW;
uint8_t  curr_speed = 0;

void setup() 
{
    Serial.begin(9600);

    motor_setup();
    motor_off(0); 
    motor_off(1);

    on_target0 = millis() + 100;
    //motor_on(0, CW, 64);    
    //motor_on(1, CCW, 64);
}

void loop() 
{
    //return;
    
    if (off_target0 && millis() >= off_target0)
    {
        off_target0 = 0;
        motor_off(0);
        motor_off(1);
        Serial.println("motor off");

        on_target0 = millis + 250;
    }
    if (on_target0 && millis() >= on_target0)
    {
        curr_dir = (curr_dir == CW) ? CCW : CW;
        curr_speed = 64;
        motor_on(0, curr_dir, curr_speed);
        motor_on(1, curr_dir, curr_speed);
        on_target0 = 0;
        off_target0 = millis() + 1500;
        Serial.println("motor on");
    }

    Serial.println(read_current_sense(0));
    delay(100);
}
