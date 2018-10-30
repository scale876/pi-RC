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
    g_mode = rcTypes.MODE['FREE']

def controller_main():
    print('success')
    pygame.init()
    vMotor = steppingMotor.SteppingMotor(0, 5)
    hMotor = steppingMotor.SteppingMotor(1, 6)
    armMotor = servoMotor.ServoMotor(18)
    while True:
        eventlist = pygame.event.get()
        eventlist = filter(lambda e : e.type == pygame.locals.JOYBUTTONDOWN , eventlist)
        eventlist = map(lambda x : x.button,eventlist)
        if eventlist:

            if g_mode != rcTypes.MODE['FREE']:
                print('That operation is not allowed!!')    
                continue
            
            if 0 in eventlist:
                threading.Thread(target=action_servo, args=([armMotor])).start()
            elif 1 in eventlist:
                threading.Thread(target=move_stepping, args=([vMotor, 400])).start()
                #vMotor.move(400)
            elif 2 in eventlist:
                threading.Thread(target=move_stepping, args=([hMotor, 200])).start()
                #hMotor.move(200)
            elif 3 in eventlist:
                threading.Thread(target=do_store, args=([armMotor, vMotor, hMotor])).start()

        pygame.time.wait(10)

if __name__ == '__main__':
    pygame_init()