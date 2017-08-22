#!/usr/bin/env python3
import RPi.GPIO as control
import datetime
import time
import os
from os import path
from time import localtime, strftime
import Adafruit_CharLCD as LCD
import Adafruit_BMP.BMP085 as BMP085
on_time = 6
off_time = 20

# Buttons on LCD 1
#buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
#            (LCD.LEFT,   'Left'  , (1,0,0)),
#            (LCD.UP,     'Up'    , (0,0,1)),
#            (LCD.DOWN,   'Down'  , (0,1,0)),
#            (LCD.RIGHT,  'Right' , (1,0,1)) )

# LCD 2 configuration:
lcd2_rs        = 27  # Note this might need to be changed to 21 for older revision Pi's.
lcd2_en        = 22
lcd2_d4        = 25
lcd2_d5        = 24
lcd2_d6        = 23
lcd2_d7        = 18
lcd2_backlight = 4
lcd2_columns = 20
lcd2_rows    = 4

#GPIO variables
s1_led = 26
s2_led = 19
l1_red = 20 #lamp1 off indicator
l1_green = 21 #lamp1 on indicator
l2_red = 12 #lamp2 off indicator
l2_green = 25 #lamp2 on indicator
l1_relay = 5 #relay for lamp1
l2_relay = 6 #relay for lamp2

#set pin modes
control.setmode(control.BCM)
control.setup(s1_led, control.OUT)
control.setup(s2_led, control.OUT)
control.setup(l1_red, control.OUT)
control.setup(l1_green, control.OUT)
control.setup(l2_red, control.OUT)
control.setup(l2_green, control.OUT)
control.setup(l1_relay, control.OUT)
control.setup(l2_relay, control.OUT)

#module variables
sensor = BMP085.BMP085()
#lcd = LCD.Adafruit_CharLCDPlate()
lcd2 = LCD.Adafruit_CharLCD(lcd2_rs, lcd2_en, lcd2_d4, lcd2_d5, lcd2_d6, lcd2_d7, lcd2_columns, lcd2_rows, lcd2_backlight)


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

if os.path.isfile('/sys/bus/w1/devices/28-000008014a4b/w1_slave'):
	s1_fault = 0
	temp1 = '/sys/bus/w1/devices/28-000008014a4b/w1_slave'
else:
        s1_fault = 1
	temp1 = ''


if os.path.isfile('/sys/bus/w1/devices/28-00000801e4f4/w1_slave'):
	temp2 = '/sys/bus/w1/devices/28-00000801e4f4/w1_slave'
	s2_fault = 0
else:
        s2_fault = 1
	temp2 = ''



web = '/var/www/html/monitor/index.cgi'


def read_outside():
        temp = open(temp1)
        text = temp.read()
        temp.close()
        data = text.split("\n")[1].split(" ")[9]
        outside = int(data[2:])
        return outside

def read_house():
        temp = open(temp2)
        text = temp.read()
        temp.close()
        data = text.split("\n")[1].split(" ")[9]
        housetemp = int(data[2:])
        return housetemp

def lamps_off():
        control.output(l1_relay, False)
        control.output(l2_relay, False)
        control.output(l1_green, False)
        control.output(l2_green, False)
        control.output(l1_red, True)
        control.output(l2_red, True)
#        if s1_fault == 1:
#		lcd.set_color(1,1,0)
#		lcd.message("Fault on Sensor1 \n outside")
#	elif s2_fault ==1:
#		lcd.set_color(1,1,0)
#                lcd.message("Fault on Sensor2 \n Doghouse")

#	else:
#		lcd.set_color(1,0,0)
        l1_status = 0
        l2_status = 0

def lamp1_only():
        control.output(l1_relay, True)
        control.output(l2_relay, False)
        control.output(l1_green, True)
        control.output(l2_green, False)
        control.output(l1_red, False)
        control.output(l2_red, True)
#        if s1_fault == 1:
#                lcd.set_color(1,1,0)
#		lcd.message("Fault on Sensor1 \n outside")
#        elif s2_fault ==1:
#                lcd.set_color(1,1,0)
#                lcd.message("Fault on Sensor2 \n Doghouse")

