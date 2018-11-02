import RPi.GPIO as GPIO
import time

SPEED = {
    'FAST': 0,
    'SLOW': 1
}

class DcMotor:    
    def __init__(self, pin_f = 17, pin_r = 27, mode='FAST'):
        self.pin_f = pin_f
        self.pin_r = pin_r
        # TODO changeable speed
        self.mode = SPEED[mode]

        GPIO.setmode( GPIO.BCM)
        GPIO.setup(self.pin_f, GPIO.OUT)
        GPIO.setup(self.pin_r, GPIO.OUT)
        self.stop()

    def foward(self):
        GPIO.output(self.pin_f, GPIO.HIGH)
        GPIO.output(self.pin_r, GPIO.LOW)
        return
    
    def back(self):
        GPIO.output(self.pin_f, GPIO.LOW)
        GPIO.output(self.pin_r, GPIO.HIGH)
        return   

    def stop(self):
        GPIO.output(self.pin_f, GPIO.LOW)
        GPIO.output(self.pin_r, GPIO.LOW)
        return

if __name__ == '__main__':
    dc = DcMotor(17, 27)
    while True:
        print('go foward')
        dc.foward()
        time.sleep(1)
        break

    while True:
        print('go back')
        dc.back()
        time.sleep(1)
        break
    GPIO.cleanup()
    quit()