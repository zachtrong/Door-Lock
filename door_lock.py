#       _                         
#      | |                        
#   ___| |_ _ __ ___  _ __   __ _ 
#  |_  / __| '__/ _ \| '_ \ / _` |
#   / /| |_| | | (_) | | | | (_| |
#  /___|\__|_|  \___/|_| |_|\__, |
#                            __/ |
#                           |___/ 

import RPi.GPIO as GPIO
import time
import hashlib
from threading import Thread

class DoorLock(object):
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        self.KEYPAD = [
                ['1', '2', '3', 'A'],
                ['4', '5', '6', 'B'],
                ['7', '8', '9', 'C'],
                ['*', '0', '#', 'D']]

        self.ROW = [31, 33, 35, 37] 
        self.COL = [32, 36, 38, 40]

        self.button_out = 16
        self.button_in = 18
        
        self.pushed = []
        
        #hehe
        #encrypt_password = trash_key + password + trash_key        
        self.encrypt_password = 'your sha256 encrypted password here'

        self.trash_key = 'dvfzpkosgjribcauqnelyxmhtw'
        self.len_password = 6

        #delay each click
        self.delay_time = 0.3

        #for open in first runtime
        self.is_open = False


    #percent 0.5 / 20
    #pwm.ChangeDutyCycle(2.5)
    #time.sleep(1)
    #percent 1.5 / 20
    #pwm.ChangeDutyCycle(7.5)
    #time.sleep(1)
    #percent 2.5 / 20
    #pwm.ChangeDutyCycle(12.5)
    #time.sleep(1)


    def check_pass(self, password):
        
        password = ''.join(password)

        my_hash = hashlib.sha256()
        my_hash.update(self.trash_key + password + self.trash_key)

        encrypt = my_hash.hexdigest()

        return encrypt == self.encrypt_password
        

    def control_open(self):

        #for pwm
        if self.is_open:
            return

        self.is_open = True

        pwm = GPIO.PWM(12, 50)

        pwm.start(2.5)
        time.sleep(2)
        pwm.stop()

    def control_close(self):
        
        #for pwm
        if not self.is_open:
            return

        self.is_open = False

        pwm = GPIO.PWM(12, 50)
        
        pwm.start(12.5)
        time.sleep(2)
        pwm.stop()

    def process(self, key):
        print key
        if (key == '*'):
            #reset

            print "Clear..."
            self.pushed = []

            #time.sleep(delay_time)
            return
        
        if (key == '#'):
            #close door

            print "Closing..."
            self.pushed = []
            self.control_close()
            return

        self.pushed.append(key)

        if len(self.pushed) == self.len_password:
            if self.check_pass(self.pushed):
                #open door
                print "Openning..."
                self.control_open()
            else:
                print "Wrong password"
                #no brute-force :)
                time.sleep(self.delay_time)

            self.pushed = []
            #time.sleep(delay_time)
            return

        #time.sleep(delay_time)

    def process_channel(self, channel):

        #dunno why it has multiple thread
        if GPIO.input(channel) != 0:
            return

        print "you press channel:", channel
        if channel == self.button_in:
            if not self.is_open:
                self.control_open()
            else:
                self.control_close()

            print "done!"
            return

        #check matrix

        row = None
        col = None

        for i in xrange(len(self.ROW)):
            if self.ROW[i] == channel:
                row = i

        if row == None:
            return

        for i in xrange(len(self.COL)):
            GPIO.setup(self.COL[i], GPIO.HIGH)
            if GPIO.input(channel) == GPIO.HIGH:
                col = i
            GPIO.setup(self.COL[i], GPIO.LOW)
                
        if col == None:
            return

        self.process(self.KEYPAD[row][col])


    def setup(self):

        #pwm of motor
        GPIO.setup(12, GPIO.OUT)

        self.control_open()

        #for matrix
        GPIO.setup(self.COL, GPIO.OUT)
        GPIO.output(self.COL, GPIO.LOW)

        GPIO.setup(self.ROW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for row in self.ROW:
            GPIO.add_event_detect(row, GPIO.FALLING, 
                    callback=self.process_channel, bouncetime=300)
        
        #for button

        GPIO.setup(self.button_out, GPIO.OUT)
        GPIO.setup(self.button_out, GPIO.LOW)

        GPIO.setup(self.button_in, GPIO.IN, pull_up_down=GPIO.PUD_UP)


        GPIO.add_event_detect(self.button_in, GPIO.FALLING,
                callback=self.process_channel, bouncetime=300)
def main():
    my_door_lock = DoorLock()
    my_door_lock.setup()

    #sleep 
    time.sleep(1000)

if __name__ == '__main__':
    try:
        main()
    finally:
        GPIO.cleanup()
