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
on_time = 11
off_time = 24
lamp1 = False  #water
lamp2 = False  #bed

control.setmode(control.BCM)

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
    url = 'https://api.ambientweather.net/v1/devices?applicationKey=c103229ca2234ebba2ead05db7bd8c163ad2f77758f7497e8f27a9afc74aa3e1&apiKey=f0f5077b6d104b178399c603501b415bf18cb8236315407481d329b9fbf82531'
    response = urllib2.urlopen(url)
    data = response.read()
    outside = json.loads(data)[0]["lastData"]["feelsLike"]
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
#Monday=0
#Tuesday=1
#Wednesday=2
#Thursday=3
#FRiday=4
#Saturday=5
#Sunday=6
    both_lamps()
    time.sleep(900)

while True:
    main()
