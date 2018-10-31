# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import time
import servoMotor
import steppingMotor
import threading
import rcTypes

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

def controller_main():
    print('success')
    global g_motor_position
    pygame.init()
    vMotor = steppingMotor.SteppingMotor(0, 5)
    hMotor = steppingMotor.SteppingMotor(1, 6)
    armMotor = servoMotor.ServoMotor(18)
    hold_button = []
    while True:
        eventlist = pygame.event.get()
        down_button = filter(lambda e : e.type == pygame.locals.JOYBUTTONDOWN, eventlist)
        down_button = map(lambda x : x.button, down_button)

        up_button = filter(lambda e : e.type == pygame.locals.JOYBUTTONUP, eventlist)
        up_button = map(lambda x : x.button, up_button)

        if g_mode != rcTypes.MODE['FREE']:
            print('That operation is not allowed!!')    
            continue

        if down_button:
            print 'down %s' % down_button
            if 0 in down_button:
                threading.Thread(target=action_servo, args=([armMotor])).start()
            elif 1 in down_button:
                threading.Thread(target=move_stepping, args=([vMotor, 400])).start()
                #vMotor.move(400)
            elif 2 in down_button:
                threading.Thread(target=move_stepping, args=([hMotor, 200])).start()
                #hMotor.move(200)
            elif 3 in down_button:
                threading.Thread(target=do_store, args=([armMotor, vMotor, hMotor])).start()
            elif 4 in down_button:
                if not 4 in hold_button:
                    print 'append'
                    hold_button.append(4)
            elif 5 in down_button:
                if not 5 in hold_button:
                    print 'append'
                    hold_button.append(5)

        if up_button:
            print 'up %s' % up_button
            if 4 in up_button:
                if 4 in hold_button:
                    hold_button.remove(4)
            elif 5 in up_button:
                if 4 in hold_button:
                    hold_button.remove(5)

        if hold_button:
            print 'hold %s' % hold_button
            if 4 in hold_button:
                g_motor_position += 5
                if g_motor_position > rcTypes.VERTICAL_THRETHOLD['MAX']:
                    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MAX']
                vMotor.move_abs(g_motor_position)
            elif 5 in hold_button:
                g_motor_position -= 5
                if g_motor_position < rcTypes.VERTICAL_THRETHOLD['MIN']:
                    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MIN']
                vMotor.move_abs(g_motor_position)

        pygame.time.wait(10)

if __name__ == '__main__':
    pygame_init()