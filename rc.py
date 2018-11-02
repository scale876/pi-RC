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

def do_store(arm, vertical, horizontal):
    global g_machine_state
    global g_target_num
    global g_mode
    global g_motor_position

    if arm.state == servoMotor.ARM_STATE['OPEN']:
        print('please close arm.')
        return

    g_mode = rcTypes.MODE['STORE']

    time.sleep(0.2)
    
    vertical.move_abs(200)
    time.sleep(0.1)
    horizontal.move_abs(400)
    time.sleep(0.1)
    vertical.move_abs(0)
    time.sleep(0.1)
    arm.open()
    arm.close()
    vertical.move_abs(200)
    time.sleep(0.1)
    horizontal.move_abs(0)
    time.sleep(0.1)
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
        print('please open arm.')
        return
    g_mode = rcTypes.MODE['CARRY_OUT']
    
    time.sleep(0.2)
    arm.close()
    vertical.move_abs(200)
    time.sleep(0.1)
    horizontal.move_abs(400)
    time.sleep(0.1)
    arm.open()
    vertical.move_abs(0)
    time.sleep(0.1)
    arm.close()
    vertical.move_abs(200)
    time.sleep(0.1)
    horizontal.move_abs(0)
    time.sleep(0.1)

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
    ps3 = rcTypes.PS3
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
            if ps3['up'] in up_button and ps3['up'] in hold_button:
                    hold_button.remove(ps3['up'])
            if ps3['down'] in up_button and ps3['down'] in hold_button:
                    hold_button.remove(ps3['down'])

        if g_mode != rcTypes.MODE['FREE']:
            hold_buttonb = []
            continue

        if down_button:
            print 'down %s' % down_button
            if ps3['sankaku'] in down_button:
                make_thread(target=do_store, data=[arm_motor, v_motor, h_motor])
            elif ps3['shikaku'] in down_button:
                make_thread(target=do_carryout, data=[arm_motor, v_motor, h_motor])
            elif ps3['maru'] in down_button:
                make_thread(target=arm_motor.open)
            elif ps3['batsu'] in down_button:
                make_thread(target=arm_motor.close)
            elif ps3['up'] in down_button:
                if not ps3['up'] in hold_button:
                    hold_button.append(ps3['up'])
            elif ps3['down'] in down_button:
                if not ps3['down'] in hold_button:
                    hold_button.append(ps3['down'])

        if hold_button:
            print 'hold %s' % hold_button
            if ps3['up'] in hold_button:
                g_motor_position += 5
                if g_motor_position > rcTypes.VERTICAL_THRETHOLD['MAX']:
                    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MAX']
                make_thread(target=v_motor.move_abs, data=[g_motor_position])
            elif ps3['down'] in hold_button:
                g_motor_position -= 5
                if g_motor_position < rcTypes.VERTICAL_THRETHOLD['MIN']:
                    g_motor_position = rcTypes.VERTICAL_THRETHOLD['MIN']
                make_thread(target=v_motor.move_abs, data=[g_motor_position])

        pygame.time.wait(100)

# FIXME スレッドの最大値を制御する方法がわからなかったのでゴリ押し。いつか直す。
def make_thread(target, data=None):
    if threading.active_count() > 1:
        return
    if isinstance(data, list):
        threading.Thread(target=target, args=(data)).start()
    else:
        threading.Thread(target=target).start()

if __name__ == '__main__':
    pygame_init()