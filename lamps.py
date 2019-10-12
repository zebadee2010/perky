#!/usr/bin/env python3
#Updated 10/12/2019

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
import json
import urllib2
from os import path
from time import localtime, strftime

import subprocess

#Global Variables
on_time = 6
off_time = 18
lamp1 = False  #water
lamp2 = False  #bed
web = '/var/www/html/monitor/index.cgi'


#Display GPIO setup
RST = None
L_pin = 27
R_pin = 23
C_pin = 4
U_pin = 17
D_pin = 22

A_pin = 5
B_pin = 6

#Relay GPIO setup
l1_relay = 6 #relay for lamp1
l2_relay = 5 #relay for lamp2
control.setup(l1_relay, control.OUT)
control.setup(l2_relay, control.OUT)

def read_outside():
    url = "http://api.wunderground.com//api/daa1156d61530bfa/conditions/q/pws:KNCELLEN10.json"
    response = urllib2.urlopen(url)
    data = response.read()
    outside = json.loads(data)["current_observation"]["temp_f"]
    return outside

def lamps_off():
    control.output(l1_relay, False)
    control.output(l2_relay, False)
    lamp1 = False
    lamp2 = False

def lamp1_only():
    control.output(l1_relay, True)
    control.output(l2_relay, False)
    lamp1 = True
    lamp2 = False

def lamp2_only():
    control.output(l1_relay, False)
    control.output(l2_relay, True)
    lamp1 = False
    lamp2 = True

def both_lamps():
    control.output(l1_relay, True)
    control.output(l2_relay, True)
    lamp1 = True
    lamp2 = True

def curtime():
    time = strftime("%H", localtime())
    return time

def day():
    day = datetime.datetime.today().weekday()
    return day

def main():
    def range():
        if outside >= 58:
            lamps_off()
        if 47 <= outside <= 57:
            lamp2_only()
        if outside <= 46:
            both_lamps()


    hour = int(curtime())
    dow = int(day())

    outside = read_outside()
    my_room = sensor.read_temperature() * 9 / 5 + 32


    if dow == 2: #Is wednesday
        if 6 <= hour <= 22:
            range()
        else:
            lamps_off()
    elif dow == 6: #Is Sunday
        if 2 <= hour <= 18:
            range()
        else:
            lamps_off()
    elif dow == 4: #Is Friday
        if 2 <= hour <= 24:
            range()
        else:
            lamps_off()
    else:
        if on_time <= hour <= off_time:
            range()
        else:
            lamps_off()

    #Sleep 15 minutes and re-check values
    time.sleep(900)

while True:
    main()