#        else:
#                lcd.set_color(0,1,1)
        l1_status = 1
        l2_status = 0

def both_lamps():
        control.output(l1_relay, True)
        control.output(l2_relay, True)
        control.output(l1_green, True)
        control.output(l2_green, True)
        control.output(l1_red, False)
        control.output(l2_red, False)
#       if s1_fault == 1:
#               lcd.set_color(1,1,0)
#		lcd.message("Fault on Sensor1 \n outside")
#        elif s2_fault ==1:
#                lcd.set_color(1,1,0)
#                lcd.message("Fault on Sensor2 \n Doghouse")

#        else:
#		lcd.set_color(0,0,1)
        l1_status = 1
        l2_status = 1

def sensor_faults():
        if os.path.isfile(temp1):
                s1_fault = 0
        else:
                s1_fault = 1

        if os.path.isfile(temp2):
                s2_fault = 0
        else:
                s2_fault = 1

def curtime():
        time = strftime("%H", localtime())
        return time

def day():
        day = datetime.datetime.today().weekday()
        return day


def main():
        sensor_faults()

        if s1_fault == 1:

	    def range():
            	if dog_house >= 58:
                    lamps_off()
            	if 47 <= dog_house <= 57:
                    lamp1_only()
            	if dog_house <= 46:
                    both_lamps()
            
            hour = int(curtime())
            dow = int(day())

            dog_house = (read_house() / 1000) * 9 / 5 + 32
            my_room = sensor.read_temperature() * 9 / 5 + 32

            lcd2.clear()
            lcd2.message("Inside: %.0fF \nOutside: NULL \nDoghouse: %.0fF" % (my_room,dog_house))
            if dow == 2: #Is wednesday
                    if 6 <= hour <= 21:
                            range()
                    else:
                            lamps_off()
            elif dow == 6: #Is Sunday
                    if 2 <= hour <= 21:
                            range()
                    else:
                            lamps_off()
            else:
                    if on_time <= hour <= off_time:
                            range()
                    else:
                            lamps_off()
    
            time.sleep(900)
                
        elif s2_fault == 1:
            def range():
                if outside >= 58:
                    lamps_off()
                if 47 <= outside <= 57:
                    lamp1_only()
                if outside <= 46:
                    both_lamps()
		

            hour = int(curtime())
            dow = int(day())

            outside = (read_outside() / 1000) * 9 / 5 + 32
            my_room = sensor.read_temperature() * 9 / 5 + 32

            lcd2.clear()
            lcd2.message("Inside: %.0fF \nOutside: %.0fF \nDoghouse: NULL" % (my_room,outside))
            if dow == 2: #Is wednesday
                    if 6 <= hour <= 21:
                            range()
                    else:
                            lamps_off()
            elif dow == 6: #Is Sunday
                    if 2 <= hour <= 21:
                            range()
                    else:
                            lamps_off()
            else:
                    if on_time <= hour <= off_time:
                            range()
                    else:
                            lamps_off()
    
            time.sleep(900)
        else:
            def range():
                if outside >= 58:
                    lamps_off()
                elif dog_house >= 58:
                    lamps_off()
                if 47 <= outside <= 57:
                    lamp1_only()
                if outside <= 46:
                    both_lamps()
                elif dog_house <= 45:
                    both_lamps()    
	    
	    hour = int(curtime())
            dow = int(day())
            outside = (read_outside() / 1000) * 9 / 5 + 32
            dog_house = (read_house() / 1000) * 9 / 5 + 32
            my_room = sensor.read_temperature() * 9 / 5 + 32

            lcd.clear()
            lcd.message("Inside: %.0fF \nOutside: %.0fF \nDoghouse: %.0fF" % (my_room,outside,dog_house))
            
            if dow == 2: #Is wednesday
                    if 6 <= hour <= 21:
                            range()
                    else:
                            lamps_off()
            elif dow == 6: #Is Sunday
                    if 2 <= hour <= 21:
                            range()
                    else:
                            lamps_off()
            else:
                    if on_time <= hour <= off_time:
                            range()
                    else:
                            lamps_off()

            time.sleep(900)

while True:
        main()





