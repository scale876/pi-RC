import RPi.GPIO as GPIO
import time

ARM_STATE = {
    'OPEN': 0,
    'CLOSE': 1
}

class ServoMotor():
    def __init__(self, pin, state = 'OPEN', hz = 50):
        self.pin = pin
        GPIO.setmode( GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.servo = GPIO.PWM(self.pin, hz)
        self.state = ARM_STATE[state]
        self.servo.start(0)

    def open(self):
        if self.state == ARM_STATE['OPEN']:
            return
        self.servo.ChangeDutyCycle(2.5)
        self.state = ARM_STATE['OPEN']
        return

    def close(self):
        if self.state == ARM_STATE['CLOSE']:
            return
        self.servo.ChangeDutyCycle(10)
        self.state = ARM_STATE['CLOSE']
        return

    def stop(self):
        self.servo.stop()
        return

if __name__ == '__main__':
    servo = ServoMotor(18)
    servo.servo.start(0)
    print('init servo state %s' % servo.state)
    servo.open()
    print('open servo state %s' % servo.state)
    servo.close()
    print('close servo state %s' % servo.state)
    servo.open()
    print('open servo state %s' % servo.state)
    servo.servo.stop()
    GPIO.cleanup()
