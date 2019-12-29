#ifndef MONSTER_H
#define MONSTER_H

#define BRAKEVCC 0
#define CW   1
#define CCW  2
#define BRAKEGND 3
#define CS_THRESHOLD 100

#define PWM_MAX  255
#define PWM_HALF 127

void motor_setup();
uint16_t read_current_sense(int motor);
void motor_on(uint8_t motor, uint8_t direct, uint8_t pwm);
void motor_off(int motor);

#endif
