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
off_time = 19

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


#module variables
sensor = BMP085.BMP085()
lcd = LCD.Adafruit_CharLCDPlate()

#Path variables
temp1 = '/sys/bus/w1/devices/28-000008014a4b/w1_slave'
temp2 = '/sys/bus/w1/devices/28-00000801e4f4/w1_slave'
web = '/var/www/html/monitor/index.cgi'

#GPIO variables
s1_led = 26
s2_led = 19
l1_red = 20 #lamp1 off indicator
l1_green = 21 #lamp1 on indicator
l2_red = 12 #lamp2 off indicator
l2_green = 25 #lamp2 on indicator
l1_relay = 5 #relay for lamp1
l2_relay = 6 #relay for lamp2

#global variables
l1_status = 0
l2_status = 0
s1_fault = 0
s2_fault = 0

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
	lcd.set_color(1,0,0)
	l1_status = 0
	l2_status = 0

def lamp1_only():
	control.output(l1_relay, True)
	control.output(l2_relay, False)
	control.output(l1_green, True)
	control.output(l2_green, False)
	control.output(l1_red, False)
	control.output(l2_red, True)
	lcd.set_color(0,1,1)
	l1_status = 1
	l2_status = 0

def both_lamps():
	control.output(l1_relay, True)
	control.output(l2_relay, True)
	control.output(l1_green, True)
	control.output(l2_green, True)
	control.output(l1_red, False)
	control.output(l2_red, False)
	lcd.set_color(0,0,1)
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

	sensor_faults()

	while s1_fault != 0:
		control.output(s1_led, True)
		lcd.set_color(1,1,0)
		os.system("modprobe -r w1-gpio")
		os.system("modprobe -r w1-therm")
		time.sleep(4)
		os.system("modprobe w1-gpio")
		os.system("modprobe w1-therm")

	while s2_fault != 0:
		control.output(s2_led, True)
		lcd.set_color(1,1,0)
		os.system("modprobe -r w1-gpio")
		os.system("modprobe -r w1-therm")
		time.sleep(4)
		os.system("modprobe w1-gpio")
		os.system("modprobe w1-therm")

	hour = int(curtime())
	dow = int(day())
	outside = (read_outside() / 1000) * 9 / 5 + 32
	dog_house = (read_house() / 1000) * 9 / 5 + 32
	my_room = sensor.read_temperature() * 9 / 5 + 32

	lcd.clear()
	lcd.message("In: %.0fF Out: %.0fF \nDog: %.0fF" % (my_room,outside,dog_house))

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

