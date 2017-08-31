#!/usr/bin/env python3

###################################################################
#                          Wiring Info                            #
#   Relay Signal GPIO pins 5,6  -  Orange And Green solid wires   #
#     Relay Ground  -  Orange / white and green / white wires     #
#        Sensor Grounds  -  Green and Green / White wires         #
#         Sensor =5v  -  Orange and Orange / White wires          #
#  Sensor Data  -  Resister =5v and Blue and Blue / White wires   #
###################################################################
import RPi.GPIO as control
import datetime
import time
import os
from os import path
from time import localtime, strftime
#import Adafruit_CharLCD as LCD
import Adafruit_BMP.BMP085 as BMP085
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

on_time = 6
off_time = 20

#Display GPIO setup
RST = None
L_pin = 27
R_pin = 23
C_pin = 4
U_pin = 17
D_pin = 22

A_pin = 5
B_pin = 6

control.setmode(control.BCM)
#control.setup(A_pin, control.IN, pull_up_down=control.PUD_UP) # Input with pull-up
#control.setup(B_pin, control.IN, pull_up_down=control.PUD_UP) # Input with pull-up
#control.setup(L_pin, control.IN, pull_up_down=control.PUD_UP) # Input with pull-up
#control.setup(R_pin, control.IN, pull_up_down=control.PUD_UP) # Input with pull-up
#control.setup(U_pin, control.IN, pull_up_down=control.PUD_UP) # Input with pull-up
#control.setup(D_pin, control.IN, pull_up_down=control.PUD_UP) # Input with pull-up
#control.setup(C_pin, control.IN, pull_up_down=control.PUD_UP) # Input with pull-up

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

#Relay GPIO setup
l1_relay = 5 #relay for lamp1
l2_relay = 6 #relay for lamp2
control.setup(l1_relay, control.OUT)
control.setup(l2_relay, control.OUT)

#Internal Temp Sensor config
control.setmode(control.BCM)
sensor = BMP085.BMP085()


if os.path.isfile('/sys/bus/w1/devices/28-000008014a4b/w1_slave'):
    s1_fault = 0
    temp1 = '/sys/bus/w1/devices/28-000008014a4b/w1_slave'
else:
    s1_fault = 1
    temp1 = ''

if os.path.isfile('/sys/bus/w1/devices/28-00000801e4f4/w1_slave'):
    s2_fault = 0
    temp2 = '/sys/bus/w1/devices/28-00000801e4f4/w1_slave'
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

def display(fault,outside,dog_house,my_room,lamp1,lamp2):
    disp.begin()
    disp.clear()
    disp.display()
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    padding = -2
    top = padding
    bottom = height-padding
    x = 0
    font = ImageFont.load_default()
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True)
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True)
    draw.text((x, top), "IP: " + str(IP), font = font, fill = 255)
    draw.text((x, top+8), str(MemUsage), font = font, fill = 255)
    draw.text((x, top+17), "Outside Temp: " + str(outside) + "F", font = font, fill = 255)
    draw.text((x, top+26), "Doghouse Temp: " + str(dog_house) + "F", font = font, fill = 255)
    draw.text((x, top+35), "Room Temp: " + str(my_room) + "F", font = font, fill = 255)
    draw.text((x, 46), str(fault), font = font, fill = 255)
    if lamp1 == True:
        draw.rectangle((0,64-8,64,64), outline=0, fill=255)   #Lamp1 Only
    elif lamp2 == True:
        draw.rectangle((0,64-8,64,64), outline=0, fill=255)   #Lamp1 Only
    elif lamp1 == True and lamp2 == True:
        draw.rectangle((0,64-8,128,128), outline=0, fill=255)   #Both Lamps ON
    else:
        draw.rectangle((0,64-8,128,128), outline=0, fill=0)   #Both Lamps OFF
    disp.image(image)
    disp.display()
    #draw.rectangle((0,64-8,128,128), outline=0, fill=0)   #Both Lamps OFF


def lamps_off():
    control.output(l1_relay, False)
    control.output(l2_relay, False)
    lamp1 = False
    lamp2 = False

def lamp1_only():
    control.output(l1_relay, True)
    control.output(l2_relay, False)
    draw.rectangle((0,64-8,64,64), outline=0, fill=255)   #Lamp1 Only
    lamp1 = True
    lamp2 = False

def lamp2_only():
    control.output(l1_relay, False)
    control.output(l2_relay, True)
    draw.rectangle((64,64-8,128,128), outline=0, fill=255)   #Lamp2 Only
    lamp1 = False
    lamp2 = True

def both_lamps():
    control.output(l1_relay, True)
    control.output(l2_relay, True)
    draw.rectangle((0,64-8,128,128), outline=0, fill=255)   #Both Lamps ON
    lamp1 = True
    lamp2 = True

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
    elif s2_fault == 1:
        def range():
            if outside >= 58:
                lamps_off()
            if 47 <= outside <= 57:
                lamp1_only()
            if outside <= 46:
                both_lamps()
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

    if s1_fault == 1:
        fault = 'Outside Sensor Fault'
        dog_house = (read_house() / 1000) * 9 / 5 + 32
        my_room = sensor.read_temperature() * 9 / 5 + 32
        outside = 'NULL'
    elif s2_fault == 1:
        fault = 'Doghouse Sensor Fault'
        outside = (read_outside() / 1000) * 9 / 5 + 32
        my_room = sensor.read_temperature() * 9 / 5 + 32
        dog_house = 'NULL'
    elif s1_fault == 1 and s2_fault == 1:
        fault = 'SENSOR MAJOR FAULT'
        outside = 'NULL'
        dog_house = 'NULL'
    else:
        outside = (read_outside() / 1000) * 9 / 5 + 32
        dog_house = (read_house() / 1000) * 9 / 5 + 32
        my_room = sensor.read_temperature() * 9 / 5 + 32


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
    display(fault,outside,dog_house,my_room,lamp1,lamp2)

    time.sleep(900)

while True:
        main()
