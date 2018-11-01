# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import time
import servoMotor
import steppingMotor
import threading
import rcTypes
import dcMotor

g_machine_state = rcTypes.MACHINE_STATE['INITIAL']
g_target_num = 0
g_mode = rcTypes.MODE['FREE']
g_motor_position = 0

def pygame_init():
    pygame.joystick.init()
    print('try get joystick')
    try:
        print pygame.joystick.get_count()
        joys = pygame.joystick.Joystick(0)
        joys.init()
        controller_main()
    except pygame.error:
        print 'error has occured'
        pygame.joystick.quit()
        time.sleep(1)
        pygame_init()

def action_servo(servo):
    servo.close()
    servo.open()

def move_stepping(stepping, step):
    stepping.move(step)

def do_store(arm, vertical, horizontal):
    global g_machine_state
    global g_target_num
    global g_mode
    global g_motor_position

    if arm.state == servoMotor.ARM_STATE['OPEN']:
        return

    g_mode = rcTypes.MODE['STORE']

    vertical.move_abs(200)
    horizontal.move_abs(400)
    vertical.move_abs(0)
    arm.open()
    arm.close()
    vertical.move_abs(200)
    horizontal.move_abs(0)
    arm.open()

    g_target_num += 1
    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MAX']
    g_mode = rcTypes.MODE['FREE']

def do_carryout(arm, vertical, horizontal):
    global g_machine_state
    global g_target_num
    global g_mode
    global g_motor_position

    if arm.state ==servoMotor.ARM_STATE['CLOSE']:
        return

    g_mode = rcTypes.MODE['CARRY_OUT']
    arm.close()
    vertical.move_abs(200)
    horizontal.move_abs(400)
    arm.open()
    vertical.move_abs(0)
    arm.close()
    vertical.move_abs(200)
    horizontal.move_abs(0)

    g_target_num -= 1
    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MAX']
    g_mode = rcTypes.MODE['FREE']

def move_dc_motor(dc, vaxis):
    if vaxis > 30:
        dc.foward()
    elif vaxis < -30:
        dc.back()
    else:
        dc.stop()


def controller_main():
    print('success')
    global g_motor_position
    pygame.init()
    v_motor = steppingMotor.SteppingMotor(0, 5)
    h_motor = steppingMotor.SteppingMotor(1, 6)
    arm_motor = servoMotor.ServoMotor(18)
    left_motor = dcMotor.DcMotor(17, 27)
    right_motor = dcMotor.DcMotor(23, 24)
    hold_button = []
    while True:
        eventlist = pygame.event.get()
        down_button = filter(lambda e : e.type == pygame.locals.JOYBUTTONDOWN, eventlist)
        down_button = map(lambda x : x.button, down_button)

        up_button = filter(lambda e : e.type == pygame.locals.JOYBUTTONUP, eventlist)
        up_button = map(lambda x : x.button, up_button)
        joys = pygame.joystick.Joystick(0)
        left_vaxis = joys.get_axis(1) * 100
        right_vaxis = joys.get_axis(3) * 100

        move_dc_motor(left_motor, left_vaxis)
        move_dc_motor(right_motor, right_vaxis)

        if up_button:
            print 'up %s' % up_button
            if 4 in up_button:
                if 4 in hold_button:
                    hold_button.remove(4)
            elif 5 in up_button:
                if 4 in hold_button:
                    hold_button.remove(5)

        if g_mode != rcTypes.MODE['FREE']:
            continue

        if down_button:
            print 'down %s' % down_button
            if 0 in down_button:
                threading.Thread(target=action_servo, args=([arm_motor])).start()
            elif 1 in down_button:
                threading.Thread(target=move_stepping, args=([v_motor, 400])).start()
                #v_motor.move(400)
            elif 2 in down_button:
                threading.Thread(target=move_stepping, args=([h_motor, 200])).start()
                #h_motor.move(200)
            elif 3 in down_button:
                threading.Thread(target=do_store, args=([arm_motor, v_motor, h_motor])).start()
            elif 4 in down_button:
                if not 4 in hold_button:
                    print 'append'
                    hold_button.append(4)
            elif 5 in down_button:
                if not 5 in hold_button:
                    print 'append'
                    hold_button.append(5)

        if hold_button:
            print 'hold %s' % hold_button
            if 4 in hold_button:
                g_motor_position += 5
                if g_motor_position > rcTypes.VERTICAL_THRETHOLD['MAX']:
                    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MAX']
                v_motor.move_abs(g_motor_position)
            elif 5 in hold_button:
                g_motor_position -= 5
                if g_motor_position < rcTypes.VERTICAL_THRETHOLD['MIN']:
                    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MIN']
                v_motor.move_abs(g_motor_position)

        pygame.time.wait(10)

if __name__ == '__main__':
    pygame_init()