import RPi.GPIO as control
import datetime
import time
import os
from os import path
from time import localtime, strftime
import Adafruit_CharLCD as LCD
import Adafruit_BMP.BMP085 as BMP085
import configparser

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#Define variables
sensor = BMP085.BMP085()
lcd = LCD.Adafruit_CharLCDPlate()
config = configparser.ConfigParser()
temp1 = '/sys/bus/w1/devices/28-000008014a4b/w1_slave'  #outside temp
temp2 = '/sys/bus/w1/devices/28-00000801e4f4/w1_slave'  #doghouse temp
s1_fault = 26 #sensor1_fault unable to read
s2_fault = 19 #sensor2_fault unable to read
l1_off = 20 #lamp1 off indicator
l1_on = 21 #lamp1 on indicator
l2_off = 12 #lamp2 off indicator
l2_on = 25 #lamp2 on indicator
r1 = 5 #relay for lamp1
r2 = 6 #relay for lamp2

#set pin modes
control.setmode(control.BCM)
control.setup(s1_fault, control.OUT)
control.setup(s2_fault, control.OUT)
control.setup(l1_off, control.OUT)
control.setup(l1_on, control.OUT)
control.setup(l2_off, control.OUT)
control.setup(l2_on, control.OUT)
control.setup(r1, control.OUT)
control.setup(r2, control.OUT)

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
	control.output(r1, False)
	control.output(r2, False)
	control.output(l1_on, False)
	control.output(l2_on, False)
	control.output(l1_off, True)
	control.output(l2_off, True)
	lcd.set_color(1,0,1)
	f=open('lamps_var.py', 'w')
	f.write("lamp1 = 0\n")
	f.write("lamp2 = 0\n")
	f.close()

def lamp1_only():
	control.output(r1, True)
	control.output(r2, False)
	control.output(l1_on, True)
	control.output(l2_on, False)
	control.output(l1_off, False)
	control.output(l2_off, True)
	lcd.set_color(0,1,1)
	f=open('lamps_var.py', 'w')
	f.write("lamp1 = 1\n")
	f.write("lamp2 = 0\n")
	f.close()

def both_lamps():
	control.output(r1, True)
	control.output(r2, True)
	control.output(l1_on, True)
	control.output(l2_on, True)
	control.output(l1_off, False)
	control.output(l2_off, False)
	lcd.set_color(0,0,1)
	f=open('lamps_var.py', 'w')
	f.write("lamp1 = 1\n")
	f.write("lamp2 = 1\n")
	f.close()

def sensor_faults():
	if os.path.isfile(temp1):
		s1f = 0
	else:
		s1f = 1

	if os.path.isfile(temp2):
		s2f = 0
	else:
		s2f = 1
	
	f=open('fault.py', 'w')
	f.write("s1_fault = %.0f\n" % s1f)
	f.write("s2_fault = %.0f\n" % s2f)
	f.close()

	if s1f == 1:
		control.output(s1_fault, True)
		lcd.set_color(1,1,0)
		os.system("modprobe -r w1-gpio")
		os.system("modprobe -r w1-therm")
		time.sleep(4)
		os.system("modprobe w1-gpio")
		os.system("modprobe w1-therm")
	
	if s2f == 1:
		control.output(s2_fault, True)
		lcd.set_color(1,1,0)
		os.system("modprobe -r w1-gpio")
		os.system("modprobe -r w1-therm")
		time.sleep(4)
		os.system("modprobe w1-gpio")
		os.system("modprobe w1-therm")

def curtime():
	time = strftime("%H", localtime())
	return time

def main_function():
	out = (read_outside() / 1000) * 9 / 5 + 32
	dog = (read_house() / 1000) * 9 / 5 + 32
	inside = sensor.read_temperature() * 9 / 5 + 32
	lcd.clear()
	lcd.message("In: %.0fF Out: %.0fF \nDog: %.0fF" % (inside,out,dog))
	if read_outside() >= 18500:   #Above 60 lamps off
		lamps_off()
	elif read_house() >= 16500:
		lamps_off()
	if 5000 <= read_outside() <= 15000:  #Between 45 and 59 outside
		lamp1_only()
	elif 10000 <= read_house() <= 15000:  #Between 50 and  59 in the doghouse
		lamp1_only()
	if read_outside() <= 5000:      #Below 45 outside
		both_lamps()
	elif read_house() <= 10000:     #Below 50 in the doghouse
		both_lamps()
	time.sleep(1800)

day_of_week = datetime.datetime.today().weekday()
out = (read_outside() / 1000) * 9 / 5 + 32
dog = (read_house() / 1000) * 9 / 5 + 32
f=open('temp_var.py', 'w+')
f.write('dog_house_temp = %.0f \n' % dog)
f.write('outside_temp = %.0f \n' % out)
f.close()
lamp1_only()
sensor_faults()
