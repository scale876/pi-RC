# -*- coding: utf-8 -*-

import struct
import time
import wiringpi as wp
import RPi.GPIO as GPIO

L6470_SPI_SPEED = 100000

class SteppingMotor():
    def __init__(self, channel = 0, busy = 5, speed=L6470_SPI_SPEED):
        self.channel = channel
        self.busy = busy
        wp.wiringPiSPISetup (self.channel, speed)
        self.init()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.busy, GPIO.IN)

    def write(self, data):
        data = struct.pack('B', data)
        return wp.wiringPiSPIDataRW(self.channel, data)

    def init(self):
        print('init spi %s busy %s' % (self.channel, self.busy))

        #SET MAX SPEED
        self.write(0x07)
        self.write(0x00)
        self.write(0x23)

        #SET MIN SPEED
        self.write(0x08)
        self.write(0x00)
        self.write(0x00)

        #SET KVAL_HOLD
        self.write(0x09)
        self.write(0x29)

        #SET KVAL_RUN
        self.write(0x0A)
        self.write(0x40)

        #SET KVAL_ACC
        self.write(0x0B)
        self.write(0x10)

        #SET KVAL_DEC
        self.write(0x0C)
        self.write(0x10)

        #SET OCD_TH
        self.write(0x13)
        self.write(0x0F)

        #SET STALL_TH
        self.write(0x14)
        self.write(0x7F)

        #SET STEP_MODE
        self.write(0x16)
        self.write(0x00)

        #INIT POSITION
        self.write(0xd8)

    def get_step(self, step):
        step_h = (0x3F0000 & step) >> 16
        step_m = (0x00FF00 & step) >> 8
        step_l = (0x0000FF & step)

        return step_h, step_m, step_l

    def move(self, n_step):
        if(n_step < 0):
            dir = 0x40
            step = -1 * n_step
        else:
            dir = 0x41
            step = n_step

        step_h, step_m, step_l = self.get_step(step)

        self.write(dir)

        self.write(step_h)
        self.write(step_m)
        self.write(step_l)

        while GPIO.input(self.busy) == 0:
            pass
        return

    def move_abs(self, pos):
        dir = 0x60
        step_h, step_m, step_l = self.get_step(pos)

        self.write(dir)

        self.write(step_h)
        self.write(step_m)
        self.write(step_l)
        
        while GPIO.input(self.busy) == 0:
            pass
        return

    def soft_stop(self):
        dir = 0xB0
        self.write(dir)
        return

    def softhiz(self):
        dir = 0xA8
        self.write(dir)
        return

if __name__ == '__main__':
    print('*** start spi test program ***')

    motor0 = SteppingMotor(0, 5)
    motor1 = SteppingMotor(1, 6)

    motor0.move(400)
    motor1.move(200)
    motor1.move(-100)
    motor0.move_abs(0)
    motor1.move_abs(0)

    motor0.soft_stop()
    motor0.softhiz()
    motor1.soft_stop()
    motor1.softhiz()

    GPIO.cleanup()
    quit()